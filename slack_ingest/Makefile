sls-plugins:
	sls plugin install -n serverless-stage-manager --stage dev
	sls plugin install -n serverless-pseudo-parameters --stage dev
	sls plugin install -n serverless-python-requirements --stage dev
	sls plugin install --name serverless-step-functions --stage=dev

# run individual test files while developing if test suite takes too long to complete
test:
	pytest --cov=slack_parse --cov=helpers --cov-report term-missing tests
testout:
	pytest --cov=slack-parse --cov=helpers -s tests
qtest:
	pytest --cov=slack_parse --cov=helpers tests/test_slack_api_downloader.py tests/test_slack_download_common.py tests/test_slack_export.py tests/test_slack_processor.py tests/test_slack_es_document.py tests/test_slack_processor_attachments.py tests/test_slack_export_ent_grid.py
devtest:
	STAGE=dev make test
devqtest:
	STAGE=dev make qtest
# Invoke function for api download locally
slslocalapidownload:
	sls invoke local --function apidownloader --stage dev --data '{"client_name": "ips"}'
# Run chromium export download process in local docker container
localexport:
	./run-local-slack-export-docker.sh
