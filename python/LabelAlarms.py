"""
项目警告误报标记脚本
"""
import pandas as pd

from Logger import LOG
from label import AlarmClassifier
from model import Alarm
from utils import PathUtils, JsonUtils

if __name__ == "__main__":
    for project_config in JsonUtils.read_projects(PathUtils.join_path("project.json")).values():
        # 读取警告记录
        alarm_df = pd.read_csv(PathUtils.report_path(project_config.name + ".csv"), index_col="index", dtype={"next": object})
        LOG.info("Project {0}: {1} alarms".format(project_config.name, len(alarm_df)))
        # 标记误报
        alarm_labels, alarm_next = AlarmClassifier(alarm_df, project_config.select, project_config.name).handle()
        # 更新标签
        for index, label in alarm_labels.items():
            alarm_df.at[index, "label"] = label
        for index, next_index in alarm_next.items():
            alarm_df.at[index, "next"] = next_index
        count_df = alarm_df.groupby("label").count()["version"]
        LOG.info("TP: {0}, FP: {1}, UNKNOWN: {2}".format(
            count_df.get(Alarm.TP, default=0), count_df.get(Alarm.FP, default=0), count_df.get(Alarm.UNKNOWN, default=0)))
        # 保存结果
        alarm_df.to_csv(PathUtils.report_path(project_config.name + ".csv"))
