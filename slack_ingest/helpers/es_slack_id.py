""" Module to take care of adding user info, first name, last name, email to a user id.
Looks in fingerprint db (Django db) for matches, otherwise the user.json supplied (info from slack)
otherwise blank. As DB access is only available with Lambda functions return something suitable for
local testing.
"""
import logging
import ssl as ssl_lib
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

import botocore.exceptions
import certifi
import es_schema.es_slack_index as ess
import methodtools
import settings
import slack

log = logging.getLogger()


def _get_domain(email_address: str) -> str:
    return email_address.split("@")[-1].lower()


@lru_cache(maxsize=None)
def get_user_info_from_slack(slack_id: str, client_name: str) -> Optional[dict]:
    if client_name == "":
        raise Exception("Client name should not be blank")
    try:
        SLACK_API_TOKEN = settings.get_slack_api_token(client_name)
    except botocore.exceptions.ClientError as e:
        log.info(f"No Slack API Token found for client {client_name} while fetching user info: {e}")
        return None
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    slack_client = slack.WebClient(token=SLACK_API_TOKEN, ssl=ssl_context)
    try:
        response = slack_client.users_info(user=slack_id)
    except slack.errors.SlackApiError as sae:
        log.warning(sae)
        log.warning(f"{slack_id=}")
        return None
    return response["user"]


def _get_slack_id_dict_from_slack_user(sud: dict, slack_id: str) -> dict:
    if "profile" in sud and "first_name" in sud["profile"] and "last_name" in sud["profile"]:
        first_name = sud["profile"]["first_name"]
        last_name = sud["profile"]["last_name"]
    else:
        first_name = sud["real_name"]
        last_name = ""
    out = {
        "firstname": first_name,
        "lastname": last_name,
        "fullname": f"{first_name} {last_name}".strip(),
        "slackid": slack_id,
    }
    # Add check for email in case it is there
    if "profile" in sud and "email" in sud["profile"]:
        out["emailaddress"] = sud["profile"]["email"]
        out["domain"] = _get_domain(out["emailaddress"])

    return out


@dataclass
class SlackIdInnerDocCreator:
    client_name: str
    fingerprintdb_users: dict
    slack_users: dict

    def __hash__(self):  # So that methods with this as input can use lru_cache
        return hash(self.client_name + str(id(self.fingerprintdb_users)) + str(id(self.slack_users)))

    @methodtools.lru_cache(maxsize=4096)
    def get_slack_id_inner_doc(self, slack_id: str) -> ess.SlackId:
        if slack_id in self.fingerprintdb_users:
            fdb_entry = self.fingerprintdb_users[slack_id]
            out = {
                "firstname": fdb_entry["first_name"],
                "lastname": fdb_entry["last_name"],
                "fullname": f'{fdb_entry["first_name"]} {fdb_entry["last_name"]}',
                "emailaddress": fdb_entry["email"],
                "domain": _get_domain(fdb_entry["email"]),
                "companyname": fdb_entry["firm_name"],
                "slackid": slack_id,
            }
        elif slack_id in self.slack_users:
            sud = self.slack_users[slack_id]
            out = _get_slack_id_dict_from_slack_user(sud, slack_id)
        # User might be a Slack Connect user, not in slack user.list but resolvable thru users.info
        elif (user := get_user_info_from_slack(slack_id, self.client_name)) is not None:
            out = _get_slack_id_dict_from_slack_user(user, slack_id)
        else:
            out = {"slackid": slack_id, "fullname": slack_id}

        slack_id_inner_doc = ess.SlackId(**out)
        return slack_id_inner_doc
