import requests
import json
import numpy as np
import time
from pathlib import Path
import argparse

# Load test data
data_path = Path.cwd().parent.joinpath("data")
with np.load(data_path.joinpath("mnist_test.npz"), allow_pickle=True) as f:
    x_test, y_test = f["x"], f["y"]

x_test = np.expand_dims(x_test, -1)
# normalize pixel values
x_test = x_test.astype("float32") / 255.0

url = "http://0.0.0.0:8080/predict/batch"


def make_prediction(instances):
    data = json.dumps({"x": instances.tolist()})
    headers = {"accept": "application/json", "content-type": "application/json"}
    json_response = requests.post(url, data=data, headers=headers)
    if json_response.status_code == 200:
        predictions = json.loads(json_response.text)["y"]
    else:
        raise Exception("Error: {}".format(json_response.status_code))
    return predictions


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--num_instances",
        type=int,
        help="Number of instances to predict",
        required=False,
        default=250,
    )
    args = parser.parse_args()
    i = args.num_instances
    # Get a slice of the test data
    x, y = x_test[0:i], y_test[0:i].tolist()
    # Make predictions and report time
    start = time.time()
    predictions = make_prediction(x)
    end = time.time()
    # Return the time and accuracy
    print("Time: {:.4f}s".format(end - start))
    accuracy = sum(p == t for p, t in zip(predictions, y)) / len(y)
    print("Accuracy: {:.2f}%".format(accuracy * 100))

    # print("Prediction: {}".format(predictions))
    # print("Labels: {}".format(y))
