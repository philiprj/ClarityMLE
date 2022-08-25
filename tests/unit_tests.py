"""Module performs unit testing of the API including:

    - Latencty when making repeat calls
    - Scaling of the number of instances
    - Asserting correct errors

"""
import json
import numpy as np
import time
from pathlib import Path
import pytest
import asyncio
from httpx import AsyncClient

# Load test data
data_path = Path.cwd().parent.joinpath("data")
with np.load(data_path.joinpath("mnist_test.npz"), allow_pickle=True) as f:
    x_test, y_test = f["x"], f["y"]

with np.load(data_path.joinpath("cifar_test.npz"), allow_pickle=True) as f:
    x_cifar, y_cifar = f["x"], f["y"]

# Deployed endpoint
url = "http://clarityapi-env-1.eba-289rmxee.eu-west-1.elasticbeanstalk.com"
# Local endpoint
# url = "http://0.0.0.0:8080"


@pytest.mark.asyncio
async def test_root():
    """Test the root endpoint returns a 200"""
    async with AsyncClient(base_url=url) as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


@pytest.mark.asyncio
async def test_404():
    """Test error code if endpoint not found"""
    async with AsyncClient(base_url=url) as client:
        response = await client.get("/non_existent_endpoint")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_prediction():
    """Test prediction latenct, accuracy, repsonde code for healthy inputs"""
    # Take the first 500 test examples and convert to json
    x, y = x_test[0:100].tolist(), y_test[0:100].tolist()
    data = json.dumps({"x": x})
    headers = {"accept": "application/json", "content-type": "application/json"}
    # Asyncronously make the request to the API
    async with AsyncClient(base_url=url) as client:
        # Time latency for making 5 predictions in batches of 100
        start = time.time()
        response = await asyncio.gather(
            client.post("predict/batch", content=data, headers=headers),
            client.post("predict/batch", content=data, headers=headers),
            client.post("predict/batch", content=data, headers=headers),
            client.post("predict/batch", content=data, headers=headers),
            client.post("predict/batch", content=data, headers=headers),
        )
        end = time.time()
    # Take the first response (should all be the same)
    response = response[0]
    latency = end - start
    # Assert the response code is 200
    assert response.status_code == 200
    # Assert the latency is less than 4 seconds
    assert latency < 4.0
    predictions = json.loads(response.text)["y"]
    accuracy = sum(p == t for p, t in zip(predictions, y)) / len(y)
    # Assert the test accuracy is greater than 0.95
    assert accuracy > 0.95


@pytest.mark.asyncio
async def test_break_prediction():
    """tests unhealthy inputs return appropratie errors"""
    headers = {"accept": "application/json", "content-type": "application/json"}

    # Check correct error if images passed with incorrect tag.
    z = x_test[0:100].tolist()
    data1 = json.dumps({"z": z})
    # Check the model can handel singular images
    x, y = x_test[0].tolist(), y_test[0].tolist()
    data2 = json.dumps({"x": x})
    # Check the model can handel colour images (no correct prediction)
    x_c = x_cifar[0].tolist()
    data3 = json.dumps({"x": x_c})
    # Check no image predictions
    x_odd = [[0, 1, 2], [3, 4]]
    data4 = json.dumps({"x": x_odd})
    # Check no image predictions
    data5 = json.dumps({"x": []})

    async with AsyncClient(base_url=url) as client:
        response1 = await client.post("predict/batch", content=data1, headers=headers)
        response2 = await client.post("predict/batch", content=data2, headers=headers)
        response3 = await client.post("predict/batch", content=data3, headers=headers)
        response4 = await client.post("predict/batch", content=data4, headers=headers)
        response5 = await client.post("predict/batch", content=data5, headers=headers)

    # Assert 400 when incorrect tag is passed
    assert response1.status_code == 400
    # Check no error if single image passed
    assert response2.status_code == 200
    pred = json.loads(response2.text)["y"]
    # Assumed the prediction is correct
    assert pred[0] == y
    # This test if the image pre-processing is working, but will return nonsense predictions.
    assert response3.status_code == 200
    # Assert 400 error when image is not square
    assert response4.status_code == 400
    # Assert 400 when no images are passed
    assert response5.status_code == 400
