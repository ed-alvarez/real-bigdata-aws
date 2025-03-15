""" Test suite for attachments. Run tika server using java -jar tika-server.jar or simply set
TIKA_JAVA=/usr/bin/java
TIKA_SERVER_JAR=/Users/anthony/Downloads/tika/1.24/tika-server-1.24-bin/tika-server.jar
to the java and the tika-server.jar path and the python module will start up the server for you.
Download tika-server.jar from https://repo1.maven.org/maven2/org/apache/tika/tika-server/
"""

import os

import helpers.attachments
import helpers.s3
import pytest
import settings
import slack_parse.download_api.slack_api_downloader
import slack_parse.process.slack_processor

CLIENT_NAME = "ips"


def test_6th_jan_documents_go_in_right_places_with_zip(monkeypatch):
    date_y_m_d = "2021-01-06"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "zip")

    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    try:
        s3.delete_file(f"dev.processed.slack/{date_y_m_d}/attachments/F01JT4DCVMW.zip")
        s3.delete_file(f"dev.archived.slack/{date_y_m_d}/attachments/F01JT4DCVMW.zip")
    except Exception as e:
        print(str(e))
        pass

    # Download attachment to _todo and archived
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d)

    """
    Not needed anymore as download is now in processor.
    # Check attachment is at _todo and archived
    todo_attachment_path = f'dev.todo.slack/{date_y_m_d}/attachments/F01JT4DCVMW.tgz'
    res = s3.get(todo_attachment_path)
    assert(res is not None)
    archived_attachment_path = f'dev.archived.slack/{date_y_m_d}/attachments/F01JT4DCVMW.tgz'
    res = s3.get(archived_attachment_path)
    assert (res is not None
    """

    # Do processing step
    sp = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    assert sp["ok"] is True
    # Check processed and archived versions of files still there, _todo gone.
    processed_attachment_path = f"dev.processed.slack/{date_y_m_d}/attachments/F01JT4DCVMW.zip"
    res = s3.get(processed_attachment_path)
    assert res is not None
    archived_attachment_path = f"dev.archived.slack/{date_y_m_d}/attachments/F01JT4DCVMW.zip"
    res = s3.get(archived_attachment_path)
    assert res is not None
    todo_attachment_path = f"dev.todo.slack/{date_y_m_d}/attachments/F01JT4DCVMW.zip"
    with pytest.raises(Exception) as e_info:
        res = s3.get(todo_attachment_path)
    assert "NoSuchKey" in str(e_info.value)

    # Check tmp files gone
    extracted_path = os.path.join(
        settings.TEMPDIR,
        "attachments_processing",
        "test_document_to_upload_into_slack.docx",
    )
    assert os.path.isfile(extracted_path) is not True
    tar_tmp_path = os.path.join(
        settings.TEMPDIR,
        "todo",
        "attachments",
        "test_document_to_upload_into_slack.docx",
    )
    assert os.path.isfile(tar_tmp_path) is not True


def test_get_contents_from_slack_correctly_with_zip(monkeypatch):
    date_y_m_d = "2021-01-06"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "zip")
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    SLACK_API_TOKEN = settings.get_slack_api_token(CLIENT_NAME)
    ATTACH_URL = "https://files.slack.com/files-pri/TP2JMH5U3-F01JT4DCVMW/test_document_to_upload_into_slack.docx"
    text, error, s3_path = helpers.attachments.get_attachment_data(
        CLIENT_NAME,
        date_y_m_d,
        "F01JT4DCVMW",
        file_name="Test document to upload into slack.docx",
        file_date=1609926380,
        is_todo=True,  # Download from Slack
        url=ATTACH_URL,
        slack_api_token=SLACK_API_TOKEN,
    )

    print(text, error, s3_path)
    assert "Yadda" in text
    assert error == ""
    attach_file = s3.get(s3_path)
    assert attach_file is not None


def test_get_contents_from_archive_correctly_with_zip(monkeypatch):
    date_y_m_d = "2021-01-06"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "zip")
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    # SLACK_API_TOKEN = settings.get_slack_api_token(CLIENT_NAME)
    # ATTACH_URL = "https://files.slack.com/files-pri/TP2JMH5U3-F01JT4DCVMW/test_document_to_upload_into_slack.docx"
    text, error, s3_path = helpers.attachments.get_attachment_data(
        CLIENT_NAME,
        date_y_m_d,
        "F01JT4DCVMW",
        file_name="Test document to upload into slack.docx",
        file_date=1609926380,
        is_todo=False,  # Obtain from Ss3 archive
        # url=ATTACH_URL,
        # slack_api_token=SLACK_API_TOKEN
    )

    print(text, error, s3_path)
    assert "Yadda" in text
    assert error == ""
    attach_file = s3.get(s3_path)
    assert attach_file is not None


