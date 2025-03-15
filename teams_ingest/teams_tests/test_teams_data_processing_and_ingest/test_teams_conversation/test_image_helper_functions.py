import sys
from pathlib import Path
from typing import Dict, List

import pytest

tenant_directory = Path(__file__).resolve().parent.parent
root_dir = tenant_directory.parent
sys.path.insert(0, str(root_dir))
sys.path.append(str(tenant_directory))
from teams_src.teams_data_processing_and_ingest.teams_conversation import (
    image_helper_functions,
)
from teams_src.teams_shared_modules.teams_data_classes import ClientCreds, imageURL

body: Dict = {
    "contentType": "html",
    "content": "<div><div>\n"
    "<div><span>"
    '<img height="222" src="https://graph.microsoft.com/beta/chats/19:28ad04f7-55d2-4fe8-b917-52f3c24ab13d_9a618be6-2988-4202-84cf-634ecc976bf2@unq.gbl.spaces/messages/1608551081694/hostedContents/aWQ9eF8wLXdldS1kNS1kZTNiYWNjZmU2MGJlNzExODJiZDAyMDUyYjNmMzI1Nyx0eXBlPTEsdXJsPWh0dHBzOi8vZXUtYXBpLmFzbS5za3lwZS5jb20vdjEvb2JqZWN0cy8wLXdldS1kNS1kZTNiYWNjZmU2MGJlNzExODJiZDAyMDUyYjNmMzI1Ny92aWV3cy9pbWdv/$value" width="2706" style="vertical-align:bottom; width:2706px; height:222px"></span><span><img src="https://graph.microsoft.com/beta/chats/19:28ad04f7-55d2-4fe8-b917-52f3c24ab13d_9a618be6-2988-4202-84cf-634ecc976bf2@unq.gbl.spaces/messages/1611748617729/hostedContents/aWQ9LHR5cGU9MSx1cmw9aHR0cHM6Ly9ldS1hcGkuYXNtLnNreXBlLmNvbS92MS9vYmplY3RzLzAtd2V1LWQ5LTM1OWVkYjExMDlhYTM0ZTcyZGE1MTY2NjU5ODgyNGJmL3ZpZXdzL2ltZ28=/$value" style="width:828px; height:1047px"></span>\n\n</div>\n\n\n</div>\n</div>',
}


class TestFunctions:
    def test_extract_images_from_content(self):
        response: List = image_helper_functions._extract_images_from_content(content=body["content"])
        assert "https://graph.microsoft.com/beta/chats" in response[0]
        assert len(response) == 2

    def test_get_image_data(self, ssm_teams_setup):
        with ssm_teams_setup:
            client_creds: ClientCreds = ClientCreds(firm="test-ips", tenant_id="a38e65be-fb2c-4ab0-9084-199607af9f21")
        url: str = "https://graph.microsoft.com/beta/chats/19:28ad04f7-55d2-4fe8-b917-52f3c24ab13d_9a618be6-2988-4202-84cf-634ecc976bf2@unq.gbl.spaces/messages/1608551081694/hostedContents/aWQ9eF8wLXdldS1kNS1kZTNiYWNjZmU2MGJlNzExODJiZDAyMDUyYjNmMzI1Nyx0eXBlPTEsdXJsPWh0dHBzOi8vZXUtYXBpLmFzbS5za3lwZS5jb20vdjEvb2JqZWN0cy8wLXdldS1kNS1kZTNiYWNjZmU2MGJlNzExODJiZDAyMDUyYjNmMzI1Ny92aWV3cy9pbWdv/$value"
        response: bytes = image_helper_functions._get_image_data(url=url, client_creds=client_creds)
        assert response

    def test_decode_image_url(self):
        url: str = "https://graph.microsoft.com/beta/chats/19:28ad04f7-55d2-4fe8-b917-52f3c24ab13d_9a618be6-2988-4202-84cf-634ecc976bf2@unq.gbl.spaces/messages/1608551081694/hostedContents/aWQ9eF8wLXdldS1kNS1kZTNiYWNjZmU2MGJlNzExODJiZDAyMDUyYjNmMzI1Nyx0eXBlPTEsdXJsPWh0dHBzOi8vZXUtYXBpLmFzbS5za3lwZS5jb20vdjEvb2JqZWN0cy8wLXdldS1kNS1kZTNiYWNjZmU2MGJlNzExODJiZDAyMDUyYjNmMzI1Ny92aWV3cy9pbWdv/$value"
        response: imageURL = image_helper_functions._decode_image_url(url=url)
        assert response.chat_id == "19:28ad04f7-55d2-4fe8-b917-52f3c24ab13d_9a618be6-2988-4202-84cf-634ecc976bf2@unq.gbl.spaces"
        assert response.message_id == "1608551081694"
        assert (
            response.hosted_contents_id
            == "aWQ9eF8wLXdldS1kNS1kZTNiYWNjZmU2MGJlNzExODJiZDAyMDUyYjNmMzI1Nyx0eXBlPTEsdXJsPWh0dHBzOi8vZXUtYXBpLmFzbS5za3lwZS5jb20vdjEvb2JqZWN0cy8wLXdldS1kNS1kZTNiYWNjZmU2MGJlNzExODJiZDAyMDUyYjNmMzI1Ny92aWV3cy9pbWdv"
        )
