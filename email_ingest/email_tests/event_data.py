event = {
    "eventSource": "aws:ses",
    "eventVersion": "1.0",
    "ses": {
        "mail": {
            "timestamp": "2019-07-29T15:59:06.251Z",
            "source": "Info@melqart.com",
            "messageId": "1k9bqt4574vl85vhquc5ecc92fpa44tca8e8pcg1",
            "destination": ["nicolas.verle@melqart.com"],
            "headersTruncated": False,
            "headers": [
                {"name": "Return-Path", "value": "<Info@melqart.com>"},
                {
                    "name": "Received",
                    "value": "from GBR01-LO2-obe.outbound.protection.outlook.com (mail-lo2gbr01lp2058.outbound.protection.outlook.com [104.47.21.58]) by inbound-smtp.eu-west-1.amazonaws.com with SMTP id 1k9bqt4574vl85vhquc5ecc92fpa44tca8e8pcg1 for melqart@ip-sentinel.net; Mon, 29 Jul 2019 15:59:06 +0000 (UTC)",
                },
                {
                    "name": "Received-SPF",
                    "value": "softfail (spfCheck: transitioning domain of melqart.com does not designate 104.47.21.58 as permitted sender) client-ip=104.47.21.58; envelope-from=Info@melqart.com; helo=mail-lo2gbr01lp2058.outbound.protection.outlook.com;",
                },
                {
                    "name": "Authentication-Results",
                    "value": "amazonses.com; spf=softfail (spfCheck: transitioning domain of melqart.com does not designate 104.47.21.58 as permitted sender) client-ip=104.47.21.58; envelope-from=Info@melqart.com; helo=mail-lo2gbr01lp2058.outbound.protection.outlook.com; dmarc=none properties.from=octofinances.com;",
                },
                {
                    "name": "X-SES-RECEIPT",
                    "value": "AEFBQUFBQUFBQUFIZXgzQ1dVRlhHa0lQbitXMTZNR2pYV1NHR0hBWE5YS1hIY3ZHZXJqbS9JV3JZWEJHWEh6R1F4UkJaKzdQMlVsekFFbjU4WERSOFN3T0xKbG5MQ2lVQzAwbFVKM29tMWZEdDFodGRseTJhb2dCNmtIVUZ1NlZLODM3bUdobkVhZFh3c3NPdi9DVlkzY0xqUndmOFY1SjhLcUhuRkZaSFpia1YxbExlMmtSazk5RGFCUFBBU3ZQbDRzMVBGOVNxWWxXYWFFM01qL29zQ2xZbHpWNHM1MzRYZUJFYlZ5dUVRWFhuQVNORDkzbkVvcmxyL3p6WlBVc1pmSmdsRExEZmszNFRzUzhRZ1hCWDR1VTdBVGJDYjNLV09ZejBtK2JZUlBlLzJBeHBMVUxKSkE9PQ==",
                },
                {
                    "name": "X-SES-DKIM-SIGNATURE",
                    "value": "a=rsa-sha256; q=dns/txt; b=YFlE3tSIulTxuApwc7lrGJCmFAwOOL4BGVpH7DcWFwIFDmWgo2fdenOHgkVnLmu3hubwepDAv31GUpBAcmlp60R/3ZqeAWlQScSg6f/M7NeSMumrDtwiXc5TYM7dWCQFhbi1LCz2/bokGPZSH/Axfd45IJd9W8u0NqAydjfwT08=; c=relaxed/simple; s=ihchhvubuqgjsxyuhssfvqohv7z3u4hn; d=amazonses.com; t=1564415946; v=1; bh=aBZ3fswCBLEj6zTjgG3hhlZ3WlOc4QtnGR3vMV+UnzQ=; h=From:To:Cc:Bcc:Subject:Date:Message-ID:MIME-Version:Content-Type:X-SES-RECEIPT;",
                },
                {
                    "name": "Content-Type",
                    "value": 'multipart/mixed; boundary="_555955cd-697e-4592-96e0-d16176bf73cb_"',
                },
                {
                    "name": "Subject",
                    "value": "PEMEX : l'aide de l'Etat couvre globalement le déficit de FCF au S1 19",
                },
                {"name": "To", "value": "<nicolas.verle@melqart.com>"},
                {"name": "From", "value": "Octo Finances <credito@octofinances.com>"},
                {"name": "MIME-Version", "value": "1.0"},
                {
                    "name": "Sender",
                    "value": "<MicrosoftExchange329e71ec88ae4615bbc36ab6ce41109e@Melqart365.onmicrosoft.com>",
                },
                {
                    "name": "Message-ID",
                    "value": "<542dcc67-832c-42da-bcaa-5ccfb78212a7@journal.report.generator>",
                },
                {"name": "Date", "value": "Mon, 29 Jul 2019 15:59:05 +0000"},
                {"name": "X-MS-PublicTrafficType", "value": "Email"},
                {"name": "X-MS-Journal-Report", "value": ""},
                {
                    "name": "X-MS-Exchange-Parent-Message-Id",
                    "value": "<6d7628431ba5b2d813012f2114a609a3@www.privateaccessoctofinances.com>",
                },
                {"name": "Auto-Submitted", "value": "auto-generated"},
                {"name": "X-MS-Exchange-Generated-Message-Source", "value": "Journal Agent"},
                {"name": "X-MS-TrafficTypeDiagnostic", "value": "CWLP123MB1940:JournalingReport"},
                {"name": "X-LD-Processed", "value": "6fed32bf-cc6b-4b02-9c29-cc91d7807f71,ExtAddr"},
                {"name": "X-OriginatorOrg", "value": "Melqart365.onmicrosoft.com"},
                {
                    "name": "X-MS-Exchange-CrossTenant-Network-Message-Id",
                    "value": "47775571-1dd8-4f86-f1b8-08d7143daee5",
                },
                {"name": "X-MS-Exchange-Transport-CrossTenantHeadersStamped", "value": "CWLP123MB1940"},
            ],
            "commonHeaders": {
                "returnPath": "Info@melqart.com",
                "from": ["Octo Finances <credito@octofinances.com>"],
                "sender": "MicrosoftExchange329e71ec88ae4615bbc36ab6ce41109e@Melqart365.onmicrosoft.com",
                "date": "Mon, 29 Jul 2019 15:59:05 +0000",
                "to": ["nicolas.verle@melqart.com"],
                "messageId": "<542dcc67-832c-42da-bcaa-5ccfb78212a7@journal.report.generator>",
                "subject": "PEMEX : l'aide de l'Etat couvre globalement le déficit de FCF au S1 19",
            },
        },
        "receipt": {
            "timestamp": "2019-07-29T15:59:06.251Z",
            "processingTimeMillis": 380,
            "recipients": ["melqart@ip-sentinel.net"],
            "spamVerdict": {"status": "DISABLED"},
            "virusVerdict": {"status": "DISABLED"},
            "spfVerdict": {"status": "GRAY"},
            "dkimVerdict": {"status": "GRAY"},
            "dmarcVerdict": {"status": "GRAY"},
            "action": {
                "type": "Lambda",
                "functionArn": "arn:aws:lambda:eu-west-1:955323147179:function:prod-emailStep-state-machine-invoker",
                "invocationType": "Event",
            },
        },
    },
}
events = []
events.append(event)

records = {}
records["Records"] = events
