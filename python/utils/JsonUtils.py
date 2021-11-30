import json
from typing import Dict

from model import ProjectConfig
from .MyEncoder import MyEncoder


class JsonUtils(object):

    @staticmethod
    def read_projects(json_file: str) -> Dict[str, ProjectConfig]:
        with open(json_file, "r") as f:
            return {k: ProjectConfig(v) for k, v in json.load(f).items()}

    @staticmethod
    def save_projects(config: Dict[str, ProjectConfig], json_file: str):
        """
        保存json到数据目录
        :param config: 配置json
        :param json_file: json文件路径
        """
        with open(json_file, "w") as f:
            f.write(json.dumps(config, indent=4, separators=(',', ':'), cls=MyEncoder))
