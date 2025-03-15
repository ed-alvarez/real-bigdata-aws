#!/bin/bash
echo  Test with curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"client_name":"ips", "date_y_m_d": "2021-03-15"}'
docker build -t slackexportdownloaderdocker . && docker run -p 9000:8080 -v ~/.aws:/root/.aws slackexportdownloaderdocker
