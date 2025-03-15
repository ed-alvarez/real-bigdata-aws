import os

import pytest
from email_src.email_ingest_handler import lambda_handler
from email_tests.ses_records.test_event import create_event

CLIENT_NAME = "test-ips"
BUCKET_NAME = f"{CLIENT_NAME}.ips"

event = create_event(event_bucket=BUCKET_NAME, event_key="todo.email/mime/4ho0o54uiim77vmpsmkl8jbchtn2utci5ai382g1")


class TestUploads:
    @pytest.mark.skipif(os.environ.get("TEST_ENV") == "CICD", reason="No Java on Serverless CI/CD")
    def test_es_upload(self, email_s3_setup, test_lambda_context, s3_client):
        with email_s3_setup:
            response = lambda_handler(event=event, context=test_lambda_context, s3_client=s3_client)
        assert response == True
