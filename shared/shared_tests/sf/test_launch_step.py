import json
from ast import Dict
from dataclasses import dataclass
from datetime import datetime, timedelta

import dataclass_wizard
import pytest
from freezegun import freeze_time

from shared.shared_src.sf.launch_step import LaunchStepFunction

FAKE_TIME = datetime(year=2020, month=12, day=25, hour=17, minute=5, second=55, microsecond=3030)

from typing import Optional


@dataclass
class TestLaunchIngestChannel:
    firm: str = "test_client"
    tenant_name: str = "test_tenant"
    period: str = "historical"
    tenant_id: str = "abc"
    start_date: Optional[str] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    end_date: Optional[str] = datetime.now().strftime("%Y-%m-%d")


@pytest.fixture()
def launch_event():
    return {
        "firm": "test_client",
        "tenant_name": "test_tenant",
        "period": "historical",
        "start_date": "2022-01-01",
        "end_date": "2022-01-31",
    }


@pytest.fixture()
def launch_tenant_dt(launch_event):
    return dataclass_wizard.fromdict(TestLaunchIngestChannel, launch_event)


class TestLaunchStepFunction:
    def test_generate_step_function_name(self, launch_event, launch_tenant_dt):
        launch_step_function = LaunchStepFunction(launch_event, "test_arn")
        with freeze_time(FAKE_TIME):
            response: str = launch_step_function._generate_step_function_name(launch_event=launch_tenant_dt)
        assert response == "test_client_test_tenant_2022-01-01_2022-01-31__tsmp_2020_12_25_17_05_55"
