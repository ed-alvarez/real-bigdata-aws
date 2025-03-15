import socket
import threading
import time
from contextlib import contextmanager
from pathlib import Path

import pytest
from paramiko import AUTH_SUCCESSFUL, RSAKey, SFTPServer, Transport

from shared.shared_tests.fixtures.stub_ftp import StubServer, StubSFTPServer

BASE_DIR = Path(__file__).resolve().parent.resolve()

CLIENT_NAME = "testing"
BUCKET_NAME = f"{CLIENT_NAME}.ips"
S3_FIXTURES_DIR = f"{BASE_DIR}/shared_tests/fixtures"


@contextmanager
def parameters_shared_sftp_setup(ssm_client):
    with open(f"{BASE_DIR}/shared_tests/fixtures/sftp/sftpkey") as f:
        priv_key_contents = f.read()
    with open(f"{BASE_DIR}/shared_tests/fixtures/sftp/sftpkey.pub") as f:
        pub_key_contents = f.read()

    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/level_1/level2",
        Description="Levels of SSM",
        Value="value_content",
        Type="String",
    )

    ssm_client.put_parameter(
        Name=f"/default/level_1/level2",
        Description="Default Levels of SSM",
        Value="default_value_content",
        Type="String",
    )

    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/private_key",
        Description="private key",
        Value=priv_key_contents,
        Type="String",
    )
    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/public_key",
        Description="public key",
        Value=pub_key_contents,
        Type="String",
    )
    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/public_key_password",
        Description="public key",
        Value="KeyP@ssw0rd",
        Type="String",
    )

    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/password",
        Description="password",
        Value="P@ssw0rd",
        Type="String",
    )

    yield


@pytest.fixture
def ssm_shared_sftp_setup(ssm_client):
    result = parameters_shared_sftp_setup(ssm_client=ssm_client)
    yield result


@contextmanager
def parameters_shared_gpg_setup(ssm_client):
    with open(f"{BASE_DIR}/shared_tests/fixtures/gpg/default_key.pem") as f:
        priv_key_contents = f.read()

    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/voice/gpgprivkey.pem",
        Description="Client GPG PEM Key",
        Value="dummy_data",
        Type="String",
    )

    ssm_client.put_parameter(
        Name=f"/default/voice/gpgprivkey.pem",
        Description="Default GPG PEM key",
        Value=priv_key_contents,
        Type="String",
    )

    ssm_client.put_parameter(
        Name=f"/{CLIENT_NAME}/voice/gpgprivkeypass",
        Description="Client GPG PEM Key Passcode",
        Value="dummy_data",
        Type="String",
    )
    ssm_client.put_parameter(
        Name=f"/default/voice/gpgprivkeypass",
        Description="default GPG PEM Key Passcode",
        Value="drugs.declaim.calendar",
        Type="String",
    )
    yield


@pytest.fixture
def ssm_shared_gpg_setup(ssm_client):
    result = parameters_shared_gpg_setup(ssm_client=ssm_client)
    yield result


class TCPServer:
    def __init__(self, ssh_server_response):
        self._sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self._sock.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )
        self._ssh_server_response = ssh_server_response
        # self._host_key = paramiko.RSAKey(data=base64.b64decode('AAAAB3NzaC1yc2EAAAADAQABAAACAQDOCcWEDDx0jIgD4sFxE0hUXkhCEnCy6JlSbidnmOaL3No6SyXRNznzrptCYY2ImaOzW9rOWD1DOgS+XmyW6dyNpttpFE+6fqcR61mZ/8UwvlTusk+ALkFpeX/fMdm4aNNCj1UOk1zzkYCL3okkoxqg7RlO9/FAV6GMutHqDIoOwK3ZlibOilhXHBVTDZIZU5+OipRuIgsBhgyMYeB/9/xLsM9icQAiIG7XhC9dofEQCNl0D+K7XBfU5t+NEwkkq1ODwc+KIz/kTbuyIdYU5n0wjcWKKyQOaemy9u5vuJKEuAeAwWD9nXGtWiZBQXh6Fk0xbfltsVoPLMF7zXdfi/EJZFL+TGlXRXtA5O3h44s7Ws/eeaPTIwONe3SAL5ENoAjyjLHX5qvMhdPZ8Mw+5lqHkBWIWXY7VhLjK2ZpFwZR98vt7QqxG94tPbgqv8Q/LORroM44rep8ZE8OhMsSP7y0jTmwI+b6a98SjNmAqZrBtc0v6J3WAaQlsgj1BXLJumjWZWKGYUmOR+1YRHyX6+jQzn1Zp+TaIMGC3Okpo6RALXXQBDF2OzGgLHvZTkG7n4pq7uwEOBPucH+EcHmFYh0F3jzO3DIyH39AgZuh5hfd8vuzfZ4QwKkk20PAC9fuP7DHXfP4fAXw1JVEKCC7V0U8Cyn27XiuLaI/w8n5GRc/RQ=='))
        self._host_key = RSAKey(filename=f"{BASE_DIR}/shared_tests/fixtures/sftp/sftpkey")
        self._sock.bind(("127.0.0.1", 2225))

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._sock.close()

    def listen_for_traffic(self):
        while True:
            self._sock.listen(5)
            client, addr = self._sock.accept()
            t = Transport(client)
            t.set_gss_host(socket.getfqdn(""))
            t.load_server_moduli()
            t.add_server_key(self._host_key)
            t.set_subsystem_handler(
                "sftp",
                SFTPServer,
                StubSFTPServer,
            )
            server = StubServer(auth_return=self._ssh_server_response)
            t.start_server(server=server)
            channel = t.accept()
            while t.is_active():
                time.sleep(1)
            # time.sleep(5)


@pytest.fixture(scope="function")
def dummy_tcp_server(request):
    ssh_server_response = getattr(request, "param", AUTH_SUCCESSFUL)
    tcp_server = TCPServer(ssh_server_response=ssh_server_response)
    with tcp_server as example_server:
        thread = threading.Thread(target=example_server.listen_for_traffic)
        thread.daemon = True
        thread.start()
        yield example_server


@contextmanager
def s3_shared_setup(s3_client):
    bucket = s3_client.create_bucket(
        Bucket=BUCKET_NAME,
        CreateBucketConfiguration={"LocationConstraint": "eu-west-1"},
    )
    s3_mock_upload_list = []

    file_1 = (
        f"todo.voice/2021-09-22/20210922-151637_1632316597.19842.json.gpg",
        f"{S3_FIXTURES_DIR}/sftp/20210922-151637_1632316597.19842.json.gpg",
    )
    s3_mock_upload_list.append(file_1)

    file_2 = (
        f"todo.voice/2021-09-22/20210922-151637_1632316597.19842.wav.gpg",
        f"{S3_FIXTURES_DIR}/sftp/20210922-151637_1632316597.19842.wav.gpg",
    )
    s3_mock_upload_list.append(file_2)

    for file_pair in s3_mock_upload_list:
        mock_s3_upload(local_filename=file_pair[1], s3_key=file_pair[0], s3_client=s3_client)

    yield


def mock_s3_upload(local_filename, s3_key, s3_client):
    with open(local_filename, "rb") as f:
        s3_client.upload_fileobj(f, BUCKET_NAME, s3_key)


@pytest.fixture
def shared_s3_setup(s3_client):
    result = s3_shared_setup(s3_client)
    yield result
