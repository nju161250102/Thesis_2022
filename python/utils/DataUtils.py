import json
from typing import Dict

import pandas as pd

from . import PathUtils
from model import ProjectConfig, WarningType
from .MyEncoder import MyEncoder


def iter_report_df():
    for project_name, project_config in read_projects(PathUtils.join_path("project.json")).items():
        yield read_report_df(project_config)


def iter_version_df(project_config: ProjectConfig):
    """
    遍历项目各版本数据
    :param project_config: 项目配置
    :return 版本名称, 之前的所有版本数据, 当前版本的数据
    """
    report_df = read_report_df(project_config)
    for i in range(0, len(project_config.select) - 1):
        # 如果是第一个版本，则只存在测试集
        yield (project_config.select[i],
               None if i == 0 else report_df[report_df["version"] < project_config.select[i]].copy(),
               report_df[report_df["version"] == project_config.select[i]].copy())


def to_feature_df(project_config: ProjectConfig, index: pd.Index):
    feature_df = pd.read_csv(PathUtils.feature_path(project_config.name + ".csv"), index_col="index")
    return feature_df.loc[feature_df.index.intersection(index)]


def read_project_config(project_name: str = None):
    config_dict = read_projects(PathUtils.join_path("project.json"))
    return config_dict[project_name] if project_name else config_dict.values()


def read_projects(json_file: str) -> Dict[str, ProjectConfig]:
    """ 读取项目json """
    try:
        with open(json_file, "r") as f:
            return {k: ProjectConfig(v) for k, v in json.load(f).items()}
    except FileNotFoundError:
        return {}


def save_projects(config: Dict[str, ProjectConfig], json_file: str):
    """ 保存json到数据目录 """
    with open(json_file, "w") as f:
        f.write(json.dumps(config, indent=4, separators=(',', ':'), cls=MyEncoder))


def read_report_df(project_config: ProjectConfig):
    report_df = pd.read_csv(PathUtils.report_path(project_config.name + ".csv"), index_col="index", dtype={"next": object})
    version_type = pd.CategoricalDtype(project_config.select, ordered=True)
    report_df["version"] = report_df["version"].astype(version_type)
    report_df["addr"] = report_df.apply(lambda row: WarningType.to_addr(row["type"]), axis=1)
    report_df["_package"] = report_df["class_name"].map(lambda s: ".".join(s.split(".")[:-1]))
    report_df["_class"] = report_df["class_name"].map(lambda s: s.split("$")[0])
    report_df["_method"] = report_df.apply(lambda row: row["class_name"] + "." + row["method"], axis=1)
    return report_df
