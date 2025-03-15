from pprint import pprint


def create_event(event_bucket, event_key, move_files=False):
    record = dict()
    record["bucket"] = event_bucket
    record["key"] = event_key
    if move_files:
        record["move_files"] = True

    Records = list()
    Records.append(record)

    event = dict()
    event["Records"] = Records

    return event


if __name__ == "__main__":
    event = create_event("ips.ips", "whatsapp/o255h8fqv9jo21q8ug959sqebqvv46fgqqgj23o1")
    pprint(event)
