# ClarityMLE
Clarity AI Machine Learning Engineering Test

## Purpose 
* How you take the business context into account
* What approaches you considered and why you chose the final one in particular
* Technical proficiency and best practices
* What you would do differently if you had more time

## The Task
One of the data scientists in the team hands you a model in the form of a notebook and asks you to deploy it in production. It is a model that can recognise handwritten digits.

Example use case: 
* Postal service looking to recognise numerical postal codes
* Online prediction, with up to 100 request per second
* Must have latency less the couple of seconds
* Could be variable load, e.g. multiple postal trucks arriving at once
* No existing baseline model in production 
* Assume given model is the best model delevoped 

Utilise machine learning and engineering skills to design a suitable architecture and develop deployable code to run model training and inference. Part, if not all, of your solution should be written in Python, as this is the language in which the model has been developed. Your design should take into consideration how the model will be used in practice.

### Service Level Objectives (SLOs)

- [ ] 99.99% uptime
- [ ] 500 predictions within 2s
- [ ] Dashboard to show the relevent engineering metrics and model observability

## Plan

- [X] Create prediction API using FastAPI. (alternatives such as TensorFlow and PyTorch Serving could acheive a similar effect).
- [X] Containerisation - Docker container for the prediction API.
- [X] Batching online prediction for performance. Can batch list inputs, currently no batch endpoint for raw image files. 
- [ ] Model registry (mlFlow).
- [ ] Cloud deployment - AWS for deployment using EC2 instance. In future could test hardware acceleration such as GPUs and AWS Inferentia.
- [ ] Auto scalling and load balancing.
- [ ] Application Monitoring - metrics, logs, tracing (API latency, log errors, service health metrics).
- [ ] Model Observability - prediction distribtion (compared to training distribution), data quality. A model card with the key model metrics and details can be seen in the docs directory.  

## Considerations out of scope

* Test in production - Shadow Testing, A/B Testing, Canary Release, Bandits.
* Pre model development stages of ML lifecycle - Data Engineering, Training Data, Feature Engineering, Model Development and Testing.
* Model compression - consider Quantisation of model, e.g. using half-precision (16-bit) or fixed-point (8-bit ints) to represent model paramters. This should reduce computation and memory footprint, but may drop accuracy too much. 
* Continual learning - in a productuon system we would store new incoming data in a datalake, alongside logs, predictions, and application data, which we could use for further training.
* Human-in-the-loop feedback. For low probability predictions we may want to include human feedback/labels. Interesting video of the topic of how poorly written addresses are handled [here](https://www.youtube.com/watch?v=XxCha4Kez9c). We may also want to include a group of human labelers to further create a larger, more diverse, training set for future model improvements.  
* Batch features - The only features for this app come streaming from the request. More complex model applications may use a combination of streaming and batch features. Batch features may be stored in data warehouses, for example we may store the median food preperation time for a restaurant when predicting the estimated delivery time for a food delivery app. 
* Edge Serving - to decrease latency we may deploy the model on and edge device to the postal sorting office, which will decrease time taken to transfer data to an off-prem cloud server. New models could be trained off-line and stored in the model registry, and peridocially pushed to edge devices. Edge serving comes with benifits in latency, efficient network usage, privacy and security, reliability. But they may have less compute/memory for larger models, so quantization may be key for success.
* Data Distributional Shifts - the training data has a roughly equal class distribtuion, but this may not be the same as the class distribution in production, e.g. we may expect far may 0s than 9s. Further the input format of the training images is very consistant, e.g. white digits on a clean black background vertically alligned at 28 x 28 scale. In real life the images may on a different scale, coloured, or not vetically alligned. This requires processing the image into the correct format which may look quite different to the training data. This could be as simple as having white writing on a dark background, something not encountered in training.  
* Data Monitoring - linking to the above, we want to automate input data monitoring for features like, freshness, volume, distribution, model fairness.
* Explainability - Given the nature of the taks (predicting zip codes), prediction explainability is not a major concern. We could evaluate the model using [SHAP](https://github.com/slundberg/shap) to understand which pixel are most important to a models prediction. 
* Business Impact Metrics - The (assumed) end goal of the project is to reduce the overal cost and time taken to deliver post. This sub-project of classifying digits of zip codes, pressumably at a sorting office, should therefore aim to sort post quickly. Accuracy is vital as misdircted post could drastically increase the expected delivery time and associated cost. In order to validate the benifit we must compare this process to the baseline (e.g. human sorting). If any accuracy is lost in changing to the ML model, we must factor in the time and cost to correct mistakes into our evaluation.  

## Setup

To create a new environment with Python version 3.9:
```bash
conda create -n <env_name> python=3.9 
```

We can then activate this environment:
```bash
conda activate <env_name>
```

And install all relevent requirements:
```bash
pip install -r requirements.txt
```

## Containerise with Docker

To containerise the application with Docker run the below from the root directory:

```bash
docker build -t <image_name> .
```

```bash
docker run -p 8080:8080 -d <image_name>
```

Then visit http://0.0.0.0:8080/docs to see the interactive Swagger UI for the prediction API. Here you can test the prediction by linking to you own images. For example using the URL [here](https://camo.githubusercontent.com/3d9666a8f0c5658667292b74ca19295827c2b22a0e903db283998ae213e6f6e1/68747470733a2f2f646174616d61646e6573732e6769746875622e696f2f6173736574732f696d616765732f74665f66696c655f666565642f4d4e4953545f64696769742e706e67).

A library of MNIST .jpg images can be found on [Kaggle](https://www.kaggle.com/datasets/scolianni/mnistasjpg).

## Testing

* Functional Testing -- assert expected output for given inputs.
* Statistical - test API on unseen request, and check prediction distribtuion against trining prediction distribution.
* Error handling - how do we handle bad inputs.
* Load testing - test API with x inputs over y seconds
* End-to-end - validate all subsystems are working as expected. 

We can perform basic API testing using the api_test.py script in the test directory. Whilst running the docker container on port 8080, from the root directory:

```bash
cd tests
python3 api_test.py -n 500
```

This will call the API with a batch of 500 test set examples, the expected return will look something like the below:

```
Time: 1.4840s
Accuracy: 99.60%
Prediction distribution: OrderedDict([(0, 43), (1, 67), (2, 54), (3, 45), (4, 55), (5, 50), (6, 42), (7, 50), (8, 40), (9, 54)])
```

Using the -p True flag we can also return a plot of the prediction distribution.

```bash
python3 api_test.py -n 500 -p True
```

<img src="docs/media/histogram.png" alt="Prediction histogram" width="400"/>



