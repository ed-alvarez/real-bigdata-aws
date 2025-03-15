from dataclasses import dataclass, field
from typing import Dict, List


@dataclass()
class ssh_server_creds:
    client_name: str = ""
    sftp_host: str = ""
    sftp_port: int = 22
    ssm_account_id: str = ""
    ssm_key_file: str = ""
    ssm_key_passcode: str = ""
    ssm_account_password: str = ""
