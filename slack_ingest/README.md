# Installation and Setup
To install serverless

``` bash
npm install -g serverless
```

Use login to connect it to your serverless framework account
``` bash
sls login
```

Install serverless stage manager and other plugins:

``` bash
sls plugin install -n serverless-stage-manager --stage dev
sls plugin install -n serverless-pseudo-parameters --stage dev
sls plugin install -n serverless-python-requirements --stage dev
sls plugin install -n serverless-step-functions --stage=dev

```
or just run
``` sh
make sls-plugins
```
TODO make commands

Invoke locally
``` bash
sls invoke local --function download
sls invoke local --function processor
```

To run main tests (for dev feedback)
``` sh
make qtest
```

To run all tests:
``` sh
make test
```

or run individual tests with e.g.
``` sh
pytest -s tests/test_slack_processor.py
```
to maintain pace for development.

Read https://github.com/IP-Sentinel/bbg-parse/blob/master/LambdaLayers/read.me on how to obtain and install Tika. Env var TIKA_SERVER_JAR needs to be set (with the file:/// prefix) to file:///path/to/tika-server.jar
This downloads the tika file to the /tmp directory from the file path supplied. This may also support http urls.

Todos
- attachment parsing - done
- tika layer - done
- serverless deploy - done
- serverless invoke local - done
- cicd
- upload to elasticsearch - done


# Overview
This service is implemented as an AWS Step Function which orchestrates two main lambda functions, download_handler and
processor_handler. Functionality is implemented in slack_data.py and slack_processor respectively.

Slack download takes all the data from the Slack API, user lists, channel lists and channel members, and conversation
histories as well as attachments and saves them in the todo.slack folder of the client's S3 bucket.

Slack processor is supplied a list of s3 paths (keys) that point to channel conversation histories. Each history is then
processed and attachments are parsed, and an elasticsearch document is constructed and saved.


Slack download has been modified to be callable more than once and to continue where downloading left off. To force
re-download of all files pass the force=True parameter to the download_all_data method.


Attachments are saved as SLACKID.tgz and put into the relevant folder on S3.


ES uploads are batched by number of documents (500) and total size of documents (5mb).
The execution will stop itself if less than the min time specified in the environment variable LAMBDA_MIN_TIME_REQUIRED_SECS is available (lambdas know how much time remains from context.get_remaining_time_in_millis()), it will also return a data structure with continue=True and continuation information that can be passed into the next call to the lambda. The step function is set up so that It will iterate till complete.