def test_get_contents_from_slack_correctly_with_tgz(monkeypatch):
    date_y_m_d = "2021-01-06"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "tgz")
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    SLACK_API_TOKEN = settings.get_slack_api_token(CLIENT_NAME)
    ATTACH_URL = "https://files.slack.com/files-pri/TP2JMH5U3-F01JT4DCVMW/test_document_to_upload_into_slack.docx"
    text, error, s3_path = helpers.attachments.get_attachment_data(
        CLIENT_NAME,
        date_y_m_d,
        "F01JT4DCVMW",
        file_name="Test document to upload into slack.docx",
        file_date=1609926380,
        is_todo=True,  # Download from Slack
        url=ATTACH_URL,
        slack_api_token=SLACK_API_TOKEN,
    )

    print(text, error, s3_path)
    assert "Yadda" in text
    assert error == ""
    attach_file = s3.get(s3_path)
    assert attach_file is not None


def test_get_contents_from_archive_correctly_with_tgz(monkeypatch):
    date_y_m_d = "2021-01-06"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "tgz")
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    # SLACK_API_TOKEN = settings.get_slack_api_token(CLIENT_NAME)
    # ATTACH_URL = "https://files.slack.com/files-pri/TP2JMH5U3-F01JT4DCVMW/test_document_to_upload_into_slack.docx"
    text, error, s3_path = helpers.attachments.get_attachment_data(
        CLIENT_NAME,
        date_y_m_d,
        "F01JT4DCVMW",
        file_name="Test document to upload into slack.docx",
        file_date=1609926380,
        is_todo=False,  # Obtain from Ss3 archive
        # url=ATTACH_URL,
        # slack_api_token=SLACK_API_TOKEN
    )

    print(text, error, s3_path)
    assert "Yadda" in text
    assert error == ""
    attach_file = s3.get(s3_path)
    assert attach_file is not None


def test_mp3_ignored_with_zip_archive_type_dl_from_slack_todo(monkeypatch):
    date_y_m_d = "2021-01-19"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "zip")

    # sd = slack_parse.slack_data.SlackData(CLIENT_NAME)
    # data = sd.download_all_data(date_y_m_d)
    ATTACH_URL = "https://files.slack.com/files-pri/TP2JMH5U3-F01JQMS00SK/i_ll-talk-for-14-hours_-and-three-of-those-will-be-untranslatable-literally-baby-noises.mp3"
    SLACK_API_TOKEN = settings.get_slack_api_token(CLIENT_NAME)
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    text, error, s3_path = helpers.attachments.get_attachment_data(
        CLIENT_NAME,
        date_y_m_d,
        "F01JQMS00SK",
        file_name="i'll-talk-for-14-hours!-and-three-of-those-will-be-untranslatable-literally-baby-noises.mp3",
        file_date=1611073993,
        is_todo=True,  # Download from Slack
        url=ATTACH_URL,
        slack_api_token=SLACK_API_TOKEN,
    )
    assert text == ""
    assert "skipped" in error
    # Assert that file was saved to archived
    att = s3.get(s3_path)
    assert att is not None


def test_mp3_ignored_with_zip_archive_type_dl_from_slack_archive(monkeypatch):
    date_y_m_d = "2021-01-19"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "zip")

    # sd = slack_parse.slack_data.SlackData(CLIENT_NAME)
    # data = sd.download_all_data(date_y_m_d)
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    text, error, s3_path = helpers.attachments.get_attachment_data(
        CLIENT_NAME,
        date_y_m_d,
        "F01JQMS00SK",
        file_name="i'll-talk-for-14-hours!-and-three-of-those-will-be-untranslatable-literally-baby-noises.mp3",
        file_date=1611073993,
        is_todo=False,  # Download from S3
        # url=ATTACH_URL,
        # slack_api_token=SLACK_API_TOKEN
    )
    assert text == ""
    assert "skipped" in error
    # Assert that file was saved to archived
    att = s3.get(s3_path)
    assert att is not None


