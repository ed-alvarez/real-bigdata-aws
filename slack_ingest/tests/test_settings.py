import pytest
import settings


def test_non_existent_client_api_token():
    with pytest.raises(Exception) as e:
        token = settings.get_slack_api_token("non-existent-client")
        print(token)
    assert "ParameterNotFound" in str(e.value)


def test_try_non_existent_client_api_token():
    token = settings.try_get_slack_api_token("non-existent-client")
    print(token)
    assert token == ""


def test_invalid_client_api_token():
    with pytest.raises(Exception) as e:
        token = settings.get_slack_api_token("non existent client")
        print(token)
    print(str(e.value))
    assert "ValidationException" in str(e.value)
