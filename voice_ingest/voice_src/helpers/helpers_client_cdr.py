from typing import List


class ClientCDR:
    def __init__(self, client: str, file_stem: str):
        self._raw_file_stem: str = file_stem
        self._file_name: str = f"{self._raw_file_stem}.json"
        self._process_client(client=client)

    @property
    def FileName(self) -> str:
        return self._file_name

    def _process_client(self, client: str) -> str:
        file_name: str = ""
        if client == "ips":
            file_parts: List = self._raw_file_stem.split(".")
            file_name: str = (".").join([file_parts[0], "meta", file_parts[1], "json"])
            self._file_name = file_name
        return file_name
