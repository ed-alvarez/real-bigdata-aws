import os
import sys
from contextlib import contextmanager
from pathlib import Path

import pytest

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.teams_data_processing_and_ingest.teams_conversation import (
    attachment_helper_functions,
)
from teams_src.teams_shared_modules.teams_data_classes import ClientCreds

AWS_REGION = os.environ.get("AWS_Region", "eu-west-1")

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"


class TestFunctions:
    @contextmanager
    def s3_setup(self, s3_client):
        bucket = s3_client.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
        yield

    def test_get_attachment_data(self, ssm_teams_setup):
        with ssm_teams_setup:
            client_creds: ClientCreds = ClientCreds(firm="test-ips", tenant_id="a38e65be-fb2c-4ab0-9084-199607af9f21")

        url = "https://ipsentinelltd-my.sharepoint.com/personal/mike_ip-sentinel_com1/Documents/Microsoft Teams Chat Files/Screenshot 2021-01-27 at 12.23.40.png"
        response = attachment_helper_functions.get_attachment_data(url=url, client_creds=client_creds)
        assert response

    attachment_fail = {
        "id": "1636475319930",
        "contentType": "messageReference",
        "contentUrl": None,
        "content": '{"messageId":"1636475319930","messagePreview":"well a bit more if they want voice transcriptions","messageSender": {"application":null,"device":null,"user": {"userIdentityType":"aadUser", "id":"28ad04f7-55d2-4fe8-b917-52f3c24ab13d","displayName":"James Hogbin"}}}',
        "name": None,
        "thumbnailUrl": None,
    }
    attachment_success = {
        "id": "86e8a7fd-b44c-4fc4-997d-cc67713fa897",
        "contentType": "reference",
        "contentUrl": "https://ipsentinelltd-my.sharepoint.com/personal/sean_fingerprint-supervision_com/Documents/Microsoft Teams Chat Files/Screenshot 2021-11-09 at 11.08.49.png",
        "content": None,
        "name": "Screenshot 2021-11-09 at 11.08.49.png",
        "thumbnailUrl": None,
    }

    case_1 = (attachment_fail, False)
    case_2 = (attachment_success, True)

    cases = [case_1, case_2]

    @pytest.mark.parametrize("attachment, expected", cases)
    def test_is_attachment_a_url_link(self, attachment, expected):
        response = attachment_helper_functions.is_attachment_a_url_link(attachment=attachment)
        assert response == expected
