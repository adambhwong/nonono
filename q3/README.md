This project contains following elements:   
1. The Dockerfile & source (/app) for building the docker image url-shortener-api.  
2. The terraform folder (/tf) contains code for AWS DynamoDB table used by the URL-shortener.  
3. The Helm chart (/chart) for deploying the docker image to any Kubernetes cluster.  

Prerequisites:  
1. You should have an AWS account with generated admin permission access key.  
2. The execution server should be installed with AWS cli and configured with the access key.  
3. The execution server should be installed with Terraform.  
4. The execution server should be installed with kubectl and configured to connect with the target Kubernetes cluster.  
5. The execution server should be installed with Helm.  
6. The execution server should have cloned this sources repository.  
7. The execution server should be installed with Docker for building the source.
8. A Docker Registry should be ready for hosting the docker image produced.
9. A URL ready for use as the service endpoint of this deployment.
10. The kubernetes should support ACME to generate SSL cert along the deployment.

Deployment procedure:  
1. Create the Dynamodb table on AWS by execute following commands under /tf folder:  
```
terraform init
terraform apply
```
2. Build the source with the 'test_docker.sh' script, you should provide the AWS access key ID, secret key & region as parameter:  
```
./test_docker.sh -k <Key ID:Secret Key:Region>
```
You can test the API at this stage with 'curl' command agaist the image port '9099'.  
3. Tag and push the image to your docker registry.  
4. Change directory to /chart, modify values.yaml regarding to your environment.  
5. Create the namespace for the deployment.  
6. Create the aws-secert in namespace, the secret should contain "id", "key", "region" regarding to the AWS configuration.  
7. Use helm cli to install the app:  
```
helm -n <namespace> install production .
```  
8. Verfiy the service with curl post and get:  
```  
curl -d '{"url": "https://www.google.com"}' -X POST <Service URL>/newurl
```  
You should get the shorten URL from output, and try curl with it:
```
curl -i <shorten url>
```
sample output:
```
HTTP/1.1 304 Not Modified
Server: gunicorn
Date: Sun, 29 Aug 2021 12:35:51 GMT
Connection: close
content-location: https://www.google.com
```

Design:  
  
user request ----> url-shortener-api@EKS <---> ShortenUrl-table@DynamoDB      
  
1. The service logics run in the container "url-shortener-api", and data stored in AWS DynamoDB table. 
2. Since the DynamoDB table is a managed service provided by AWS, it already cater HA ability.
3. While the data is stored in DynamoDB, you can deploy any replica count of url-shortener-api in kubernetes clusters.
4. To scale up the service, simply modfiy the replica count in Kubernetes deployment.
