FROM python:3.10

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY compose/local/aws-cli/aws-cli-installations.sh aws-cli-installations.sh
RUN chmod +x aws-cli-installations.sh
RUN ./aws-cli-installations.sh

COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

COPY compose/local/aws-cli/credentials /root/.aws/credentials

WORKDIR /app
