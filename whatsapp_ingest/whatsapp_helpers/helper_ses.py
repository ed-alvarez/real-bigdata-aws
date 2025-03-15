"""
Module to process the SES header to add/update to Dynamo DB
input is the SES event
output is the  dynamoRec
"""


class processSESEvent:
    def __init__(self):
        self._event = None
        self._dynamo_rec = dict()
        self._headers_orig = None
        self._headers_new = dict()

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, event):
        self._event = event

    @property
    def dynamoRec(self):
        return self._dynamo_rec

    def reformatHeaders(self):
        for header in self._headers_orig:
            if header["value"]:
                # if header['name'] not in ['To', 'CC']:
                #    self._headers_new[header['name']] = header['value']
                # else:
                #    self._headers_new[header['name']] = header['value'].split(',')
                self._headers_new[header["name"]] = header["value"]

    def parseEvent(self):
        self._dynamo_rec["messageId"] = self._event["Records"][0]["ses"]["mail"]["messageId"]
        self._dynamo_rec["destination"] = self._event["Records"][0]["ses"]["receipt"]["recipients"][0]
        self._dynamo_rec["client"] = self._dynamo_rec["destination"].split("@")[0]
        self._dynamo_rec["timestamp"] = self._event["Records"][0]["ses"]["mail"]["timestamp"]
        self._dynamo_rec["source"] = self._event["Records"][0]["ses"]["mail"]["source"]
        self._headers_orig = self._event["Records"][0]["ses"]["mail"]["headers"]
        self.reformatHeaders()
        self._dynamo_rec["headers"] = self._headers_new
