#!/bin/bash
# env;

# Install requirements.txt
pip3 install -r requirements.txt;

# Install aws if missing (on sls cicd)
if ! command -v aws &> /dev/null
then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    if command -v yum &> /dev/null
    then
        yum install -y unzip
    fi
    unzip awscliv2.zip
    ./aws/install
    # Cleanup or ends up being copied to CloudFormation Stack
    rm awscliv2.zip
    rm -rf aws
fi


# Install google-chrome and dependencies if on sls-cicd
if command -v yum &> /dev/null
then
    yum install -y wget
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
    yum install -y ./google-chrome-stable_current_x86_64.rpm
    # Cleanup or ends up being copied to CloudFormation Stack
    rm ./google-chrome-stable_current_x86_64.rpm
fi

# Copy chrome and chromedriver binaries from S3 bucket
aws s3 cp s3://ips.ips/cicd/binaries/chromium/slack/chromedriver ./chromium/chromedriver
chmod +x ./chromium/chromedriver;
aws s3 cp s3://ips.ips/cicd/binaries/chromium/slack/headless-chromium ./chromium/headless-chromium
chmod +x chromium/headless-chromium

# Install Java for Tika parser
if command -v yum &> /dev/null
then
    # sls cicd
    yum install -y java-1.8.0-openjdk-headless.x86_64;
else
    # github actions
    sudo apt install python3.8
    sudo apt install python3.7
    sudo apt-get install openjdk-8-jre
fi
