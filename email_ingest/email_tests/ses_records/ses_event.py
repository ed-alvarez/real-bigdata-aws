from pprint import pprint


def create_event(event_recipient, event_message_id, event_subject):

    common_headers = dict()
    common_headers["returnPath"] = "JournalError@ip-sentinel.com"
    common_headers["from"] = [
        "HMRC Business Help and Support Emails <no.reply@advice.hmrc.gov.uk>",
    ]
    common_headers["sender"] = "MicrosoftExchange329e71ec88ae4615bbc36ab6ce41109e@IPSentinelLtd.onmicrosoft.com"
    common_headers["date"] = "Mon, 17 Feb 2020 12:14:50 +0000"
    common_headers["to"] = [
        "james@ip-sentinel.com",
    ]
    common_headers["messageId"] = "<c92f18b5-4df5-41e1-871c-5063b407273f@journal.report.generator>"
    common_headers["subject"] = event_subject or "Tell ABAB survey – how small businesses engage with HMRC"

    msg_headers = list()
    msg_headers = [
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
        {"name": "Subject", "value": common_headers["subject"]},
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
        {"name": "Message-ID", "value": common_headers["messageId"]},
        {"name": "Date", "value": common_headers["date"]},
        {"name": "X-MS-PublicTrafficType", "value": "Email"},
        {"name": "X-MS-Journal-Report", "value": ""},
        {"name": "X-MS-Exchange-Parent-Message-Id", "value": "<16826335.363822@advice.hmrc.gov.uk>"},
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
    ]

    mail_obj = dict()
    mail_obj["timestamp"] = "2020-02-17T12:14:51.761Z"
    mail_obj["source"] = "JournalError@ip-sentinel.com"
    mail_obj["messageId"] = event_message_id
    mail_obj["destination"] = [
        "james@ip-sentinel.com",
    ]
    mail_obj["headersTruncated"] = False
    mail_obj["headers"] = msg_headers
    mail_obj["commonHeaders"] = common_headers

    recipients = list()
    recipients.append(event_recipient)

    def create_status_obj(status):
        status_obj = dict()
        status_obj["status"] = status
        return status_obj

    action_obj = dict()
    action_obj["type"] = "Lambda"
    action_obj["functionArn"] = "arn:aws:lambda:eu-west-1:955323147179:function:prod-emailStep-state-machine-invoker"
    action_obj["invocationType"] = "Event"

    receipt_obj = dict()
    receipt_obj["timestamp"] = "2020-02-17T12:14:51.761Z"
    receipt_obj["processingTimeMillis"] = 476
    receipt_obj["recipients"] = recipients
    receipt_obj["spamVerdict"] = create_status_obj("DISABLED")
    receipt_obj["virusVerdict"] = create_status_obj("DISABLED")
    receipt_obj["spfVerdict"] = create_status_obj("PROCESSING_FAILED")
    receipt_obj["dkimVerdict"] = create_status_obj("GRAY")
    receipt_obj["dmarcVerdict"] = create_status_obj("FAIL")
    receipt_obj["action"] = action_obj
    receipt_obj["dmarcPolicy"] = "reject"

    ses_obj = dict()
    ses_obj["mail"] = mail_obj
    ses_obj["receipt"] = receipt_obj

    event_obj = dict()
    event_obj["eventSource"] = "aws:ses"
    event_obj["eventVersion"] = "1.0"
    event_obj["ses"] = ses_obj

    records_obj = list()
    records_obj.append(event_obj)

    records = dict()
    records["Records"] = records_obj

    return records


if __name__ == "__main__":
    event = create_event("ips.ips", "whatsapp/o255h8fqv9jo21q8ug959sqebqvv46fgqqgj23o1")
    pprint(event)
