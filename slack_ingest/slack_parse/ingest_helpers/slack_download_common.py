# Common methods to save json files to S3 shared between API download (slack_data) and export downloader (slack_export_downloader).

import logging
import os
from typing import Optional

import helpers.s3
import settings

log = logging.getLogger()


def _determine_save_locations(
    s3: helpers.s3.S3,
    type_: str,
    date_y_m_d: str,
    channel_id: str = "",
    channel_name: str = None,
    always_save: bool = False,
):
    # Determine local /tmp and remote s3 save paths according to data type.
    if type_ == "users" or type_ == "channels":
        # Users/channels calls only return realtime rather than historical information.
        # Keep only earliest available capture for each day to use as the file for the day before.
        metadata_file_path = os.path.join("json-slack", type_ + ".json")
        if not always_save and s3.check_metadata_file_exists(filename=metadata_file_path):
            # Snapshot already exists, do not update since there is one for the day, unless always_save (i.e. from export) in which case skip this check
            log.info(f"Snapshot already exists for {metadata_file_path}")
            return None, None
        local_path = os.path.join(settings.TEMPDIR, type_ + ".json")
        s3_sub_folder = "json-slack"
    elif type_ == "messages":
        channel_label = f"{channel_id}__{channel_name}" if channel_name else channel_id  # Use rsplit and get last match
        local_path = os.path.join(settings.TEMPDIR, channel_label, f"{date_y_m_d}.json")
        s3_sub_folder = os.path.join("json-slack", "messages", channel_label)
    else:
        log.info(f"archive type {type_} not implemented")
        raise NotImplementedError

    return local_path, s3_sub_folder


def archive_data(
    client_name: str,
    data,
    type_: str,
    date_y_m_d: str,
    channel_id: str = "",
    channel_name: str = None,
    always_save: bool = False,
) -> Optional[str]:
    s3 = helpers.s3.S3(client_name=client_name, date_y_m_d=date_y_m_d)

    local_path, s3_sub_folder = _determine_save_locations(
        s3=s3,
        type_=type_,
        date_y_m_d=date_y_m_d,
        channel_id=channel_id,
        channel_name=channel_name,
        always_save=always_save,
    )
    if local_path is None and s3_sub_folder is None:
        # Snapshot already exists, no need to save file.
        return None

    helpers.file_io.save_data_to_path(data, local_path)

    if type_ == "users" or type_ == "channels":  # Only archived folder for metadata
        s3_file = s3.upload_files_to_s3_archived_subfolder([local_path], s3_sub_folder)[0]
    else:  # Normal messages go into _todo and archived
        s3_file = s3.upload_files_to_s3_todo_and_archived_subfolder([local_path], s3_sub_folder)[0]

    return s3_file
