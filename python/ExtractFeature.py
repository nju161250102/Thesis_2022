"""
项目警告特征提取脚本
"""
import pandas as pd

from feature import *
from model import Alarm
from utils import PathUtils, JsonUtils

if __name__ == "__main__":
    for project_name, project_config in JsonUtils.read_projects(PathUtils.join_path("project.json")).items():
        data_df = pd.read_csv(PathUtils.report_path(project_config.name + ".csv"), index_col="index")
        # 提取特征时就过滤掉未知的警告
        data_df = data_df[data_df["label"] != Alarm.UNKNOWN]
        # 选择每个警告链中与之前相比发生变化的警告，以减少重复数据量
        next_dict = data_df["next"].to_dict()
        choose_index_set = set()
        handled_index_set = set()
        for alarm_index, row in data_df.iterrows():
            if alarm_index in handled_index_set:
                continue
            choose_index_set.add(alarm_index)
            handled_index_set.add(alarm_index)
            # 向后遍历警告，如果标记值不同，则选中
            while alarm_index in next_dict.keys() and pd.notna(next_dict[alarm_index]):
                if data_df.at[next_dict[alarm_index], "label"] != data_df.at[alarm_index, "label"]:
                    choose_index_set.add(next_dict[alarm_index])
                alarm_index = next_dict[alarm_index]
                handled_index_set.add(alarm_index)
        data_df = data_df.loc[choose_index_set]
        # 保存特征结果
        result_df = pd.DataFrame()
        # 分版本特征提取
        for version, group_df in data_df.groupby("version"):
            feature_df = pd.DataFrame(index=group_df.index)
            code_anl_df = CodeAnl(group_df, project_config.name, version).get_feature_df()
            code_chr_df = CodeChr(group_df, project_config.name, version).get_feature_df()
            warning_chr_df = WarningChr(group_df, project_config.name, version).get_feature_df()
            warning_cmb_df = WarningCmb(group_df, project_config.name, version).get_feature_df()
            # 合并不同类的特征DataFrame
            feature_df = feature_df.join(code_anl_df)
            feature_df = feature_df.join(code_chr_df)
            feature_df = feature_df.join(warning_chr_df)
            feature_df = feature_df.join(warning_cmb_df)
            # 合并到项目整体DataFrame
            result_df = result_df.append(feature_df)
        result_df["label"] = data_df["label"]
        result_df.dropna(inplace=True)
        result_df.to_csv(PathUtils.feature_path(project_config.name + ".csv"))
