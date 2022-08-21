from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
from tensorflow.keras.models import load_model
from src.predict import preprocess, predict, preprocess_batch
import os

app = FastAPI()

# Add CORS middleware to allow access from other domains.
# This is required for the frontend to access the API. Not implimented here.
origins = ["*"]
methods = ["*"]
headers = ["*"]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=methods, allow_headers=headers
)

version = 1
path = Path.cwd()
# Running from scripts directory
if path.name == "scripts":
    model_path = path.parent.joinpath("models", "mnist_convnet", str(version))
# Running from root directory (if niether than will cause error)
else:
    model_path = Path.cwd().joinpath("models", "mnist_convnet", str(version))
# Load the model once at the start of the server
model = load_model(model_path)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/predict/batch")
async def predict_array(images: list):
    # Process batch of images
    image = preprocess_batch(images)
    # predict class
    pred = predict(model=model, image=image)

    return {"y": str(pred)}


@app.post("/predict/img")
async def predict_image(image_link: str = ""):
    """Predicts single image class from file upload

    Args:
        file (bytes, optional): Upload a image file. Defaults to File(...).

    Returns:
        pred (JSON): JSON object with predicted class and probability
    """
    if image_link == "":
        raise HTTPException(status_code=400, detail="No image link provided")
    # read image and process
    try:
        image = preprocess(image_link)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # predict class
    pred = predict(model=model, image=image)
    # return prediction
    return {"y": str(pred[0])}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
