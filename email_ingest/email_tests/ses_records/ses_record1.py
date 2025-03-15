aws_data_1 = dict()
aws_data_2 = dict()
aws_data_complex_meeting = dict()
aws_data_1["Records"] = [
    {
        "eventSource": "aws:ses",
        "eventVersion": "1.0",
        "ses": {
            "mail": {
                "timestamp": "2020-02-17T12:14:51.761Z",
                "source": "JournalError@ip-sentinel.com",
                "messageId": "7k822gft4kqtq4dgji1sqdhnqgqnj9bsv76lqoo1",
                "destination": ["james@ip-sentinel.com"],
                "headersTruncated": False,
                "headers": [
                    {"name": "Return-Path", "value": "<JournalError@ip-sentinel.com>"},
                    {
                        "name": "Received",
                        "value": "from EUR01-HE1-obe.outbound.protection.outlook.com (mail-he1eur01lp2053.outbound.protection.outlook.com [104.47.0.53]) by inbound-smtp.eu-west-1.amazonaws.com with SMTP id 7k822gft4kqtq4dgji1sqdhnqgqnj9bsv76lqoo1 for ips@ip-sentinel.net; Mon, 17 Feb 2020 12:14:51 +0000 (UTC)",
                    },
                    {
                        "name": "Received-SPF",
                        "value": "permerror (spfCheck: Error in processing SPF Record) client-ip=104.47.0.53; envelope-from=JournalError@ip-sentinel.com; helo=mail-he1eur01lp2053.outbound.protection.outlook.com;",
                    },
                    {
                        "name": "Authentication-Results",
                        "value": "amazonses.com; spf=permerror (spfCheck: Error in processing SPF Record) client-ip=104.47.0.53; envelope-from=JournalError@ip-sentinel.com; helo=mail-he1eur01lp2053.outbound.protection.outlook.com; dmarc=fail header.from=advice.hmrc.gov.uk;",
                    },
                    {
                        "name": "X-SES-RECEIPT",
                        "value": "AEFBQUFBQUFBQUFGamRKeHJ1dGlqRlhRRFM3eEZkanppWlFYNzdZUkt5eG5oUjY2dXZKanIzNWNlZFFtb0krVE5hZWI3L2J1QXMrT0Z5Uzd5L2s2TjBMblo0VnZ1cFczckRmd01OYWN3VTN1bGo0U0wybWF1VGlIUlJzMkJneE9Lb0p3QTd5emliQUtkZ3l5VDdzQTlxZGtHd2ZhTFpob0d2WU1tMTFydnd1UHlsVERYeU1TcGlZc0w4RmF6OVcrViswY3dza0hZWndoWFFCT0tIMGxSemN2OC9wWDc4L1pyUUVLOFRjOGZ4Yk00V3FINjYyd3lkb3FDNmlFbVRUNmUzNXRlWlFTMm5qRUR6ZHBmWXdmNWlkQW42TEM1Z2VpWE5rdnp1V1gyQUdNRmIyV2ZSYkp6OWI4d0ZqKzEvckFWTjBzM2JSbE9Fdms9",
                    },
                    {
                        "name": "X-SES-DKIM-SIGNATURE",
                        "value": "a=rsa-sha256; q=dns/txt; b=KB6s/8d1G7io+H5Bkzt9ZRyjiKopygB25cRbfZt9jGzD5eCP0TE+g9ee5e1Y7KTEsiXlCL9Ly5STHNw44qVrr/vuyDJfKWDGVL3d9Rgv93hPpMjbucmcASHLHyVZmLi1YviwS9uxlErHJX+Q6j0+dBN+wi8fyPD50YGLCN+lbM8=; c=relaxed/simple; s=ihchhvubuqgjsxyuhssfvqohv7z3u4hn; d=amazonses.com; t=1581941692; v=1; bh=+VcVTMOCwLPtv3tnafbZ1vd6MTQng0tzEQeJhn29UCk=; h=From:To:Cc:Bcc:Subject:Date:Message-ID:MIME-Version:Content-Type:X-SES-RECEIPT;",
                    },
                    {
                        "name": "Content-Type",
                        "value": 'multipart/mixed; boundary="_ba735b42-46a6-4a6d-91dc-75014d02dfc0_"',
                    },
                    {"name": "Subject", "value": "Tell ABAB survey – how small businesses engage with HMRC"},
                    {"name": "To", "value": "james@ip-sentinel.com"},
                    {
                        "name": "From",
                        "value": '"=?US-ASCII?Q?HMRC_Business_Help_and_Support_Emails?=" <no.reply@advice.hmrc.gov.uk>',
                    },
                    {"name": "MIME-Version", "value": "1.0"},
                    {
                        "name": "Sender",
                        "value": "<MicrosoftExchange329e71ec88ae4615bbc36ab6ce41109e@IPSentinelLtd.onmicrosoft.com>",
                    },
                    {
                        "name": "Message-ID",
                        "value": "<c92f18b5-4df5-41e1-871c-5063b407273f@journal.report.generator>",
                    },
                    {"name": "Date", "value": "Mon, 17 Feb 2020 12:14:50 +0000"},
                    {"name": "X-MS-PublicTrafficType", "value": "Email"},
                    {"name": "X-MS-Journal-Report", "value": ""},
                    {
                        "name": "X-MS-Exchange-Parent-Message-Id",
                        "value": "<16826335.363822@advice.hmrc.gov.uk>",
                    },
                    {"name": "Auto-Submitted", "value": "auto-generated"},
                    {"name": "X-MS-Exchange-Generated-Message-Source", "value": "Journal Agent"},
                    {"name": "X-MS-TrafficTypeDiagnostic", "value": "PR3PR10MB3914:JournalingReport"},
                    {"name": "X-LD-Processed", "value": "a38e65be-fb2c-4ab0-9084-199607af9f21,ExtAddr"},
                    {"name": "X-OriginatorOrg", "value": "IPSentinelLtd.onmicrosoft.com"},
                    {
                        "name": "X-MS-Exchange-CrossTenant-Network-Message-Id",
                        "value": "44218cb8-217d-4ec7-b41b-08d7b3a2fd0f",
                    },
                    {"name": "X-MS-Exchange-CrossTenant-FromEntityHeader", "value": "Hosted"},
                    {"name": "X-MS-Exchange-Transport-CrossTenantHeadersStamped", "value": "PR3PR10MB3914"},
                ],
                "commonHeaders": {
                    "returnPath": "JournalError@ip-sentinel.com",
                    "from": ["HMRC Business Help and Support Emails <no.reply@advice.hmrc.gov.uk>"],
                    "sender": "MicrosoftExchange329e71ec88ae4615bbc36ab6ce41109e@IPSentinelLtd.onmicrosoft.com",
                    "date": "Mon, 17 Feb 2020 12:14:50 +0000",
                    "to": ["james@ip-sentinel.com"],
                    "messageId": "<c92f18b5-4df5-41e1-871c-5063b407273f@journal.report.generator>",
                    "subject": "Tell ABAB survey – how small businesses engage with HMRC",
                },
            },
            "receipt": {
                "timestamp": "2020-02-17T12:14:51.761Z",
                "processingTimeMillis": 476,
                "recipients": ["ips@ip-sentinel.net"],
                "spamVerdict": {"status": "DISABLED"},
                "virusVerdict": {"status": "DISABLED"},
                "spfVerdict": {"status": "PROCESSING_FAILED"},
                "dkimVerdict": {"status": "GRAY"},
                "dmarcVerdict": {"status": "FAIL"},
                "action": {
                    "type": "Lambda",
                    "functionArn": "arn:aws:lambda:eu-west-1:955323147179:function:prod-emailStep-state-machine-invoker",
                    "invocationType": "Event",
                },
                "dmarcPolicy": "reject",
            },
        },
    }
]
aws_data_2["Records"] = [
    {
        "eventSource": "aws:ses",
        "eventVersion": "1.0",
        "ses": {
            "mail": {
                "timestamp": "2020-02-17T14:05:28.527Z",
                "source": "JournalFail@mirabella.uk",
                "messageId": "irnjt42kcq086s1rqcvpvpbpcq3sm5tbc5lvnh81",
                "destination": [
                    "ryanf@mirabella.co.uk",
                    "dominicw@mirabella.co.uk",
                    "jonathanm@mirabella.co.uk",
                    "stevans@mirabella.co.uk",
                    "mltrisk@mirabella.co.uk",
                    "GRCOperations@mirabella.co.uk",
                ],
                "headersTruncated": False,
                "headers": [
                    {"name": "Return-Path", "value": "<JournalFail@mirabella.uk>"},
                    {
                        "name": "Received",
                        "value": "from EUR05-VI1-obe.outbound.protection.outlook.com (mail-vi1eur05lp2176.outbound.protection.outlook.com [104.47.17.176]) by inbound-smtp.eu-west-1.amazonaws.com with SMTP id irnjt42kcq086s1rqcvpvpbpcq3sm5tbc5lvnh81 for mirabella@ip-sentinel.net; Mon, 17 Feb 2020 14:05:28 +0000 (UTC)",
                    },
                    {
                        "name": "Received-SPF",
                        "value": "pass (spfCheck: domain of mirabella.uk designates 104.47.17.176 as permitted sender) client-ip=104.47.17.176; envelope-from=JournalFail@mirabella.uk; helo=mail-vi1eur05lp2176.outbound.protection.outlook.com;",
                    },
                    {
                        "name": "Authentication-Results",
                        "value": "amazonses.com; spf=pass (spfCheck: domain of mirabella.uk designates 104.47.17.176 as permitted sender) client-ip=104.47.17.176; envelope-from=JournalFail@mirabella.uk; helo=mail-vi1eur05lp2176.outbound.protection.outlook.com; dmarc=fail header.from=mirabella.co.uk;",
                    },
                    {
                        "name": "X-SES-RECEIPT",
                        "value": "AEFBQUFBQUFBQUFHeFJCN3N1M2FZVmJYVTg2eFhubVBIbmVZa1NuRGcxR2ZuM1o3eXNNaTlmdGJjWEtDeWcvZGNQNDNuK1ZiZy83TDhvVVVwMHR2WEpPUis0UXAzWkpqRm9MWU12NjhKSVdwSjk0bnRXUUo1Wkl1emZvSjAxc2RpeVI3N29tYTFnUU05ZXQvM082NVdTZVV6bXZmd3pNN1pFT0dBWFRZUzZpRGhOM2VBMmROc0I5b2FuTUMxaDRyYnA5Y2RvQjYvUnJRTEtCRnptQjZKSFdMTWF4dXV1TW9ZbWNDNXExdEwzenlFa1AzR0Q2ZFVFUjVLOVhwQ2xVekhaRjRuSFVDbHhuWEZvOEgrL29hSnIrNUZhTDlraWIrMHRKSnJ0T3FUclIrb1VoRE9wZ2JZbVA3eDRrdU9RSXd0aVdabXl1cllUd0k9",
                    },
                    {
                        "name": "X-SES-DKIM-SIGNATURE",
                        "value": "a=rsa-sha256; q=dns/txt; b=UIMbfnOBnoegqqkLvVS8lJoxppq1kJ+xl7iSUzPDLD53/oiG8jZpXR/bFKNC7Ra+SXDVbW4ZrwKdkPs4bM/u5/QbtmxCNuLWZzC+KRRe5TRQLyOfJaunczwLyKl/zsdUwHU/5fdmZbz8EJgDW92ivdA+Yf8XZmaDLP1c7+RklFM=; c=relaxed/simple; s=ihchhvubuqgjsxyuhssfvqohv7z3u4hn; d=amazonses.com; t=1581948328; v=1; bh=FalWKBjUOmQrHatIBdWt85m5H2i0ZQiil1EXzXqSZTQ=; h=From:To:Cc:Bcc:Subject:Date:Message-ID:MIME-Version:Content-Type:X-SES-RECEIPT;",
                    },
                    {
                        "name": "Content-Type",
                        "value": 'multipart/mixed; boundary="_058b0004-4d72-41e8-ac0b-76b56427fc63_"',
                    },
                    {
                        "name": "Subject",
                        "value": "RE: SSR Summary cob 14-02-2020 ***Two Positions to Report to AMF and One to FCA - France & UK***",
                    },
                    {
                        "name": "CC",
                        "value": "Stevan Simic <stevans@mirabella.co.uk>, MLT-Risk <mltrisk@mirabella.co.uk>, GRC Operations Team <GRCOperations@mirabella.co.uk>",
                    },
                    {
                        "name": "To",
                        "value": "Ryan Farrugia <ryanf@mirabella.co.uk>, Dominic Williams <dominicw@mirabella.co.uk>, Jonathan Mott <jonathanm@mirabella.co.uk>",
                    },
                    {"name": "From", "value": "Angelo Girardi <angelog@mirabella.co.uk>"},
                    {
                        "name": "Sender",
                        "value": "<MicrosoftExchange329e71ec88ae4615bbc36ab6ce41109e@mirabella.onmicrosoft.com>",
                    },
                    {
                        "name": "Message-ID",
                        "value": "<c3ded70b-e486-4ff8-9777-1d5ab89141ee@journal.report.generator>",
                    },
                    {"name": "Date", "value": "Mon, 17 Feb 2020 14:05:27 +0000"},
                    {"name": "X-MS-PublicTrafficType", "value": "Email"},
                    {"name": "X-MS-Journal-Report", "value": ""},
                    {
                        "name": "X-MS-Exchange-Parent-Message-Id",
                        "value": "<AM6PR08MB322494813EE9B9EAB0F03B4FF0160@AM6PR08MB3224.eurprd08.prod.outlook.com>",
                    },
                    {"name": "Auto-Submitted", "value": "auto-generated"},
                    {"name": "X-MS-Exchange-Generated-Message-Source", "value": "Journal Agent"},
                    {"name": "X-MS-TrafficTypeDiagnostic", "value": "AM6PR08MB3639:JournalingReport"},
                    {"name": "X-LD-Processed", "value": "2e3cadcd-0cf8-419d-86a0-e17d7f408117,ExtAddr"},
                    {"name": "X-MS-Exchange-Transport-Forked", "value": "True"},
                    {"name": "Keywords", "value": ""},
                    {"name": "MIME-Version", "value": "1.0"},
                    {"name": "X-OriginatorOrg", "value": "mirabella.onmicrosoft.com"},
                    {
                        "name": "X-MS-Exchange-CrossTenant-Network-Message-Id",
                        "value": "a64b124b-568b-441e-2220-08d7b3b2710c",
                    },
                    {"name": "X-MS-Exchange-CrossTenant-FromEntityHeader", "value": "Hosted"},
                    {"name": "X-MS-Exchange-Transport-CrossTenantHeadersStamped", "value": "AM6PR08MB3639"},
                ],
                "commonHeaders": {
                    "returnPath": "JournalFail@mirabella.uk",
                    "from": ["Angelo Girardi <angelog@mirabella.co.uk>"],
                    "sender": "MicrosoftExchange329e71ec88ae4615bbc36ab6ce41109e@mirabella.onmicrosoft.com",
                    "date": "Mon, 17 Feb 2020 14:05:27 +0000",
                    "to": [
                        "Ryan Farrugia <ryanf@mirabella.co.uk>",
                        "Dominic Williams <dominicw@mirabella.co.uk>",
                        "Jonathan Mott <jonathanm@mirabella.co.uk>",
                    ],
                    "cc": [
                        "Stevan Simic <stevans@mirabella.co.uk>",
                        "MLT-Risk <mltrisk@mirabella.co.uk>",
                        "GRC Operations Team <GRCOperations@mirabella.co.uk>",
                    ],
                    "messageId": "<c3ded70b-e486-4ff8-9777-1d5ab89141ee@journal.report.generator>",
                    "subject": "RE: SSR Summary cob 14-02-2020 ***Two Positions to Report to AMF and One to FCA - France & UK***",
                },
            },
            "receipt": {
                "timestamp": "2020-02-17T14:05:28.527Z",
                "processingTimeMillis": 484,
                "recipients": ["mirabella@ip-sentinel.net"],
                "spamVerdict": {"status": "DISABLED"},
                "virusVerdict": {"status": "DISABLED"},
                "spfVerdict": {"status": "PASS"},
                "dkimVerdict": {"status": "GRAY"},
                "dmarcVerdict": {"status": "FAIL"},
                "action": {
                    "type": "Lambda",
                    "functionArn": "arn:aws:lambda:eu-west-1:955323147179:function:prod-emailStep-state-machine-invoker",
                    "invocationType": "Event",
                },
                "dmarcPolicy": "none",
            },
        },
    }
]
aws_data_complex_meeting["Records"] = [
    {
        "eventSource": "aws:ses",
        "eventVersion": "1.0",
        "ses": {
            "mail": {
                "timestamp": "2020-02-17T14:05:28.527Z",
                "source": "JournalFail@mirabella.uk",
                "messageId": "complex_meetingrqcvpvpbpcq3sm5tbc5lvnh81",
                "destination": [
                    "ryanf@mirabella.co.uk",
                    "dominicw@mirabella.co.uk",
                    "jonathanm@mirabella.co.uk",
                    "stevans@mirabella.co.uk",
                    "mltrisk@mirabella.co.uk",
                    "GRCOperations@mirabella.co.uk",
                ],
                "headersTruncated": False,
                "headers": [
                    {"name": "Return-Path", "value": "<JournalFail@mirabella.uk>"},
                    {
                        "name": "Received",
                        "value": "from EUR05-VI1-obe.outbound.protection.outlook.com (mail-vi1eur05lp2176.outbound.protection.outlook.com [104.47.17.176]) by inbound-smtp.eu-west-1.amazonaws.com with SMTP id irnjt42kcq086s1rqcvpvpbpcq3sm5tbc5lvnh81 for mirabella@ip-sentinel.net; Mon, 17 Feb 2020 14:05:28 +0000 (UTC)",
                    },
                    {
                        "name": "Received-SPF",
                        "value": "pass (spfCheck: domain of mirabella.uk designates 104.47.17.176 as permitted sender) client-ip=104.47.17.176; envelope-from=JournalFail@mirabella.uk; helo=mail-vi1eur05lp2176.outbound.protection.outlook.com;",
                    },
                    {
                        "name": "Authentication-Results",
                        "value": "amazonses.com; spf=pass (spfCheck: domain of mirabella.uk designates 104.47.17.176 as permitted sender) client-ip=104.47.17.176; envelope-from=JournalFail@mirabella.uk; helo=mail-vi1eur05lp2176.outbound.protection.outlook.com; dmarc=fail header.from=mirabella.co.uk;",
                    },
                    {
                        "name": "X-SES-RECEIPT",
                        "value": "AEFBQUFBQUFBQUFHeFJCN3N1M2FZVmJYVTg2eFhubVBIbmVZa1NuRGcxR2ZuM1o3eXNNaTlmdGJjWEtDeWcvZGNQNDNuK1ZiZy83TDhvVVVwMHR2WEpPUis0UXAzWkpqRm9MWU12NjhKSVdwSjk0bnRXUUo1Wkl1emZvSjAxc2RpeVI3N29tYTFnUU05ZXQvM082NVdTZVV6bXZmd3pNN1pFT0dBWFRZUzZpRGhOM2VBMmROc0I5b2FuTUMxaDRyYnA5Y2RvQjYvUnJRTEtCRnptQjZKSFdMTWF4dXV1TW9ZbWNDNXExdEwzenlFa1AzR0Q2ZFVFUjVLOVhwQ2xVekhaRjRuSFVDbHhuWEZvOEgrL29hSnIrNUZhTDlraWIrMHRKSnJ0T3FUclIrb1VoRE9wZ2JZbVA3eDRrdU9RSXd0aVdabXl1cllUd0k9",
                    },
                    {
                        "name": "X-SES-DKIM-SIGNATURE",
                        "value": "a=rsa-sha256; q=dns/txt; b=UIMbfnOBnoegqqkLvVS8lJoxppq1kJ+xl7iSUzPDLD53/oiG8jZpXR/bFKNC7Ra+SXDVbW4ZrwKdkPs4bM/u5/QbtmxCNuLWZzC+KRRe5TRQLyOfJaunczwLyKl/zsdUwHU/5fdmZbz8EJgDW92ivdA+Yf8XZmaDLP1c7+RklFM=; c=relaxed/simple; s=ihchhvubuqgjsxyuhssfvqohv7z3u4hn; d=amazonses.com; t=1581948328; v=1; bh=FalWKBjUOmQrHatIBdWt85m5H2i0ZQiil1EXzXqSZTQ=; h=From:To:Cc:Bcc:Subject:Date:Message-ID:MIME-Version:Content-Type:X-SES-RECEIPT;",
                    },
                    {
                        "name": "Content-Type",
                        "value": 'multipart/mixed; boundary="_058b0004-4d72-41e8-ac0b-76b56427fc63_"',
                    },
                    {
                        "name": "Subject",
                        "value": "RE: SSR Summary cob 14-02-2020 ***Two Positions to Report to AMF and One to FCA - France & UK***",
                    },
                    {
                        "name": "CC",
                        "value": "Stevan Simic <stevans@mirabella.co.uk>, MLT-Risk <mltrisk@mirabella.co.uk>, GRC Operations Team <GRCOperations@mirabella.co.uk>",
                    },
                    {
                        "name": "To",
                        "value": "Ryan Farrugia <ryanf@mirabella.co.uk>, Dominic Williams <dominicw@mirabella.co.uk>, Jonathan Mott <jonathanm@mirabella.co.uk>",
                    },
                    {"name": "From", "value": "Angelo Girardi <angelog@mirabella.co.uk>"},
                    {
                        "name": "Sender",
                        "value": "<MicrosoftExchange329e71ec88ae4615bbc36ab6ce41109e@mirabella.onmicrosoft.com>",
                    },
                    {
                        "name": "Message-ID",
                        "value": "<c3ded70b-e486-4ff8-9777-1d5ab89141ee@journal.report.generator>",
                    },
                    {"name": "Date", "value": "Mon, 17 Feb 2020 14:05:27 +0000"},
                    {"name": "X-MS-PublicTrafficType", "value": "Email"},
                    {"name": "X-MS-Journal-Report", "value": ""},
                    {
                        "name": "X-MS-Exchange-Parent-Message-Id",
                        "value": "<AM6PR08MB322494813EE9B9EAB0F03B4FF0160@AM6PR08MB3224.eurprd08.prod.outlook.com>",
                    },
                    {"name": "Auto-Submitted", "value": "auto-generated"},
                    {"name": "X-MS-Exchange-Generated-Message-Source", "value": "Journal Agent"},
                    {"name": "X-MS-TrafficTypeDiagnostic", "value": "AM6PR08MB3639:JournalingReport"},
                    {"name": "X-LD-Processed", "value": "2e3cadcd-0cf8-419d-86a0-e17d7f408117,ExtAddr"},
                    {"name": "X-MS-Exchange-Transport-Forked", "value": "True"},
                    {"name": "Keywords", "value": ""},
                    {"name": "MIME-Version", "value": "1.0"},
                    {"name": "X-OriginatorOrg", "value": "mirabella.onmicrosoft.com"},
                    {
                        "name": "X-MS-Exchange-CrossTenant-Network-Message-Id",
                        "value": "a64b124b-568b-441e-2220-08d7b3b2710c",
                    },
                    {"name": "X-MS-Exchange-CrossTenant-FromEntityHeader", "value": "Hosted"},
                    {"name": "X-MS-Exchange-Transport-CrossTenantHeadersStamped", "value": "AM6PR08MB3639"},
                ],
                "commonHeaders": {
                    "returnPath": "JournalFail@mirabella.uk",
                    "from": ["Angelo Girardi <angelog@mirabella.co.uk>"],
                    "sender": "MicrosoftExchange329e71ec88ae4615bbc36ab6ce41109e@mirabella.onmicrosoft.com",
                    "date": "Mon, 17 Feb 2020 14:05:27 +0000",
                    "to": [
                        "Ryan Farrugia <ryanf@mirabella.co.uk>",
                        "Dominic Williams <dominicw@mirabella.co.uk>",
                        "Jonathan Mott <jonathanm@mirabella.co.uk>",
                    ],
                    "cc": [
                        "Stevan Simic <stevans@mirabella.co.uk>",
                        "MLT-Risk <mltrisk@mirabella.co.uk>",
                        "GRC Operations Team <GRCOperations@mirabella.co.uk>",
                    ],
                    "messageId": "<c3ded70b-e486-4ff8-9777-1d5ab89141ee@journal.report.generator>",
                    "subject": "RE: SSR Summary cob 14-02-2020 ***Two Positions to Report to AMF and One to FCA - France & UK***",
                },
            },
            "receipt": {
                "timestamp": "2020-02-17T14:05:28.527Z",
                "processingTimeMillis": 484,
                "recipients": ["test@ip-sentinel.net"],
                "spamVerdict": {"status": "DISABLED"},
                "virusVerdict": {"status": "DISABLED"},
                "spfVerdict": {"status": "PASS"},
                "dkimVerdict": {"status": "GRAY"},
                "dmarcVerdict": {"status": "FAIL"},
                "action": {
                    "type": "Lambda",
                    "functionArn": "arn:aws:lambda:eu-west-1:955323147179:function:prod-emailStep-state-machine-invoker",
                    "invocationType": "Event",
                },
                "dmarcPolicy": "none",
            },
        },
    }
]
