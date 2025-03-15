import helpers.s3
import pytest

CLIENT_NAME = "ips"


def test_get_closest_metadata_fail():  # slow test
    date_y_m_d = "2019-12-15"  # should raise exception
    with pytest.raises(Exception) as e_info:
        channels, users, is_future = helpers.s3.get_closest_metadata(CLIENT_NAME, date_y_m_d)
    assert "Could not find metadata" in str(e_info.value)
