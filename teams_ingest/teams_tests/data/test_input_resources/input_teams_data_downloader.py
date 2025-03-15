"""
Resources for testing teams_data_downloader lambda
"""

input_teams_data_downloader = {
    "firm": "dev-ips",
    "period": "historical",
    "start_date": "2021-01-13",
    "end_date": "2021-01-14",
    "tenant_name": "test-ips",
    "tenant_id": "cab90704-9f9a-464f-9a7d-08116dc47cc3",
}

expected_output_teams_data_downloader = {
    "firm": "dev-ips",
    "period": "historical",
    "tenant_name": "",
    "tenant_id": "",
    "start_date": "",
    "end_date": "",
    "user_ids": [],
}
