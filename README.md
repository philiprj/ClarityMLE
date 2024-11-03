# Model Deployment Experiment

Exploration of model deployment for handwritten digit classifier.

## Service Level Objectives (SLOs)

- [X] 99.99% uptime - tested over 24 hours (no downtime).
- [X] 500 predictions within 4s (tested in unit_test.py with 5 asynchronous calls of 100 images).
- [X] > 95% accuracy on unseen test images.
- [X] Dashboard to show the relevant engineering metrics and model observability (AWS CloudWatch).

## Plan

The plan for this solution involves creating an online inference REST API which takes JSON input holding a list of images, with features represented as floats in a list. This enables us to batch together predictions for more efficient inference. The inference endpoint will then be hosted on AWS, using Elastic Beanstalk to manage infrastructure deployment. We could set up compute and autoscaling/load balancing manually with more fine-grained control but this would require far more setup time. AWS Sagemaker also offers managed host solutions. Application monitoring and alerts can be easily managed through Elastic Beanstalk Health and Monitoring dashboards. Logs can also be extracted from the Elastic Beanstalk Logs tab, these are automatically generated through the Uvicorn service.

The detailed plan can be seen below:

- [X] Create inference API using FastAPI. (alternatives such as Flask, TensorFlow and PyTorch Serving could achieve a similar effect). Why an API? By creating a standalone inference microservice, the model can be integrated with several apps which can call the API a black box, rather than worry about what is going on under the hood. 
- [X] Containerisation - Docker container for the prediction API.
- [X] Batching online prediction for performance. Can batch list inputs, currently no batch endpoint for raw image files. 
- [X] Cloud deployment - AWS for deployment using Elastic Beanstalk with EC2 instances.
- [X] Auto scaling and load balancing - Our Elastic Beanstalk service creates an Auto Scaling Group and Elastic Load Balancer to route traffic to the EC2 instances running our endpoints. 
- [X] Application Monitoring - metrics, logs, tracing (API latency, log errors, service health metrics).
- [X] Model Observability - prediction distribution (compared to training distribution), data quality. A model card with the key model metrics and details can be seen in the docs directory.  
- [X] IaC - As far as possible follow engineering best practices by defining infrastructure as code. Define bash scripts to build and push Docker Images, Deploy Infrastructure using Elastic Beanstalk script. Create automated unit tests using pytest that tests if the endpoint achieves the objectives and how it behaves with unexpected inputs.
- [X] Testing - To ensure the model is meating the project objectives, engineering and data science objectives, we have implimented a set of tests using pytest in the test directory. This should comfirm the hosted model is acheiving the latency and performance requirements, and handles errors gracefully.  
 
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

We can perform basic API testing using the api_test.py script in the test directory. This script can either be used with a local Docker conainter running or testing the hosted endpoint by setting the "--local" flag to True for local testing or False for testing the hosted endpoint. To test locally whilst running the docker container on port 80, from the root directory run:

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
