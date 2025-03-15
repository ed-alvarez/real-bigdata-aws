import contextlib
import json
import logging
import os
import time
from enum import Enum
from typing import List

import boto3

from shared.shared_src.sf.launch_step import LaunchStepFunction

logger = logging.getLogger(name="STEP_FUNCTION_LOGGER")

STAGE = os.environ.get("STAGE", "dev")


class StepFunctionStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    ABORTED = "ABORTED"


class StepFunctionOrchestrator:
    def __init__(self, kwargs):

        logger.info(f"Initialize StepFunction Client with {kwargs}")

        self.state_machine_name = kwargs.get("step_function_name")
        self.event = kwargs.get("event")
        self._lambda_name = kwargs.get("lambda_name")
        self.step_function_arn = kwargs.get("step_function_arn")
        self.sfn_client = kwargs.get("sfn_client") or boto3.client("stepfunctions")
        self.tenant_class = kwargs.get("tenant_dataclass")
        self.success_runs = []
        self.failure_runs = []
        self.execution_arn = None
        self.list_executions = None
        self.lambda_execution_logs = None
        self.step_function_verification = None
        self.error_log = None
        if not self.step_function_arn:
            self.get_arn_by_name()

    def get_arn_by_name(self):
        try:
            response = self.sfn_client.list_state_machines()["stateMachines"]
            for sfn in response:
                if sfn["name"] == self.state_machine_name:
                    self.step_function_arn = sfn["stateMachineArn"]
                    logger.info(f"State machine name {self.step_function_arn}")
        except Exception as e:
            self.error_log = str(e)
            logger.error(self.error_log)

    def _log_status(self, response: dict, status: str, is_done: bool) -> bool:
        logger.info(f"State machine name: {response['name']} is {status}")
        self.step_function_verification = response
        return is_done

    def get_lambda_execution_logs(self, execution_arn):
        response = self.sfn_client.get_execution_history(executionArn=execution_arn, maxResults=100)
        events = response["events"]

        while response.get("nextToken"):
            response = self.sfn_client.get_execution_history(
                executionArn=execution_arn, maxResults=100, nextToken=response["nextToken"]
            )
            events += response["events"]
        causes = [json.loads(e["taskFailedEventDetails"]["cause"]) for e in events if e["type"] == "TaskFailed"]

        self.lambda_execution_logs = [
            {
                "ClusterArn": cause["ClusterArn"],
                "Containers": [
                    {
                        "ContainerArn": container["ContainerArn"],
                        "Name": container["Name"],
                        "ExitCode": container["ExitCode"],
                        "Overrides": cause["Overrides"]["ContainerOverrides"][i],
                    }
                    for i, container in enumerate(cause["Containers"])
                ],
                "TaskArn": cause["TaskArn"],
                "StoppedReason": cause["StoppedReason"],
            }
            for cause in causes
        ]

    def get_list_executions(self):
        try:
            executions = []
            response = self.sfn_client.list_executions(stateMachineArn=self.step_function_arn)

            for execution in response["executions"]:
                self.get_execution_history(execution["executionArn"])
                execution["history"] = self.list_executions
                executions.append(execution)
            response["executions"] = executions
            self.list_executions = response

        except Exception as e:
            self.error_log = str(e)
            logger.error(self.error_log)

    def create_historical(self, start_date: str, end_date: str, date_format: str = "%Y-%m-%d"):
        import pandas

        dates = pandas.date_range(start=start_date, end=end_date).to_pydatetime().tolist()
        days_historical: list = [date.strftime(date_format) for date in dates]

        return [[days_historical[i], days_historical[i]] for i in range(len(days_historical) - 1)]

    def check_for_next_run(self, execution_arn: str):
        # Wait for the previous invocation to complete and check if it was successful
        try:
            while True:
                # Get Execution detail
                run_status: StepFunctionStatus = self.get_status_from_execution_arn(execution_arn=execution_arn)
                if run_status == StepFunctionStatus.SUCCEEDED:
                    self.success_runs.append(execution_arn)
                    break
                elif run_status in {
                    StepFunctionStatus.FAILED.value,
                    StepFunctionStatus.TIMED_OUT.value,
                    StepFunctionStatus.ABORTED.value,
                }:
                    self.failure_runs.append(execution_arn)
                    break
                else:
                    time.sleep(3)

        except Exception as error:
            logger.exception(f"Failure Describing execution: {error}")

    def execute_historical(self):

        pair_dates: List[List[str]] = self.create_historical(start_date=self.event["start_date"], end_date=self.event['end_date'])
        for date_range in pair_dates:

            event_for_function = {
                **self.event,
                'start_date': date_range[0] if len(date_range) > 1 else None,
                'end_date': date_range[1] if len(date_range) > 1 else None,
            }
            try:
                launch_step_function: LaunchStepFunction = LaunchStepFunction(
                    event=event_for_function, state_machine_arn=self.step_function_arn
                )
                step_fn_name, execution_arn = launch_step_function.start_execution_step_function(self.tenant_class)

                logger.info(f"Triggered Historical Step Function: {step_fn_name}")

                self.check_for_next_run(execution_arn)

            except Exception as error:
                logger.exception(f"Failure on Lambda execution: {error}")

    def execute_daily(self):
        try:
            launch_step_function: LaunchStepFunction = LaunchStepFunction(event=self.event, state_machine_arn=self.step_function_arn)
            step_fn_name, execution_arn = launch_step_function.start_execution_step_function(self.tenant_class)
            logger.info(f"Triggered Daily Step Function: {step_fn_name}")
        except Exception as error:
            logger.exception(f"Failure on Lambda execution: {error}")

    def orchestrate(self):
        ingest_range = self.event.get('period')
        if ingest_range == 'historical':
            self.execute_historical()
            return self.success_runs, self.failure_runs

        else:
            self.execute_daily()

    def get_status_from_execution_arn(self, execution_arn: str) -> StepFunctionStatus:
        response = self.sfn_client.describe_execution(executionArn=execution_arn)
        return StepFunctionStatus(response.get("status"))
