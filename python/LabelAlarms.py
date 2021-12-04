"""
项目警告误报标记脚本
"""
import pandas as pd

from label import AlarmClassifier
from utils import PathUtils, JsonUtils

if __name__ == "__main__":
    for project_name, project_config in JsonUtils.read_projects(PathUtils.join_path("project.json")).items():
        labeled_alarms = AlarmClassifier(project_config).handle()
        df = pd.DataFrame([alarm.__dict__ for alarm in labeled_alarms])
        df.to_csv(PathUtils.report_path(project_config.name + ".csv"), index_label="index")
