# Call cabinet ☎️

> Overview 

CallCabinet provides a number of different APIs and methodologies to allow for direct integration with the CallCabinet Atmos system. This project ingest the calls returned from call cabinet API and process the data into a few S3 buckets on AWS. This is part of a context called `big_data` That is basically a data consumer with processing steps following the basic concept of `ELT (Extract Load Transform)` &` ETL( Extract Transform Load) `


**Note:** This API provides access to the CallListingService and SingleCall APIs provided by CallCabinet.

[========]


#### Call endpoints 
> This Urls allows you to get calls from the Call cabinet API , the params are specified in the urls down below 📝

[========]



- `call_listings_url`: will return a list of calls (100 max).
- `call_recording_download_url`: will return a call recording (mp3).
- `single_call_listing_url`: will return a single call.
- `single_call_client_ref`: will return a single call.
- `single_call_call_id`: will return a single call.
- `single_call_phone_system_call`: will return a single call.


```
call_listings_url: str = "https://api.callcabinet.com/api/CallListingService"
```
```
call_recording_download_url: str = "https://api.callcabinet.com/APIServices/DownloadAudioFile?APIKey={APIKey}&CustomerID={CustomerID}&SiteID={SiteID}&CallID={CallID}"
```
```
single_call_listing_url: str = "https://atmos.callcabinet.com/Calls/SingleCall?CallID={AtmosCallID}"
```
```
single_call_client_ref = "https://secure.callcabinet.com/Calls/SingleCall?clientref={ClientRef}"
```
```
single_call_call_id = "https://secure.callcabinet.com/Calls/SingleCall?callId={CallID}" 
```
```
single_call_phone_system_call = "https://secure.callcabinet.com/Calls/SingleCall?phoneSystemCallId={PhoneSystemCallID}" 
```

[========]

**Required Parameters**

- `api_key`: str - Required. The API Key you were provided for the site.
- `customer_id`: str - Required. The Customer ID.
- `site_id`: str - Required. The Site ID.



**Optional Parameters**

- `call_id`: str or None - Will return only the one call with that CallID if there is a matching call.
- `from_date_time`: str or None - Will return calls where the start timestamp is greater than or equal to the value.
- `to_date_time`: str or None - Will return calls where the start timestamp is less than or equal to the value.
- `from_duration`: int or None - Will return calls where the duration is greater than or equal to the value.
- `to_duration`: int or None - Will return calls where the duration is less than or equal to the value.
- `agent_name`: str or None - Will return where the Agent Name matches completely (as FirstName[space]LastName, case insensitive).
- `extension`: str or None - Will return where the Extension matches completely.
- `phone_number`: str or None - Will return where the Phone Number matches completely.
- `is_incoming`: bool or None - If true will return only incoming calls, if false will return only outgoing calls.
- `customer_internal_ref`: str or None - Will return where the CustomerInternalRef/ClientRef matches completely (case insensitive).
- `did`: str or None - Will return where the DiD matches completely (case insensitive).
- `is_flagged`: bool or None - If true will return only flagged calls, if false will return only unflagged calls.
- `caller_id`: str or None - Will return where the CallerID matches completely (case insensitive).
- `phone_system_call_id_starts_with`: str or None - Will return calls where the PhoneSystemCallId starts with matching string.
- `phone_system_call_id_contains`: str or None - Will return calls.



[========]

## Call Listing Fields  📝

- `call_id`: str - The CallID of the call.
- `start_time`: str - The start time of the call.
- `duration`: int - The duration of the call in seconds.
- `extension`: str - The extension of the call.
- `agent_name`: str - The agent name as FirstName[space]LastName.
- `phone_number`: str - The phone number of the call.
- `customer_internal_ref`: str - The CustomerInternalRef/ClientRef assigned to the call.
- `flagged`: bool - Whether the call is flagged.
- `dtmf`: str - The DTMF of the call.
- `did`: str - The DiD of the call.
- `direction`: str - The direction of the call (as "Incoming", "Outgoing", or "Unknown").
- `caller_id`: str - The CallerID of the call.
- `recording_available`: bool - Whether the recording has finished uploading and is available to listen to or download.

#TODO what is this? I know, but please explain elaborate. 


```
{
    "call_id": "string",
    "start_time": "string",
    "duration": "integer",
    "extension": "string",
    "agent_name": "string",
    "phone_number": "string",
    "customer_internal_ref": "string",
    "flagged": "boolean",
    "dtmf": "string",
    "did": "string",
    "direction": "string",
    "caller_id": "string",
    "recording_available": "boolean"
}
```

