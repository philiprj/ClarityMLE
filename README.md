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
- [ ] Model compression
- [ ] Cloud deployment 
- [ ] Containerisation
- [ ] Data Distribution Shifts
- [ ] Model registry (mlFlow)
- [ ] Continual learning

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
