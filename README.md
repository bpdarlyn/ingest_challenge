# How to Run



## Pre-requisities

It was tested with the following tools

- Docker Compose: v2.17.3
- Docker Engine: 23.0.5
- Docker Desktop 4.19.0 (106363)
- At least 8GB of space in your computer





## Settings

Clone repository

```
git clone git@github.com:bpdarlyn/ingest_challenge.git
```

Copy the .env.example

```
cp .env.example .env

# Content .env
STACK_VERSION=8.14.2
```

Copy your aws credentials (just used to upload files to s3 the first time)

```
cp compose/local/aws-cli/credentials-example compose/local/aws-cli/credentials

# content compose/local/aws-cli/credentials
# Request the testing access key on the meeting
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
region = us-east-1
```



## Run

Run Entire App

```
docker compose -f local.yml up --build
```

Open another terminal and sync the index

```
docker compose -f local.yml exec celeryworker python manage.py migrate
docker compose -f local.yml exec celeryworker python manage.py search_index --rebuild
```



## Test

- Go to `http://localhost:5601` to see if all nodes are working well

- Step to execute the postman collection:

  1. Get a Presigned Url

  ```
  # This ENDPOINT will allow use to upload directly files to s3, without overload the django server
  GET http://localhost:8000/api/v1/generate-presigned-url?filename=organizations-2000000.csv
  ```

  2. With the presigned url do a `PUT` request with attached file
  3. With the s3 key and s3 bucket obtained in the first step enqueue a JOB

  Request

  ```
  http://localhost:8000/api/v1/enqueue-job
  
  # body
  {
      "s3_bucket": "ingest-backend-100-tmp",
      "s3_key": "uploads/20240709120637/organizations-2000000.csv"
  }
  ```

  4. Use the status endpoint to know the status and the time execution for this task
  5. Start using the `search` endpoint
