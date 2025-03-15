# Handler file borrowed from bbg-parse
import logging
import os
import shutil

import aws_lambda_logging
import slack_parse.process.slack_processor

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
                log.info(f"Error deleting files in tmp {e}")
        for d in dirs:
            try:
                shutil.rmtree(os.path.join(root, d))
            except Exception as e:
                log.info(f"Error deleting files in tmp {e}")

    response = None

    log.info("Start Slack Processing")
    log.info(event)

    # todo data might be in event/context
    """ Event looks like:
    {'channels': None,
            'date_y_m_d': '2020-12-22',
            'client_name': 'ips',
'messages_s3_paths': ['dev.todo.slack/2020-12-22/json-slack/messages/C01FHG8T7J5__slack-ingest/2020-12-22.json',
          'dev.todo.slack/2020-12-22/json-slack/messages/G01FQMA8UVA__mpdm-anthony--james--mike-1/2020-12-22.json',
          'dev.todo.slack/2020-12-22/json-slack/messages/DPE3CD7CY/2020-12-22.json'],
'users': None}
    Leave messages_s3_paths blank to load from archived folder
"""

    response = slack_parse.process.slack_processor.process_slack_from_lambda_event(event, context)
    log.info(response)
    log.info(f'End Slack Processor for {response["date_y_m_d"]} for {response["client_name"]}')
    return response

    """
    try:

        log.info('Start Slack Processing')
        log.info(event)

        # todo data might be in event/context
        ''' Event looks like:
        {'channels': None,
                'date_y_m_d': '2020-12-22',
                'client_name': 'ips',
 'messages_s3_paths': ['dev.todo.slack/2020-12-22/json-slack/messages/C01FHG8T7J5__slack-ingest/2020-12-22.json',
              'dev.todo.slack/2020-12-22/json-slack/messages/G01FQMA8UVA__mpdm-anthony--james--mike-1/2020-12-22.json',
              'dev.todo.slack/2020-12-22/json-slack/messages/DPE3CD7CY/2020-12-22.json'],
 'users': None}
        Leave messages_s3_paths blank to load from archived folder
'''

        response = slack_parse.slack_processor.process_slack_from_lambda_event(event)
        log.info(response)
        log.info('End Download Data for {dates}')

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
        log.error('End with Error BBG IB Parse & Upload')

    finally:
        return response
    """
