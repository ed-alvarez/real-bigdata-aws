# Handler file borrowed from bbg-parse
import logging
import os
import shutil

import aws_lambda_logging
import slack_parse.download_api.slack_api_downloader
from slack_parse.download_api import slack_api_downloader

log_level = os.environ.get("LOGGING_LEVEL", "INFO")
boto_log_level = os.environ.get("BOTO_LOGGING_LEVEL", "INFO")
log = logging.getLogger()


def lambda_handler(event, context):
    if os.environ.get("AWS_EXECUTION_ENV") is None:
        ch = logging.StreamHandler()
        log.addHandler(ch)
        aws_lambda_logging.setup(level=log_level, boto_level=boto_log_level, module="%(module)s")
    else:
        aws_lambda_logging.setup(
            level=log_level,
            boto_level=boto_log_level,
            aws_request_id=context.aws_request_id,
            module="%(module)s",
        )

    for root, dirs, files in os.walk("/tmp"):
        for f in files:
            try:
                os.unlink(os.path.join(root, f))
            except Exception as e:
                log.info(f"Error deleting messages {e}")
        for d in dirs:
            try:
                shutil.rmtree(os.path.join(root, d))
            except Exception as e:
                log.info(f"Error deleting messages {e}")

    response = None

    log.info("Start Download Slack")
    log.info(event)

    """ expected event:
    event = {'client_name': 'ips', 'date_y_m_d': '2020-12-31'}
    """
    response = slack_parse.download_api.slack_api_downloader.download_slack_from_lambda_event(event)

    log.info(response)
    log.info(f"End Download Slack Data for {response['date_y_m_d']}")

    return response

    '''
    try:

        log.info('Start Download Slack')
        log.info(event)

        """ expected event:
        event = {'client_name': 'ips', 'date_y_m_d': '2020-12-31'}
        """
        response = slack_parse.slack_data.download_slack_from_lambda_event(event)

        log.info(response)
        log.info(f"End Download Slack Data for {response['date_y_m_d']}")

    except Exception as error:
    #
        response = {
            'status': 500,
            'error' : {
                'type'       : type(error).__name__,
                'description': str(error),
            },
        }
        log.error(response)
        log.error('End with Error Slack data download')

    finally:
        return response
    '''
