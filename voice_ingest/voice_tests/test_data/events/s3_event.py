from pprint import pprint


def create_event(event_bucket, event_key, event_etag=None) -> dict:

    object = dict()
    object["key"] = event_key
    object["size"] = 1305107
    if event_etag:
        object["eTag"] = event_etag
    else:
        object["eTag"] = "b21b84d653bb07b05b1e6b33684dc11b"
    object["sequencer"] = "0C0F6F405D6ED209E1"

    ownerIdentity = dict()
    ownerIdentity["principalId"] = "A3I5XTEXAMAI3E"

    bucket = dict()
    bucket["name"] = event_bucket
    bucket["ownerIdentity"] = ownerIdentity
    bucket["arn"] = "arn:aws:s3:::" + event_bucket

    s3 = dict()
    s3["s3SchemaVersion"] = "1.0"
    s3["configurationId"] = "828aa6fc-f7b5-4305-8584-487c791949c1"
    s3["bucket"] = bucket
    s3["object"] = object

    responseElements = dict()
    responseElements["x-amz-request-id"] = "D82B88E5F771F645"
    responseElements["x-amz-id-2"] = "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo="

    requestParameters = dict()
    requestParameters["sourceIPAddress"] = "205.255.255.255"

    userIdentity = dict()
    userIdentity["principalId"] = "AWS:AIDAINPONIXQXHT3IKHL2"

    record = dict()
    record["eventVersion"] = "2.1"
    record["eventSource"] = "aws:s3"
    record["awsRegion"] = "us-east-2"
    record["eventTime"] = "2019-09-03T19:37:27.192Z"
    record["eventName"] = "ObjectCreated:Put"
    record["userIdentity"] = userIdentity
    record["requestParameters"] = requestParameters
    record["responseElements"] = responseElements
    record["s3"] = s3

    Records = list()
    Records.append(record)

    event = dict()
    event["Records"] = Records

    return event


if __name__ == "__main__":
    event = create_event("ips.ips", "whatsapp/o255h8fqv9jo21q8ug959sqebqvv46fgqqgj23o1", "ad5e55fcc6ac49325e16af52ea63ef7f")
    pprint(event)

    """{'Records': [{'awsRegion': 'us-east-2',
              'eventName': 'ObjectCreated:Put',
              'eventSource': 'aws:s3',
              'eventTime': '2019-09-03T19:37:27.192Z',
              'eventVersion': '2.1',
              'requestParameters': {'sourceIPAddress': '205.255.255.255'},
              'responseElements': {'x-amz-id-2': 'vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo=',
                                   'x-amz-request-id': 'D82B88E5F771F645'},
              's3': {'bucket': {'arn': 'arn:aws:s3:::ips.ips',
                                'name': 'ips.ips',
                                'ownerIdentity': {'principalId': 'A3I5XTEXAMAI3E'}},
                     'configurationId': '828aa6fc-f7b5-4305-8584-487c791949c1',
                     'object': {'eTag': 'ad5e55fcc6ac49325e16af52ea63ef7f',
                                'key': 'whatsapp/o255h8fqv9jo21q8ug959sqebqvv46fgqqgj23o1',
                                'sequencer': '0C0F6F405D6ED209E1',
                                'size': 1305107},
                     's3SchemaVersion': '1.0'},
              'userIdentity': {'principalId': 'AWS:AIDAINPONIXQXHT3IKHL2'}}]}"""
