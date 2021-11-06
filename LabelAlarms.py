"""
项目警告误报标记脚本
"""
import json
import sys
import pandas as pd

from data import ReportData
from utils import LOG, PathUtils
from label import label_bug


def add_report(report_map: dict, report: list, version_sum: int, version_index: int):
    """
    将报告中的漏洞以 类名.方法名 聚合成 Map，保留版本顺序
    :param report_map: 聚合 Map
    :param report: 漏洞报告
    :param version_sum: 版本总数
    :param version_index: 当前版本在序列中的序号
    """
    for bug in report:
        bug_index = bug["Class"] + "." + bug["Method"]
        if bug_index not in report_map.keys():
            report_map[bug_index] = [None] * version_sum
        report_map[bug_index][version_index] = bug


if __name__ == "__main__":
    # 项目名（和project.json中的键名保持一致）
    project_name = sys.argv[1]
    with open(PathUtils.join_path("project.json"), "r") as f:
        project_config = json.load(f)
    # 没有这个项目的配置则退出
    if project_name not in project_config.keys():
        LOG.error("{0} not found in config".format(project_name))
        sys.exit()
    # 前后版本顺序
    versions = project_config[project_name]["select"]
    # 各版本整合
    report_dict = {}
    for i in range(len(versions)):
        current_report = ReportData.read_report(project_config[project_name]["name"], versions[i])
        add_report(report_dict, current_report, len(versions), i)
    # 误报标记
    labeled_bug_list = []
    for bug_list in report_dict.values():
        bug_list = list(filter(None, bug_list))
        for i in range(len(bug_list) - 1):
            label_flag = False
            # 存在一个不一致的说明是正报
            for j in range(i, len(bug_list)):
                label_flag = label_flag or label_bug(bug_list[i], bug_list[j])
            bug_list[i]["Label"] = 1 if label_flag else 0
        labeled_bug_list.extend(bug_list)
    # 保存为csv文件
    df = pd.DataFrame(labeled_bug_list)
    df.to_csv(PathUtils.alarm_path(project_config[project_name]["name"] + ".csv"),
              index=False, encoding='utf-8')
