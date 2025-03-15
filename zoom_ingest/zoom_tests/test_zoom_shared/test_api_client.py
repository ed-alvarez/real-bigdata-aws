import pytest

from zoom_ingest.zoom_shared.api_client import ZoomAPI


class TestZoom:
    @pytest.fixture
    def zoom_client():
        return ZoomAPI("melqart", "2022-08-17", "2022-08-19")

    def test_create_instance(self, zoom_client):
        assert isinstance(zoom_client, ZoomAPI)

    def test_get_bearer(self, zoom_client):
        token = zoom_client.token
        assert len(token) > 20

    def test_list_users(self, zoom_client):
        result, _ = zoom_client.list_users()
        assert type(result) == list

    def test_list_calls_logs(self, zoom_client):
        result = zoom_client.list_calls_logs()
        assert type(result) == list

    def test_list_meetings_recordings(self, zoom_client):
        user_id = "XD5VZiZVTMCrBnaw7Dw0iw"
        result = zoom_client.list_meetings_recordings(user_id)
        assert type(result) == list

    def test_list_phone_recordings(self, zoom_client):
        call_id = "bfeb6574-6eb8-45ad-b818-f0ca4f904b08"
        result = zoom_client.list_phone_recordings(call_id)
        assert result["file_url"]

    def test_call_download_transcript(self, zoom_client):
        recording_id = "581f05d5a1b94bb9a1f9917f66458cca"
        result = zoom_client.call_download_transcript(recording_id)
        assert result is not None

    def test_download_endpoint(self, zoom_client):
        download_url = "https://melqart.zoom.us/rec/download/POelSojOTUWxNRgUAgDPUdO8UjOu70D3hL7eva8y0HK4Wb4-q3Usa4yGvfFQ3itnejn4tMV56ZxOfQpU.7JC8DNLxloqNlN4t"
        result = zoom_client.download_endpoint(download_url, zoom_client.token)
        assert result is not None
