user_list = {
    "ok": True,
    "members": [
        {
            "id": "W012A3CDE",
            "team_id": "T012AB3C4",
            "name": "spengler",
            "deleted": False,
            "color": "9f69e7",
            "real_name": "spengler",
            "tz": "America/Los_Angeles",
            "tz_label": "Pacific Daylight Time",
            "tz_offset": -25200,
            "profile": {
                "avatar_hash": "ge3b51ca72de",
                "status_text": "Print is dead",
                "status_emoji": ":books:",
                "real_name": "Egon Spengler",
                "display_name": "spengler",
                "real_name_normalized": "Egon Spengler",
                "display_name_normalized": "spengler",
                "email": "spengler@ghostbusters.example.com",
                "image_24": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_32": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_48": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_72": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_192": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "image_512": "https://.../avatar/e3b51ca72dee4ef87916ae2b9240df50.jpg",
                "team": "T012AB3C4",
            },
            "is_admin": True,
            "is_owner": False,
            "is_primary_owner": False,
            "is_restricted": False,
            "is_ultra_restricted": False,
            "is_bot": False,
            "updated": 1502138686,
            "is_app_user": False,
            "has_2fa": False,
        },
        {
            "id": "W07QCRPA4",
            "team_id": "T0G9PQBBK",
            "name": "glinda",
            "deleted": False,
            "color": "9f69e7",
            "real_name": "Glinda Southgood",
            "tz": "America/Los_Angeles",
            "tz_label": "Pacific Daylight Time",
            "tz_offset": -25200,
            "profile": {
                "avatar_hash": "8fbdd10b41c6",
                "image_24": "https://a.slack-edge.com...png",
                "image_32": "https://a.slack-edge.com...png",
                "image_48": "https://a.slack-edge.com...png",
                "image_72": "https://a.slack-edge.com...png",
                "image_192": "https://a.slack-edge.com...png",
                "image_512": "https://a.slack-edge.com...png",
                "image_1024": "https://a.slack-edge.com...png",
                "image_original": "https://a.slack-edge.com...png",
                "first_name": "Glinda",
                "last_name": "Southgood",
                "title": "Glinda the Good",
                "phone": "",
                "skype": "",
                "real_name": "Glinda Southgood",
                "real_name_normalized": "Glinda Southgood",
                "display_name": "Glinda the Fairly Good",
                "display_name_normalized": "Glinda the Fairly Good",
                "email": "glenda@south.oz.coven",
            },
            "is_admin": True,
            "is_owner": False,
            "is_primary_owner": False,
            "is_restricted": False,
            "is_ultra_restricted": False,
            "is_bot": False,
            "updated": 1480527098,
            "has_2fa": False,
        },
    ],
    "cache_ts": 1498777272,
    "response_metadata": {"next_cursor": "dXNlcjpVMEc5V0ZYTlo="},
}


class conv_history:
    def __init__(self, data):
        self.data = data


conv_1 = {
    "ok": True,
    "messages": [
        {
            "type": "message",
            "user": "U012AB3CDE",
            "text": "I find you punny and would like to smell your nose letter",
            "ts": "1512085950.000216",
        },
        {
            "type": "message",
            "user": "U061F7AUR",
            "text": "What, you want to smell my shoes better?",
            "ts": "1512104434.000490",
        },
    ],
    "has_more": True,
    "pin_count": 0,
    "response_metadata": {"next_cursor": "bmV4dF90czoxNTEyMDg1ODYxMDAwNTQz"},
}
conv_2 = {
    "ok": True,
    "messages": [
        {
            "type": "message",
            "user": "U012AB3CDE",
            "text": "SET 2 - I find you punny and would like to smell your nose letter",
            "ts": "1512085950.000216",
        },
        {
            "type": "message",
            "user": "U061F7AUR",
            "text": "SET 2 - What, you want to smell my shoes better?",
            "ts": "1512104434.000490",
        },
    ],
    "has_more": False,
    "pin_count": 0,
    "response_metadata": {"next_cursor": "bmV4dF90czoxNTEyMDg1ODYxMDAwNTQz"},
}

convItem1 = conv_history(data=conv_1)
convItem2 = conv_history(data=conv_2)

conversations_history = [convItem1, convItem2]
