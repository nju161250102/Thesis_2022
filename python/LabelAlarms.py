"""
项目警告误报标记脚本
"""
import sys

import pandas as pd

from label import AlarmClassifier
from utils import LOG, PathUtils, JsonUtils


def add_report(report_map: dict, report: list, version_sum: int, version_index: int):
    """
    将报告中的漏洞以 类名.方法名 聚合成 Map，保留版本顺序
    :param report_map: 聚合 Map
    :param report: 漏洞报告
    :param version_sum: 版本总数
    :param version_index: 当前版本在序列中的序号
    """
    for bug in report:
        bug_index = bug["Class"] + "." + bug["Type"]
        if bug_index not in report_map.keys():
            report_map[bug_index] = [None] * version_sum
        report_map[bug_index][version_index] = bug


if __name__ == "__main__":
    # 项目名（和project.json中的键名保持一致）
    project_name = sys.argv[1]
    with open(PathUtils.join_path("project.json"), "r") as f:
        project_config = JsonUtils.read_projects(PathUtils.join_path("project.json"))
    # 没有这个项目的配置则退出
    if project_name not in project_config.keys():
        LOG.error("{0} not found in config".format(project_name))
        sys.exit()
    labeled_alarms = AlarmClassifier(project_config[project_name]).handle()
    df = pd.DataFrame([alarm.__dict__ for alarm in labeled_alarms])
    df.to_csv(PathUtils.report_path(project_config[project_name].name + "_labeled.csv"), index_label="index")
