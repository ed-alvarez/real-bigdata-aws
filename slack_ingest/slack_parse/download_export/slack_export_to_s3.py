import json
import logging
import os
import zipfile
from datetime import datetime
from typing import Optional, Tuple

import slack_parse.ingest_helpers.slack_download_common as dl_common

log = logging.getLogger()


def to_s3(client_name: str, date_y_m_d: str, export_local_path: str) -> dict:

    # Extract end date to determine where to save the metadata (channels and users) files
    filename = os.path.basename(export_local_path)
    dates = filename.replace(".zip", "").split("-")  # Special char
    end_date_str = dates[1].strip()
    end_date = datetime.strptime(end_date_str, "%b %d %Y")
    end_date_y_m_d = end_date.strftime("%Y-%m-%d")

    channels, channels_s3_path, _, users_s3_path = save_metadata_to_s3(client_name, end_date_y_m_d, export_local_path)
    results = save_to_s3(client_name, date_y_m_d, export_local_path, channels)
    results["channels"] = channels_s3_path
    results["users"] = users_s3_path
    return results


def save_metadata_to_s3(
    client_name: str, meta_date_y_m_d: str, export_local_path: str
) -> Tuple[list, Optional[str], list, Optional[str]]:
    """Collect channels and chats into one channels_all object and archive them as "channels".
        Enterprise Grid exports have a different internal folder structure to Plus exports, users.json is in a subfolder.
    Public only exports only contain channels.json no dms.json etc."""

    zf = zipfile.ZipFile(export_local_path)
    channels = []
    dms = []
    groups = []
    mpims = []
    users = []

    for f in zf.namelist():
        if f.endswith("channels.json"):
            channels.extend(json.loads(zf.read(f)))
        elif f.endswith("dms.json"):
            dms.extend(json.loads(zf.read(f)))
        elif f.endswith("groups.json"):
            groups.extend(json.loads(zf.read(f)))
        elif f.endswith("mpims.json"):
            mpims.extend(json.loads(zf.read(f)))
        elif f.endswith("users.json") and not f.endswith("org_users.json"):
            users.extend(json.loads(zf.read(f)))

    channels_all = channels + dms + groups + mpims

    channels_s3_path = dl_common.archive_data(
        client_name,
        data=channels_all,
        type_="channels",
        date_y_m_d=meta_date_y_m_d,
        always_save=True,
    )
    users_s3_path = dl_common.archive_data(
        client_name,
        data=users,
        type_="users",
        date_y_m_d=meta_date_y_m_d,
        always_save=True,
    )
    zf.close()
    return channels_all, channels_s3_path, users, users_s3_path


def _identify_channel(channel_identifier: str, channels_by_name: dict) -> Tuple[str, str]:
    # Channels, Groups, mpims are stored by name in the export.zip, DMs by id
    if channel_identifier in channels_by_name:
        channel_id = channels_by_name[channel_identifier]["id"]
        channel_name = channel_identifier
    else:
        channel_id = channel_identifier
        channel_name = ""
    return channel_id, channel_name


def save_to_s3(client_name: str, date_y_m_d: str, export_local_path: str, channels_data: list) -> dict:
    zf = zipfile.ZipFile(export_local_path)
    results: dict = {
        "client_name": client_name,
        "date_y_m_d": date_y_m_d,
        "messages_s3_paths": [],
    }
    # Slack_data saves by id rather than name, so look this up in channels_data
    channels_by_name = {c["name"]: c for c in channels_data if "name" in c}  # DMs don't have names, only ids
    # Go through zip and find channels with chats for this date in
    mask = f"{date_y_m_d}.json"
    for name in zf.namelist():
        if name.endswith(mask):
            messages = json.loads(zf.read(name))
            channel_identifier = name.split("/")[-2]
            channel_id, channel_name = _identify_channel(channel_identifier, channels_by_name)
            this_s3_path = dl_common.archive_data(
                client_name,
                data=messages,
                type_="messages",
                channel_id=channel_id,
                channel_name=channel_name,
                date_y_m_d=date_y_m_d,
            )
            results["messages_s3_paths"].append(this_s3_path)
    zf.close()
    return results
