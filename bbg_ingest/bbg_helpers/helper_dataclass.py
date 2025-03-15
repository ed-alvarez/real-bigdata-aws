from dataclasses import dataclass, field
from typing import Dict, List


@dataclass()
class Base:
    client_name: str = ""
    files_downloaded: List = field(default_factory=list)
    files_decoded: List = field(default_factory=list)
    has_files: bool = False
    error: bool = False
    error_msg: str = ""


@dataclass
class DownloadLambdaParameters(Base):
    bbg_client_id: str = ""
    bbg_manifest: str = ""
    manifest_date: str = ""
    wait_until: str = ""


@dataclass()
class BbgFiles:
    MSG_XML_to_process: bool = False
    MSG_file_name: str = ""
    MSG_ATT_file_name: str = ""
    MSG_XML_record_number: int = 0
    IB_XML_to_process: bool = False
    IB_file_name: str = ""
    IB_ATT_file_name: str = ""
    IB_XML_record_number: int = 0


@dataclass()
class DecodeLambdaParameters(DownloadLambdaParameters):
    bbg_files: BbgFiles = BbgFiles()


@dataclass()
class StepFunctionParameters:
    client_name: str = ""
    bbg_client_id: str = ""
    bbg_manifest: str = ""
    manifest_date: str = ""
