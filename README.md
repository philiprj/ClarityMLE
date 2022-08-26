# ClarityMLE
Clarity AI Machine Learning Engineering Test

## Purpose 
* How you take the business context into account
* What approaches did you consider and why did you choose the final one in particular
* Technical proficiency and best practices
* What you would do differently if you had more time

## The Task
One of the data scientists in the team hands you a model in the form of a notebook and asks you to deploy it in production. It is a model that can recognise handwritten digits.

Example use case: 
* Postal service looking to recognise numerical postal codes
* Online prediction, with up to 100 requests per second
* Must have latency of less the couple of seconds
* Could be a variable load, e.g. multiple postal trucks arriving at once
* No existing baseline model in production 
* Assume the given model is the best model developed 

Utilise machine learning and engineering skills to design a suitable architecture and develop deployable code to run model training and inference. Part, if not all, of your solution, should be written in Python, as this is the language in which the model has been developed. Your design should take into consideration how the model will be used in practice.
### Service Level Objectives (SLOs)

- [X] 99.99% uptime - tested over 24 hours (no downtime).
- [X] 500 predictions within 4s (tested in unit_test.py with 5 asynchronous calls of 100 images).
- [X] > 95% accuracy on unseen test images.
- [X] Dashboard to show the relevant engineering metrics and model observability (AWS CloudWatch).

## Plan

The plan for this solution involves creating an online inference REST API which takes JSON input holding a list of images, with features represented as floats in a list. This enables us to batch together predictions for more efficient inference. In a real-world deployment, and given more time here, we would have to consider how these online inputs would be dynamically batched using a data streaming solution, such as AWS Kinesis, TorchServe, or Apache Kafka/Flink. This would aggregate inputs over a defined window (either time or input count), and then batch them for inference. When inputs are passed to the endpoint, they are passed to a preprocessing helper function, which can convert differently sized images or colour images, to the appropriate format. It ensures the tensor shape is correct in the model and normalises the data in the range [0,1]as done in training. A second endpoint has also been set up that enables users to input a public URL to an image and have the model predict the digit. This has not been the primary focus of the project but enables users to test out individual images for fun/debugging.  

The inference endpoint will then be hosted on AWS (Azure/GCP also viable, I just have more experience with AWS), using Elastic Beanstalk to manage infrastructure deployment. We could set up compute and autoscaling/load balancing manually with more fine-grained control but this would require far more setup time. Kubernetes-based solutions were also considered but deemed overkill for the scale of the project. AWS Sagemaker also offers managed host solutions - had model development been performed with Sagemaker, I would have been included to use this solution. Application monitoring and alerts can be easily managed through Elastic Beanstalk Health and Monitoring dashboards. Given more time we would set up alerts if the unusual activity, loads, or slow latency times were detected. Logs can also be extracted from the Elastic Beanstalk Logs tab, although these are automatically generated through the Uvicorn service. Given more time we would most likely want to set up custom logging for specific events of interest. Once deployed with have implemented a set of tests for the hosted endpoint to ensure it meets our SLOs.

Additional elements outside the scope of the plan are discussed in the 'Considerations out of scope' section.

The detailed plan can be seen below:

- [X] Create inference API using FastAPI. (alternatives such as Flask, TensorFlow and PyTorch Serving could achieve a similar effect). Why an API? By creating a standalone inference microservice, the model can be integrated with several apps which can call the API a black box, rather than worry about what is going on under the hood. 
- [X] Containerisation - Docker container for the prediction API.
- [X] Batching online prediction for performance. Can batch list inputs, currently no batch endpoint for raw image files. 
- [X] Cloud deployment - AWS for deployment using Elastic Beanstalk with EC2 instances. In future could test hardware acceleration such as GPUs and AWS Inferentia. With more time, we would set up a data streaming solution (AWS Kinesis or Apache Kafka) and a real-time analytics service (Apache Flink) to manage the auto-scaling in response to traffic patterns. "Serverless" solutions such as AWS Lambda were considered but given the business context would expect some consistent level of traffic, it was deemed unsuitable. Kubernetes-based solutions were also considered, using EKS/ECS, but due to the smaller scale and cost considerations of the project, these were not pursued. 
- [X] Auto scaling and load balancing - Our Elastic Beanstalk service creates an Auto Scaling Group and Elastic Load Balancer to route traffic to the EC2 instances running our endpoints. 
- [X] Application Monitoring - metrics, logs, tracing (API latency, log errors, service health metrics).
- [X] Model Observability - prediction distribution (compared to training distribution), data quality. A model card with the key model metrics and details can be seen in the docs directory.  
- [X] IaC - As far as possible follow engineering best practices by defining infrastructure as code. Define bash scripts to build and push Docker Images, Deploy Infrastructure using Elastic Beanstalk script. Create automated unit tests using pytest that tests if the endpoint achieves the objectives and how it behaves with unexpected inputs. Ideally, we would automate to ensure these tests are run on any new endpoint before it replaces an existing production version.
- [X] Testing - To ensure the model is meating the project objectives, engineering and data science objectives, we have implimented a set of tests using pytest in the test directory. This should comfirm the hosted model is acheiving the latency and performance requirements, and handles errors gracefully.  

