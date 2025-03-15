import boto3
from botocore import session
from botocore.stub import ANY, Stubber
from mock import patch

from bbg_ingest.bbg_src.msg_upload_lambda import msg_upload
from bbg_ingest.bbg_tests import TestLambdaContext, step_case_MSG


class TestStepWrapper:
    @patch("settings.MSG_EMAIL_BATCH_SIZE", 2)
    @patch("settings.FILE_DUMP_BATCH_FILE", False)
    @patch("settings.UPLOAD_TO_ES", False)
    @patch.object(boto3, "client")
    def loop(self, mock_client, event, context):

        xml_file_name = "f848135.msg.200316.xml"
        xml_file = open("bbg_tests/fixtures_new/2020-03-16/decoded/" + xml_file_name, "rb")

        stub_msg_xlm = {"Body": xml_file}

        tar_file_name = "f848135.att.200316.tar.gz"
        tar_file = open("bbg_tests/fixtures_new/2020-03-16/decoded/" + tar_file_name, "rb")
        stub_tar_xml = {"Body": tar_file}

        stub_s3_get_object_params = {"Bucket": ANY, "Key": ANY}

        stubbed_client = session.get_session().create_client("s3")
        stubber = Stubber(stubbed_client)
        stubber.add_response("get_object", stub_msg_xlm, stub_s3_get_object_params)
        stubber.add_response("get_object", stub_tar_xml, stub_s3_get_object_params)
        stubber.activate()
        mock_client.return_value = stubbed_client

        response = msg_upload.lambda_handler(event["input"], context)

        print(response)
        print(type(response))

        del mock_client
        del stubbed_client
        del stubber
        del xml_file
        del tar_file

        return response

    def test_loop_1(self):
        event = step_case_MSG.setup_input_message()
        context = TestLambdaContext(time_limit_in_seconds=300)

        response = self.loop(event=event, context=context)
        lambda_response = step_case_MSG.setup_output_message(MSG_File_No=1, MSG_XML_No=2)["output"]

        assert response["bbg_files"]["MSG_XML_record_number"] == lambda_response["bbg_files"]["MSG_XML_record_number"]
        assert response["bbg_files"]["MSG_json_file_number"] == lambda_response["bbg_files"]["MSG_json_file_number"]
        assert response["bbg_files"]["MSG_XML_to_process"]

    def test_loop_2(self):
        event = step_case_MSG.setup_input_message(MSG_File_No=1, MSG_XML_No=2)
        context = TestLambdaContext(time_limit_in_seconds=10)

        response = self.loop(event=event, context=context)
        lambda_response = step_case_MSG.setup_output_message(MSG_File_No=2, MSG_XML_No=3)["output"]

        assert response["bbg_files"]["MSG_XML_record_number"] == lambda_response["bbg_files"]["MSG_XML_record_number"]
        assert response["bbg_files"]["MSG_json_file_number"] == lambda_response["bbg_files"]["MSG_json_file_number"]
        assert response["bbg_files"]["MSG_XML_to_process"]


if __name__ == "__main__":
    lambdatest = TestStepWrapper()
    lambdatest.test_loop_1()

    lambdatest_2 = TestStepWrapper()
    lambdatest_2.test_loop_2()
