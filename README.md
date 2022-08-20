# ClarityMLE
Clarity AI Machine Learning Engineering Test


## Purpose 
- [ ] How you take the business context into account
- [ ] What approaches you considered and why you chose the final one in particular
- [ ] Technical proficiency and best practices
- [ ] What you would do differently if you had more time

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

## Plan

- [ ] Create prediction API
- [ ] Batch prediction vs online prediction
- [ ] Auto scalling and load balancing
- [ ] Model performance monitoring and engineering metrics
- [ ] Model compression - consider Quantisation of model, e.g. using half-precision (16-bit) or fixed-point (8-bit ints) to represent model paramters. This should reduce computation and memory footprint, but may drop accuracy too much. 
- [ ] Cloud deployment - Consider using AWS for deployment. 
- [ ] Containerisation - Docker container 
- [ ] Data Distribution Shifts
- [ ] Model registry (mlFlow)
- [ ] Continual learning

## Considerations out of scope

* Test in production - Shadow Testing, A/B Testing, Canary Release, Bandits
* Pre model development stages of ML lifecycle - Data Engineering, Training Data, Feature Engineering, Model Development and Testing
* Human-in-the-loop feedback. For low probability predictions we may want to include human feedback/labels. Interesting video of the topic of how poorly written addresses are handled [here](https://www.youtube.com/watch?v=XxCha4Kez9c).
* Batch features - The only features for this app come streaming from the request. More complex model applications may use a combination of streaming and batch features. Batch features may be stored in data warehouses, for example we may store the median food preperation time for a restaurant when predicting the estimated delivery time for a food delivery app. 
* 

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

## Run FastAPI
