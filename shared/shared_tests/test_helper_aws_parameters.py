import pytest
from shared_src.helper_aws_parameters import AWS_Key_Parameters


class TestFunctions:
    def test_param_key_gen(self):
        item_key = "lots/of/levels"
        branch = "branch root"
        result = AWS_Key_Parameters.param_key_gen(item_key=item_key, ssm_branch=branch)
        assert result == f"/{branch}/{item_key}"

    CASES = [
        ("testing", "level_1/level2", "value_content"),
        ("testing", "level_1", ""),
        ("testing", "level_1/", ""),
        ("testing", "", ""),
        ("fred", "level_1", ""),
        ("", "", ""),
    ]

    @pytest.mark.parametrize("in_client, in_key, expected", CASES)
    def test_get_individual_parameter(self, in_client, in_key, expected, ssm_shared_sftp_setup):
        with ssm_shared_sftp_setup:
            test_obj = AWS_Key_Parameters()
            result = test_obj._get_individual_parameter(item_key=in_key, client_name=in_client)
            assert result == expected

    CASES = [
        ("testing", "level_1/level2", "value_content"),
        ("fred", "level_1/level2", "default_value_content"),
        ("testing", "level_1", ""),
        ("fred", "level_1", ""),
        ("testing", "level_1/", ""),
        ("testing", "", ""),
        ("", "", ""),
    ]

    @pytest.mark.parametrize("in_client, in_key, expected", CASES)
    def test_get_parameter_value(self, in_client, in_key, expected, ssm_shared_sftp_setup):
        with ssm_shared_sftp_setup:
            test_obj = AWS_Key_Parameters()
            result = test_obj.get_parameter_value(item_key=in_key, client_name=in_client)
            assert result == expected