def test_6th_jan_documents_go_in_right_places(monkeypatch):
    date_y_m_d = "2021-01-06"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "tgz")

    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    try:
        s3.delete_file(f"dev.processed.slack/{date_y_m_d}/attachments/F01JT4DCVMW.tgz")
        s3.delete_file(f"dev.archived.slack/{date_y_m_d}/attachments/F01JT4DCVMW.tgz")
    except Exception as e:
        print(str(e))
        pass

    # Download attachment to _todo and archived
    sd = slack_parse.download_api.slack_api_downloader.SlackData(CLIENT_NAME)
    data = sd.download_all_data(date_y_m_d, force=True)

    """
    # Check attachment is at _todo and archived
    todo_attachment_path = f'dev.todo.slack/{date_y_m_d}/attachments/F01JT4DCVMW.tgz'
    res = s3.get(todo_attachment_path)
    assert(res is not None)
    archived_attachment_path = f'dev.archived.slack/{date_y_m_d}/attachments/F01JT4DCVMW.tgz'
    res = s3.get(archived_attachment_path)
    assert (res is not None
    """

    # Do processing step
    sp = slack_parse.process.slack_processor.process_slack_from_lambda_event(data)
    assert sp["ok"] is True

    # Check processed and archived versions of files still there, _todo gone.
    processed_attachment_path = f"dev.processed.slack/{date_y_m_d}/attachments/F01JT4DCVMW.tgz"
    res = s3.get(processed_attachment_path)
    assert res is not None
    archived_attachment_path = f"dev.archived.slack/{date_y_m_d}/attachments/F01JT4DCVMW.tgz"
    res = s3.get(archived_attachment_path)
    assert res is not None
    todo_attachment_path = f"dev.todo.slack/{date_y_m_d}/attachments/F01JT4DCVMW.tgz"
    with pytest.raises(Exception) as e_info:
        res = s3.get(todo_attachment_path)
    assert "NoSuchKey" in str(e_info.value)

    # Check tmp files gone
    extracted_path = os.path.join(
        settings.TEMPDIR,
        "attachments_processing",
        "test_document_to_upload_into_slack.docx",
    )
    assert os.path.isfile(extracted_path) is not True
    tar_tmp_path = os.path.join(
        settings.TEMPDIR,
        "todo",
        "attachments",
        "test_document_to_upload_into_slack.docx",
    )
    assert os.path.isfile(tar_tmp_path) is not True


def test_get_contents_correctly_with_tgz(monkeypatch):
    date_y_m_d = "2021-01-06"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "tgz")
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    # Download attachment from archived s3 path to local tmp
    local_tar_path = s3.download_attachment_to_tmp("F01JT4DCVMW", is_todo=False)
    (
        filename,
        file_size,
        text,
        warn_msg,
    ) = helpers.attachments._get_data_from_tmp_tar_attachment(local_tar_path)
    print(file_size, warn_msg)
    os.remove(local_tar_path)

    assert filename == "Test document to upload into slack.docx"
    # assert(filename == 'test_document_to_upload_into_slack.docx')
    assert "Yadda" in text
    assert os.path.isfile(os.path.join(settings.TEMPDIR, "attachments_processing", filename)) is not True


def test_get_contents_correctly_with_zip(monkeypatch):
    date_y_m_d = "2021-01-06"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "zip")
    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    # Download attachment from archived s3 path to local tmp
    local_tar_path = s3.download_attachment_to_tmp("F01JT4DCVMW", is_todo=False)
    (
        filename,
        file_size,
        text,
        warn_msg,
    ) = helpers.attachments._get_data_from_tmp_tar_attachment(local_tar_path)
    print(file_size, warn_msg)
    os.remove(local_tar_path)

    assert filename == "Test document to upload into slack.docx"
    # assert(filename == 'test_document_to_upload_into_slack.docx')
    assert "Yadda" in text
    assert os.path.isfile(os.path.join(settings.TEMPDIR, "attachments_processing", filename)) is not True


def test_mp3_ignored(monkeypatch):
    date_y_m_d = "2021-01-19"
    monkeypatch.setattr(settings, "ARCHIVE_EXTENSION", "tgz")

    # sd = slack_parse.slack_data.SlackData(CLIENT_NAME)
    # data = sd.download_all_data(date_y_m_d)

    s3 = helpers.s3.S3(CLIENT_NAME, date_y_m_d)
    # Download attachment from archived s3 path to local tmp
    local_tar_path = s3.download_attachment_to_tmp("F01JQMS00SK", is_todo=False)
    (
        filename,
        file_size,
        text,
        warn_msg,
    ) = helpers.attachments._get_data_from_tmp_tar_attachment(local_tar_path)
    os.remove(local_tar_path)
    print(file_size, warn_msg)

    # original_filename = "i'll-talk-for-14-hours!-and-three-of-those-will-be-untranslatable-literally-baby-noises.mp3"
    translated_filename = "i_ll-talk-for-14-hours_-and-three-of-those-will-be-untranslatable-literally-baby-noises.mp3"
    assert filename == translated_filename
    assert text == ""  # Mp3 file type
    assert os.path.isfile(os.path.join(settings.TEMPDIR, "attachments_processing", filename)) is not True


def test_trigger_parse_with_tika_from_path_error():
    text, err = helpers.attachments._parse_with_tika("duff path")
    assert err == "Error parsing attachment"
    # with pytest.raises(Exception) as e_info:
    #    print(e_info)


def test_download_invalid_url_from_slack():
    content, err = helpers.attachments.download_attachment_from_slack("asdf", "no token")
    assert content is None
    assert err == "Error downloading"
