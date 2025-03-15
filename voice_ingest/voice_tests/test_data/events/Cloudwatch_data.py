def transcribe_event(job_name=""):
    transcribe_event = dict()
    event_detail = dict()

    event_detail["TranscriptionJobName"] = job_name or "test-test-1593872733-77324"

    event_detail["TranscriptionJobStatus"] = "COMPLETED"

    transcribe_event["version"] = "0"
    transcribe_event["id"] = "103904f8-85fe-ee6a-af0b-55c82e0d0797"
    transcribe_event["detail-type"] = "Transcribe Job State Change"
    transcribe_event["source"] = "aws.transcribe"
    transcribe_event["firm"] = "955323147179"
    transcribe_event["time"] = "2020-05-28T10:45:40Z"
    transcribe_event["region"] = "eu-west-1"
    transcribe_event["resources"] = list()
    transcribe_event["detail"] = event_detail

    return transcribe_event
