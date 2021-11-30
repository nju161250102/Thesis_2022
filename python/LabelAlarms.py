"""
项目警告误报标记脚本
"""
import sys

import pandas as pd

from Logger import LOG
from label import AlarmClassifier
from utils import PathUtils, JsonUtils

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
