import json
from typing import Dict

from model import ProjectConfig


class JsonUtils(object):

    @staticmethod
    def read_projects(json_file: str) -> Dict[str, ProjectConfig]:
        with open(json_file, "r") as f:
            return {k: ProjectConfig(v) for k, v in json.load(f).items()}
