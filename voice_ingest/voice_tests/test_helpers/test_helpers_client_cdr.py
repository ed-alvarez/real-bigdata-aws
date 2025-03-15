import pytest
from voice_src.helpers.helpers_client_cdr import ClientCDR


class TestFunctions:

    stem = "1634749641.41584"

    test_1 = (stem, "ips", "1634749641.meta.41584.json")
    test_2 = (stem, "valeur", "1634749641.41584.json")
    test_3 = (stem, "", "1634749641.41584.json")

    CASES = [test_1, test_2, test_3]

    @pytest.mark.parametrize("file_stem, client, expected", CASES)
    def test__process_client(self, file_stem, client, expected):
        test_obj = ClientCDR(client=client, file_stem=file_stem)
        assert test_obj.FileName == expected
