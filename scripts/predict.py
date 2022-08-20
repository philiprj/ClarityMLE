from fastapi import FastAPI
from requests import request
from random import randint
import json

app = FastAPI()

model = lambda x: randint(0, 9)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.route("/predict", methods=["POST"])
def predict():
    X = request.get_json()["X"]
    y = model(X)
    return json.dumps({"y": y}), 200
