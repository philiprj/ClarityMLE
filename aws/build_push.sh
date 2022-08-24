#!/usr/bin/env bash -e

# Define the image name 
image=${1:-clarity-api}
echo Image name: "${image}"

# Build the image from root
docker build -t "${image}" .

# Get the default account number
account=$(aws sts get-caller-identity --query Account --output text)
if [ $? -ne 0 ]
then 
    exit 255
fi 
    echo AWS Account: "${account}"

# Get the default region
region=$AWS_DEFAULT_REGION
region=${region:-$(aws configure get region || true)} 
region=${region:-eu-west-1}
echo AWS Region: "${region}"
export AWS_DEFAULT_REGION=$region

fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:latest"
docker tag "${image}" "${fullname}"

# If the ECR repo doesn't exist, create it
if ! aws ecr describe-repositories --repository-names "${image}" > /dev/null 2>&1
then
    echo Creating ECR repository "${image}"
    aws ecr create-repository --repository-name "${image}" > /dev/null
fi

# Gethe the login command from ECR and execute it
aws ecr get-login-password --region "${region}" | docker login --username AWS --password-stdin "${account}".dkr.ecr."${region}".amazonaws.com

docker push "${fullname}"