from datetime import datetime
from pathlib import Path, PurePath

from teams_settings import FILE_STORE, PROJ_PATH, STAGE, fileStore, processingStage


def _generate_date_directory(date: datetime) -> str:
    return date.strftime("%Y-%m-%d")


def _generate_teams_stage(processing_stage: processingStage) -> str:
    teams_processing_stage: str = f"{processing_stage.value}.teams"
    if STAGE == "dev":
        return f"dev.{teams_processing_stage}"
    else:
        return teams_processing_stage


def _generate_file_name(file_name: str, file_ext: str) -> str:
    return ("").join([file_name, file_ext])


def get_file_ext(file_name: str) -> str:
    file_name: PurePath = Path(file_name)
    return file_name.suffix


def generate_processing_stage_file_path(
    name: str, date: datetime, teams_processing_stage: processingStage, file_ext: str = ".json"
) -> str:
    file_path = "ERROR"
    teams_stage = _generate_teams_stage(processing_stage=teams_processing_stage)
    date_dir = _generate_date_directory(date=date)
    filename = _generate_file_name(file_name=name, file_ext=file_ext)
    if FILE_STORE == fileStore.Local.value:
        file_path = PurePath(PROJ_PATH).joinpath(teams_stage, date_dir, filename)
    elif FILE_STORE == fileStore.S3.value:
        root = PurePath(teams_stage)
        file_path = PurePath(root).joinpath(date_dir, filename)

    return str(file_path)
