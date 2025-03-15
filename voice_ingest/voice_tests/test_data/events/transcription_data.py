from datetime import datetime

from botocore.stub import ANY
from dateutil.tz import tzlocal

transaction_job_return = dict()
return_items = dict()
media = dict()
media["MediaFileUri"] = "https://s3-eu-west-1.amazonaws.com/test.ips/audio/test.wav"

return_items["TranscriptionJobName"] = "test-test-1590501375-9349692"
return_items["TranscriptionJobStatus"] = "IN_PROGRESS"
return_items["LanguageCode"] = "en-GB"
return_items["MediaFormat"] = "wav"
return_items["Media"] = media
return_items["StartTime"] = datetime(2020, 5, 26, 14, 56, 22, 88000, tzinfo=tzlocal())
return_items["CreationTime"] = datetime(2020, 5, 26, 14, 56, 22, 59000, tzinfo=tzlocal())

transaction_job_return["TranscriptionJob"] = return_items

expected_params = {
    "TranscriptionJobName": ANY,
    "Media": {"MediaFileUri": ANY},
    "MediaFormat": ANY,
    "LanguageCode": "en-GB",
    "OutputBucketName": ANY,
}


"""{'TranscriptionJob': {'TranscriptionJobName': 'test-test-1593867851-729686', 'TranscriptionJobStatus': 'IN_PROGRESS', 'LanguageCode': 'en-GB', 'MediaFormat': 'wav', 'Media': {'MediaFileUri': 'https://s3-eu-west-1.amazonaws.com/test.ips/audio/test.wav'}, 'StartTime': datetime.datetime(2020, 7, 4, 14, 4, 29, 673000, tzinfo=tzlocal()), 'CreationTime': datetime.datetime(2020, 7, 4, 14, 4, 29, 652000, tzinfo=tzlocal())}, 'ResponseMetadata': {'RequestId': 'd17c3cdb-5015-48d1-955c-3eab25988634', 'HTTPStatusCode': 200, 'HTTPHeaders': {'content-type': 'application/x-amz-json-1.1', 'date': 'Sat, 04 Jul 2020 13:04:29 GMT', 'x-amzn-requestid': 'd17c3cdb-5015-48d1-955c-3eab25988634', 'content-length': '304', 'connection': 'keep-alive'}, 'RetryAttempts': 0}}"""