## Considerations out of scope

* **Test in production** - Shadow Testing, A/B Testing, Canary Release, Bandits. If we had existing models in production, we would want to test our new model to understand how it compares to the existing production models. For example by gradually routing more traffic to the model if production evaluation shows it is outperforming the other models (A/B testing).
 
* **Pre-production stages of ML lifecycle** - Data Engineering, Training Data, Feature Engineering, Model Development and Testing.
  * Data Engineering: Ideally we would store the data gathered by the live application, and the already gathered training data in a data lake. We would set up a data engineering pipeline to transform the raw image data into the image format used by the model. We could perfrom this jobs in batch using a pre-defined enginerring pipeline, schedular, orchastrastor (e.g. using Sagemaker Pipelines, Kedro, Airflow, Argo, MetaFlow). These same pipelines can also be used to kick-off a model training job. 
  * Training Data: Generally we would like to use as much data as possible for training, and testing the model on 'fresh' data that would be ingested by the live model. Because we have little data at this point, sampling methods are not of great importance. When training our models, we do want to keep track of the data lineage, to tell us what data we used to train the model. This can be integrated into Experiment Tracking and Model Registries (e.g. using mlFlow or Sagemaker Experiments). In future, I would expect to consider methods such as data augmentation, to increase the training set size, whilst retaining accurate labels, using image transformation like rotations, cropping, inverting, etc. We may also utilise Data Synthesis, using high-confidence model predictions to label images, using these for training new models. Similarly, GANs can be used to generate more training data when it is hard to come by.  
  * Feature Engineering: There is little feature engineering required for the images. The core components are image resizing to achieve the 28 x 28 scale the model expects, converting to greyscale (28 x 28 x 3 -> 28 x 28 x 1), and normalising the values in the range of [0,1]. These are relatively cheap operations so can be done in real-time. There are a couple of approaches to resizing and converting to greyscale, so in the future, I would expect to try each of these approaches to see how they affect performance.       
  * Model Development and Testing: To further validate the model performance, we may want to compare the simple CNN trained here to other more complex models, such as ensembles, or simpler baselines. We would want to evaluate these based on test accuracy and latency. Experiment tracking is important when comparing models. We may want to track: training and validation loss curves, performance metrics like accuracy, logs of predictions vs ground truth labels (check if specific classes are cuaing issues), inference speed, memory and CPU/GPU utilisation, and hyperparameters. These can be tracked by tools such as Sagemaker experiments or mlFlow. Model versioning is also important with tools such as mlFlow and Sagemaker offering solutions. With larger models, we may have to consider distributed training (model or data parallelism), but given the simplicity of the task and latency constraints, this is unlikely to affect this project. We may want to train our CNN models using GPUs to speed up training. This can be done easily using cloud providers like AWS. We would also want to complete an more exhaustive hyperparameter search in order to find the best configuration for our model. This could be done using a simple grid-search or Bayesian Optimisation using Tensoflow's Keras Tuner.  

* **Model compression** - consider Quantisation of model, e.g. using half-precision (16-bit) or fixed-point (8-bit ints) to represent model parameters. This should reduce computation and memory footprint, but may drop accuracy too much. 

* **Continual learning** - in a production system we would store new incoming data in a datalake, alongside logs, predictions, and application data, which we could use for further training.

