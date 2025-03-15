FROM --platform=linux/x86_64 public.ecr.aws/lambda/python:3.9-x86_64 as stage

# Hack to install chromium dependencies
RUN yum install -y -q sudo unzip

# Find the version of latest stable build of chromium from below
# https://omahaproxy.appspot.com/
# https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Linux_x64/
# Then follow the instructions here in below URL
# to download old builds of Chrome/Chromium that are stable
# Current stable version of Chromium
#ENV CHROMIUM_VERSION=1096099
#ENV CHROMIUM_GENERATION=1674558007674030
#ENV CHROMIUM_DRIVER_GENERATION=1674558014049418
ENV CHROMIUM_VERSION=1002910
ENV CHROMIUM_GENERATION=1652397748160413
ENV CHROMIUM_DRIVER_GENERATION=1652397753719852


# Install Chromium
COPY install-browser.sh /tmp/
RUN /usr/bin/bash /tmp/install-browser.sh

FROM --platform=linux/x86_64 public.ecr.aws/lambda/python:3.9-x86_64 as base

COPY chrome-deps.txt /tmp/
RUN yum install -y $(cat /tmp/chrome-deps.txt)
RUN yum install -y gcc

# Install Python dependencies for function
COPY requirements.txt /tmp/
RUN python3 -m pip install --upgrade pip -q
RUN python3 -m pip install -r /tmp/requirements.txt -q
RUN yum remove -y gcc

COPY --from=stage /opt/chrome /opt/chrome
COPY --from=stage /opt/chromedriver /opt/chromedriver

COPY slack_parse/download_api ${LAMBDA_TASK_ROOT}/slack_parse/download_api
COPY slack_parse/download_export ${LAMBDA_TASK_ROOT}/slack_parse/download_export
COPY slack_parse/ingest_helpers ${LAMBDA_TASK_ROOT}/slack_parse/ingest_helpers
COPY slack_parse/process ${LAMBDA_TASK_ROOT}/slack_parse/process
COPY es_schema ${LAMBDA_TASK_ROOT}/es_schema
COPY helpers ${LAMBDA_TASK_ROOT}/helpers
COPY settings.py ${LAMBDA_TASK_ROOT}

CMD [ "slack_parse.download_export.slack_export_downloader.lambda_handler" ]