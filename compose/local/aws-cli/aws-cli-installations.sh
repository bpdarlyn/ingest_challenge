#!/bin/bash

# get architecture
ARCHITECTURE=$(uname -m)


# check url if is x86 or arm
if [ "$ARCHITECTURE" == "x86_64" ]; then
    URL="https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip"
    URL_AWS_CLI="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
elif [ "$ARCHITECTURE" == "aarch64" ]; then
    URL="https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-arm64.zip"
    URL_AWS_CLI="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"
else
    echo "ARCHITECTURE not supported"
    exit 1
fi

TEMP_DIR="/tmp/aws-installations"
mkdir -p $TEMP_DIR

echo "Installing AWS CLI"
wget $URL_AWS_CLI -O "$TEMP_DIR/awscliv2.zip"
unzip "$TEMP_DIR/awscliv2.zip" -d "$TEMP_DIR/aws-cli-installation"

./"$TEMP_DIR/aws-cli-installation/aws/install"
aws --version


# Download SAM CLI
echo "Downloading SAM CLI from $URL"
wget $URL -O "$TEMP_DIR/aws-sam-cli.zip"

# Uncompress file
unzip "$TEMP_DIR/aws-sam-cli.zip" -d "$TEMP_DIR/sam-installation"

# Install
./"$TEMP_DIR/sam-installation/install"

# Check installation
sam --version