* **Human-in-the-loop feedback** - For low probability predictions, we may want to include human feedback/labels. Interesting video on the topic of how poorly written addresses are handled [here](https://www.youtube.com/watch?v=XxCha4Kez9c). We may also want to include a group of human labellers to further create a larger, more diverse, training set for future model improvements.  

* **Batch features** - The only features for this app come streaming from the request. More complex model applications may use a combination of streaming and batch features. Batch features may be stored in data warehouses, for example, we may store the median food preparation time for a restaurant when predicting the estimated delivery time for a food delivery app. 

* **Edge Serving** - to decrease latency we may deploy the model on an edge device to the postal sorting office, which will decrease the time taken to transfer data to an off-prem cloud server. New models could be trained offline and stored in the model registry, and periodically pushed to edge devices. Edge serving comes with benefits in latency, efficient network usage, privacy and security, and reliability. But they may have less compute/memory for larger models, so quantization may be key for success.

* **Data Distributional Shifts** - the training data has a roughly equal class distribution, but this may not be the same as the class distribution in production, e.g. we may expect far may 0s than 9s. Further, the input format of the training images is very consistent, e.g. white digits on a clean black background vertically aligned at a 28 x 28 scale. In real life the images may on a different scale, coloured, or not vertically aligned. This requires processing the image into the correct format which may look quite different to the training data. The difference could be as simple as having white writing on a dark background, something not encountered in training, but we would expect significantly worse performance if this were the case.  

* **Data Monitoring** - linking to the above, we want to automate input data monitoring for features like freshness, volume, distribution, and model fairness.

* **Explainability** - Given the nature of the task (predicting zip codes), prediction explainability is not a major concern. We could evaluate the model using [SHAP](https://github.com/slundberg/shap) to understand which pixels are most important to a model's prediction. 

* **Business Impact Metrics** - The (assumed) end goal of the project is to reduce the overall cost and time taken to deliver the post. This sub-project of classifying digits of zip codes, presumably at a sorting office, should therefore aim to sort posts quickly. Accuracy is vital as the misdirected post could drastically increase the expected delivery time and associated costs. To validate the benefit we must compare this process to the baseline (e.g. human sorting). If any accuracy is lost in changing to the ML model, we must factor in the time and cost to correct mistakes in our evaluation.  

## Setup

If you would like to run the code in this repository firstly you need to create a new environment with Python version 3.9 and install the necessary dependencies. If using Conda to manage your environment this can be achieved using the below commands from the root of the repo:
```bash
conda create -n <env_name> python=3.9 
conda activate <env_name>
pip install -r requirements.txt
```

To deploy to AWS with the instructions here, please make sure you have an AWS account and have the AWS CLI installed (instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-prereqs.html)). Then ensure your default credentials are configured, by running:

```bash 
aws configure
``` 

Or directly accessing your '.aws/credentials' file and providing the following details:

```bash
[default]
aws_access_key_id = <YOUR_AWS_ACCESS_KEY_ID>
aws_secret_access_key = <YOUR_SECRET_ACCESS_KEY>
region = <DEFAULT-REGION>
```

You will also need a Docker installed on your decive (instructions [here](https://docs.docker.com/get-docker/)).

## Containerise with Docker

If you would like to containerise the application to run locally run the below from the root directory:

```bash
docker build -t <image_name> .
docker run -p 80:80 -d <image_name>
```

Then visit http://0.0.0.0:80/docs to see the interactive Swagger UI for the prediction API. The Swagger UI contains the API documentation, including expected inputs, outputs, and error messages.

Here you can test the prediction by linking to your own images. For example using the URL [here](https://camo.githubusercontent.com/3d9666a8f0c5658667292b74ca19295827c2b22a0e903db283998ae213e6f6e1/68747470733a2f2f646174616d61646e6573732e6769746875622e696f2f6173736574732f696d616765732f74665f66696c655f666565642f4d4e4953545f64696769742e706e67).

A library of MNIST .jpg images can be found on [Kaggle](https://www.kaggle.com/datasets/scolianni/mnistasjpg).

## Deploy to AWS

To deploy our API to make it available to the client, first push the container to AWS [Elastic Container Registry](https://aws.amazon.com/ecr/) (ECR). To do this we have added a bash script to build the docker image and push it to your default AWS account. This will create a repository called 'clarity-api'. To run the script run the below command from the root directory:

```bash
sh aws/build_push.sh
```

When we make changes to our source repo, we can run this script again to push the latest version of our app to the registry. With a CloudFormation or Terraform script, we could automatically redeploy our infrastructure with the latest version. This is a key component of the standard CI/CD pipeline. Ideally, given more time, we would implement more complete unit tests and model performance-based testing which would need to be passed before any existing app was updated with the latest version. 

To provision the infrastructure using AWS Elastic Beanstalk we may use the console of AWS CLI. 

### Option: 1 Console

First, create an S3 bucket to upload the Dockerrun.aws.json file (you may also need to edit this file with your appropriate image URI). You can do this using the AWS CLI using the below command from the AWS directory (replacing <your_s3_bucket_name> with desired bucket name):

```bash
aws s3 mb "s3://<s3_bucket_name>"
aws s3 cp "Dockerrun.aws.json" "s3://<s3_bucket_name>/Dockerrun.aws.json"
```

You can then create an Elastic Beanstalk deployment through the AWS Console using the Docker Platform and source code origin point to the S3 bucket created, as shown in the figure below.

<p align="center">
    <img src="docs/media/elb.png" alt="Elastic Beanstalk setup" width="450"/>
</p>

### Option 2: AWS and EB CLI

Alternatively, we can use the AWS EB CLI to provision our infrastructure. The installation process for the EB CLI can be found [here](https://github.com/aws/aws-elastic-beanstalk-cli-setup).

Once installed, move to the AWS directory and run the below with an appropriate name, e.g clarity-api:

```bash
eb init <application_name> --platform Docker
```

Then we can create an environment with an appropriate configuration. The first option below creates a simple environment with a single t2.mirco instance. The second option creates an environment with an Auto Scaling Group, Load Balancer, and Spot Instances to better scale with increased traffic and reduces costs through the use of Spot Instances rather than on-demand. 

Simple deployment with a single instance:
```bash
eb create <env_name> --single --instance-type "t2.micro"
```

Advanced deployment with Auto Scaling, Load Balancer, and Spot Instances:
```bash
eb create <env_name> --elb-type classic --enable-spot --instance-types "t2.micro,t2.small" --min-instances 1 --max-instances 2
```

Once completed we are now able to call the image or batch prediction endpoint by following the link provided. The URL should be:

```
URL = http://<env_name>.eba-289rmxee.eu-west-1.elasticbeanstalk.com
```

With the batch prediction having the '/prediction/batch' route. 

I have left the advanced endpoint live, and will keep it live until **01/09/22**. This API can be reached at:

```
URL = http://clarity-api-advanced.eba-289rmxee.eu-west-1.elasticbeanstalk.com/
```

The batch prediction endpoint has a limit of around 100 predictions per call due to the data transfer limit. If testing the image endpoint ("/predict/img" for jpg/png), please ensure the image URL provided is public. 

## Testing

To assess the production endpoint we have created a set of tests for the endpoint. Machine learning tests can be broadly categorised into the below subcategories:

* Functional Testing - assert expected output for given inputs.
* Statistical Testing - test the API on unseen requests, and check online prediction distribution against training prediction distribution.
* Error handling - ensure the API handle bad inputs and produces helpful error messages. 
* Load testing - test API with x inputs over y seconds to ensure is scales appropriately and has optimal CPU/GPU utilisation. 
* End-to-end - validate all subsystems are working as expected. 

We can perform basic API testing using the api_test.py script in the test directory. This script can either be used with a local Docker conainter running or testing the hosted endpoint by setting the "--local" flag to True for local testing or False for testing the hosted endpoint. To test locally whilst running the docker container on port 8080, from the root directory run:

```bash
cd tests
python3 api_test.py -n 100
```

This will call the API with a batch of 100 test set examples, the expected return will look something like the below:

```
Time: 1.4840s
Accuracy: 99.60%
Prediction distribution: OrderedDict([(0, 43), (1, 67), (2, 54), (3, 45), (4, 55), (5, 50), (6, 42), (7, 50), (8, 40), (9, 54)])
```

Using the -p True flag we can also return a plot of the prediction distribution.

```bash
python3 api_test.py -n 100 -p True
```
<p align="center">
    <img src="docs/media/histogram.png" alt="Prediction histogram" width="400"/>
</p>

### Unit testing

To perform functional, error handling, and load testing whilst the deployed endpoint is live, run from the test directory:

```bash
pytest unit_tests.py
```

This test suite checks the endpoint is running by calling the root and checking it returns the expected "hello world" message. It also tests a 404 message is returned when attempting to reach a non-existent endpoint.

The test suite then asynchronously calls the batch prediction API with a batch of 100 images, 5 times, and checks if the output achieves the SLOs outlined in the introduction. Specifically, we test if all 500 predictions are returned in under 4s, with over 95% accuracy, with a successful response code. 

To check the API handles unusual inputs appropriately we also pass misshapen or missing data. For some of these inputs, the endpoint is expected to handle with input processing, whilst still raising warning messages that the image processing may degrade performance. Specifically passing a colour image that is not 28x28 pixels. The endpoint is also expected to handle individual image predictions as well as batches. For other inputs, the endpoint is expected to produce helpgul error messages, for example when passing a non-square image, or failing to pass image features. 

Note: these tests call the live endpoint deployed to AWS, but this will be torn down after a short period to save costs. 

## AWS Monitoring - CloudWatch

Through the infrastructure setup using Elastic Beanstalk, we also set up an AWS CloudWatch Monitoring job, from which we can view the key engineering metrics for our deployed API. From here we can also set up Alarms which can be configured to send a notification to the email provided when certain thresholds are breached. A snapshot of the dashboard is shown below:

<p align="center">
    <img src="docs/media/monitoring.png" alt="Prediction histogram" width="500"/>
</p>

## Tear Down

If you have run the AWS section of this repository please make sure to tear down any infrastructure used to save costs. Most of the infrastructure is eligible for AWS free tier, but if left running may run up some costs. Instructions to tearing down Elastic Beanstalk environment can be found [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/GettingStarted.Cleanup.html), deleting S3 buckets [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/delete-bucket.html), and deleting a ECS Repository [here](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-delete.html).

## Contact

If you face any issues or have any queries feel free to contact philiprj2@gmail.com and I will be happy to assist.
