files_decoded = list()
files_decoded.append("dev.todo.bbg/2020-03-16/decoded/f848135.msg.200316.xml")
files_decoded.append("dev.todo.bbg/2020-03-16/decoded/f848135.dscl.200316.xml")
files_decoded.append("dev.todo.bbg/2020-03-16/decoded/f848135.ib.200316.xml")
files_decoded.append("dev.todo.bbg/2020-03-16/decoded/f848135.msg.200316.xml.sig")
files_decoded.append("dev.todo.bbg/2020-03-16/decoded/f848135.dscl.200316.xml.sig")
files_decoded.append(
    "dev.todo.bbg/2020-03-16/decoded/f848135.ib.200316.xml.sig",
)
files_decoded.append("dev.todo.bbg/2020-03-16/decoded/f848135.att.200316.tar.gz")
files_decoded.append("todo.bbg/2020-03-24/downloaded/f848377.att.200316.tar.gz.sig")


def setup_msg_ib_step_message(
    client_name="",
    IB_XML_No=0,
    IB_XML_to_process=True,
    IB_filename="",
    MSG_XML_No=0,
    MSG_XML_to_process=True,
    message_type="input",
) -> dict:

    bbg_files = dict()
    bbg_files["MSG_XML_to_process"] = MSG_XML_to_process
    bbg_files["MSG_file_name"] = "dev.todo.bbg/2020-03-16/decoded/f848135.msg.200316.xml"
    bbg_files["MSG_ATT_file_name"] = "dev.todo.bbg/2020-03-16/decoded/f848135.att.200316.tar.gz"
    bbg_files["MSG_XML_record_number"] = MSG_XML_No
    bbg_files["IB_XML_to_process"] = IB_XML_to_process
    bbg_files["IB_file_name"] = IB_filename or "dev.todo.bbg/2020-03-16/decoded/f848135.ib.200316.xml"
    bbg_files["IB_ATT_file_name"] = "dev.todo.bbg/2020-03-16/decoded/f848135.att.200316.tar.gz"
    bbg_files["IB_XML_record_number"] = IB_XML_No

    step_input = dict()
    step_input["client_name"] = client_name or "test_client_name"
    step_input["files_decoded"] = files_decoded
    step_input["files_downloaded"] = []
    step_input["has_files"] = False
    step_input["error"] = False
    step_input["error_msg"] = ""
    step_input["bbg_client_id"] = "mc123456"
    step_input["bbg_manifest"] = "DAILY"
    step_input["manifest_date"] = "200316"
    step_input["wait_until"] = ""
    step_input["bbg_files"] = bbg_files
    step_message = dict()
    step_message["name"]: "fnIterateIBUpload"
    step_message[message_type] = step_input

    return step_message


"""
Input and output message formats:

"input": {
    "client_name": "gemsstock",
    "files_downloaded": [],
    "files_decoded": [
      "todo.bbg/2021-02-05/decoded/f886955.msg.210205.xml",
      "todo.bbg/2021-02-05/downloaded/f886955.msg.210205.xml.sig",
      "todo.bbg/2021-02-05/decoded/f886955.dscl.210205.xml",
      "todo.bbg/2021-02-05/downloaded/f886955.dscl.210205.xml.sig",
      "todo.bbg/2021-02-05/decoded/f886955.att.210205.tar.gz",
      "todo.bbg/2021-02-05/downloaded/f886955.att.210205.tar.gz.sig",
      "todo.bbg/2021-02-05/decoded/f886955.ib.210205.xml",
      "todo.bbg/2021-02-05/downloaded/f886955.ib.210205.xml.sig"
    ],
    "has_files": false,
    "error": false,
    "error_msg": "",
    "bbg_client_id": "mc843476559",
    "bbg_manifest": "DAILY",
    "manifest_date": "210205",
    "wait_until": "",
    "bbg_files": {
      "MSG_XML_to_process": true,
      "MSG_file_name": "todo.bbg/2021-02-05/decoded/f886955.msg.210205.xml",
      "MSG_ATT_file_name": "todo.bbg/2021-02-05/decoded/f886955.att.210205.tar.gz",
      "MSG_XML_record_number": 0,
      "IB_XML_to_process": true,
      "IB_file_name": "todo.bbg/2021-02-05/decoded/f886955.ib.210205.xml",
      "IB_ATT_file_name": "todo.bbg/2021-02-05/decoded/f886955.att.210205.tar.gz",
      "IB_XML_record_number": 0,
      "IB_conversation_item": 0
    }

 "output": {
    "client_name": "gemsstock",
    "files_downloaded": [],
    "files_decoded": [
      "todo.bbg/2021-02-05/decoded/f886955.msg.210205.xml",
      "todo.bbg/2021-02-05/downloaded/f886955.msg.210205.xml.sig",
      "todo.bbg/2021-02-05/decoded/f886955.dscl.210205.xml",
      "todo.bbg/2021-02-05/downloaded/f886955.dscl.210205.xml.sig",
      "todo.bbg/2021-02-05/decoded/f886955.att.210205.tar.gz",
      "todo.bbg/2021-02-05/downloaded/f886955.att.210205.tar.gz.sig",
      "todo.bbg/2021-02-05/decoded/f886955.ib.210205.xml",
      "todo.bbg/2021-02-05/downloaded/f886955.ib.210205.xml.sig"
    ],
    "has_files": false,
    "error": false,
    "error_msg": "",
    "bbg_client_id": "mc843476559",
    "bbg_manifest": "DAILY",
    "manifest_date": "210205",
    "wait_until": "",
    "bbg_files": {
      "MSG_XML_to_process": true,
      "MSG_file_name": "todo.bbg/2021-02-05/decoded/f886955.msg.210205.xml",
      "MSG_ATT_file_name": "todo.bbg/2021-02-05/decoded/f886955.att.210205.tar.gz",
      "MSG_XML_record_number": 0,
      "IB_XML_to_process": false,
      "IB_file_name": "todo.bbg/2021-02-05/decoded/f886955.ib.210205.xml",
      "IB_ATT_file_name": "todo.bbg/2021-02-05/decoded/f886955.att.210205.tar.gz",
      "IB_XML_record_number": 0,
      "IB_conversation_item": 0
    }
"""
