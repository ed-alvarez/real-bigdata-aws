"""Settings for email Ingest Module"""

error = dict(
    cannot_unpack_journal_envelope="Journal envelope cannot be unpacked: {}",
    cannot_unpack_payload="real email payload cannot be extracted: {}",
    cannot_parse_payload="Real email payload cannot be parsed: {}",
    file_not_found="ERROR - Could not get object {} from bucket {}. Make sure the file exists and your bucket is in "
    "the same region as this function.",
    message_not_processed="Error trying to Process Message!",
    cannot_dump_to_JSON="Error cannot dump dict to json! file: {}. {}",
    cannot_save_JSON_to_tmp="Error trying to save JSON to tmp file! file: {} ",
    cannot_copy_JSON_tmp_to_s3="Error trying to copy JSON tmp file {} to s3",
    cannot_copy_MIME_to_s3_processed="Error trying to copy MIME File {} to s3 {}",
    cannot_copy_MIME_to_s3_archived="Error trying to copy MIME File {} to s3 {}",
    cannot_copy_JSON_to_processed="Error trying to copy JSON File {} to s3 {}",
    cannot_delete_MIME_from_todo="Error Deleting ToDo MIME File {}",
    cannot_delete_JSON_from_todo="Error Deleting ToDo JSON File {} ",
    cannot_save_document_to_es_pipeline="Error saving document to ElasticSearch Pipeline: {}",
    cannot_save_document_to_es_no_pipeline="Error saving document to ElasticSearch NO Pipeline: {}",
)

warning = dict(
    unable_to_decode_iCal="Warning - Unable to decode Calendar Item : {}",
    unable_to_decode_html="Warning - Unable to decode HTML Body of email : {}",
    es_document_already_exists="Warning - email is already in ElasticSearch : {}",
)
