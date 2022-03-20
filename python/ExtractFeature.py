"""
项目警告特征提取脚本
如果特征文件已存在会覆盖
暂时废弃：添加 reduce 参数减少重复数据 :see reduce_alarms
"""
import sys
import pandas as pd

from feature import *
from Logger import LOG
from model import Alarm
from utils import PathUtils, DataUtils


def reduce_alarms(df: pd.DataFrame) -> pd.DataFrame:
    """
    选择每个警告链中与之前相比发生变化的警告，以减少重复数据量
    """
    next_dict = df["next"].to_dict()
    choose_index_set = set()
    handled_index_set = set()
    for alarm_index, row in df.iterrows():
        if alarm_index in handled_index_set:
            continue
        choose_index_set.add(alarm_index)
        handled_index_set.add(alarm_index)
        # 向后遍历警告，如果标记值不同，则选中
        while alarm_index in next_dict.keys() and pd.notna(next_dict[alarm_index]):
            if df.at[next_dict[alarm_index], "label"] != df.at[alarm_index, "label"]:
                choose_index_set.add(next_dict[alarm_index])
            alarm_index = next_dict[alarm_index]
            handled_index_set.add(alarm_index)
    return df.loc[choose_index_set].copy()


def extract_one_version(alarm_df: pd.DataFrame, project_name: str, version: str) -> pd.DataFrame:
    """
    提取一个版本对应警告的特征
    :param alarm_df: 警告DataFrame
    :param project_name: 项目名称
    :param version: 版本
    :return: 特征DataFrame
    """
    # 分别提取特征
    code_anl_df = CodeAnl(alarm_df, project_name, version).get_feature_df()
    code_chr_df = CodeChr(alarm_df, project_name, version).get_feature_df()
    warning_chr_df = WarningChr(alarm_df, project_name, version).get_feature_df()
    warning_cmb_df = WarningCmb(alarm_df, project_name, version).get_feature_df()
    # 合并不同类的特征DataFrame
    return pd.concat([code_anl_df, code_chr_df, warning_chr_df, warning_cmb_df], axis=1)


if __name__ == "__main__":
    for project_name, project_config in DataUtils.read_projects(PathUtils.join_path("project.json")).items():
        data_df = pd.read_csv(PathUtils.report_path(project_config.name + ".csv"), index_col="index")
        # 提取特征时就过滤掉未知的警告
        data_df = data_df[data_df["label"] != Alarm.UNKNOWN].copy()
        # 是否减少警告数目
        if len(sys.argv) == 2 and sys.argv[1] == "reduce":
            data_df = reduce_alarms(data_df)
        # 保存特征结果
        result_df = pd.DataFrame()
        # 分版本特征提取
        for version, group_df in data_df.groupby("version"):
            result_df = pd.concat([result_df, extract_one_version(group_df, project_config.name, version)])
        result_df["label"] = data_df["label"]
        result_df.dropna(inplace=True)
        LOG.info(project_name + "\t" + str(result_df.shape))
        result_df.to_csv(PathUtils.feature_path(project_config.name + ".csv"))
