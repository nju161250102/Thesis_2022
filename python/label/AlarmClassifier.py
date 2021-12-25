from typing import List, Dict, Tuple

import pandas as pd
from pandas.api.types import CategoricalDtype

from Logger import LOG
from model import Alarm
from utils import PathUtils
from .AlarmMatching import AlarmMatching


class AlarmClassifier(object):
    """
    警告分类器：用于标注正误报
    """

    def __init__(self, alarm_df: pd.DataFrame, versions: List[str], project_name: str):
        self.alarm_df = alarm_df.copy()
        self.versions = versions
        self.alarm_matcher = AlarmMatching(project_name)
        # 用于将扫描报告按版本先后顺序排列
        self.version_type = CategoricalDtype(self.versions, ordered=True)
        self.alarm_df = self.alarm_df[self.alarm_df["new_location"] != -1]
        self.alarm_df["version"] = self.alarm_df["version"].astype(self.version_type)

    def handle(self) -> Tuple[Dict[str, int], Dict[str, str]]:
        """
        不同版本扫描报告中的警告标记出正误报
        :return: 警告ID到标签，警告ID到下一个警告的ID
        """
        alarm_groups = []
        # 首先，在不同版本的警告中找出相同的警告
        for alarm_index, df in self.alarm_df.groupby(["path", "type"]):
            grouped = list(df.groupby("version"))
            grouped = list(filter(lambda g: len(g[1]) != 0, grouped))
            # 不处理仅出现在一个版本之中的警告
            for i in range(len(grouped) - 1):
                for alarm_a in Alarm.from_dataframe(grouped[i][1]):
                    # 相邻版本的警告尝试交叉匹配
                    matched_alarm = self.alarm_matcher.same_file_match(alarm_a, Alarm.from_dataframe(grouped[i + 1][1]))
                    # 匹配失败则使用下一版本中所有同类型警告匹配
                    if matched_alarm is None:
                        next_version = grouped[i + 1][0]
                        alarm_type = alarm_index[1]
                        alarm_group = df[(df.version == next_version) & (df.type == alarm_type)].copy()
                        matched_alarm = self.alarm_matcher.other_files_match(alarm_a, Alarm.from_dataframe(alarm_group))
                    # 有同类警告则追加顺序
                    if matched_alarm is not None:
                        has_flag = False
                        for j in range(len(alarm_groups)):
                            if alarm_groups[j][-1].index == alarm_a.index:
                                alarm_groups[j].append(matched_alarm)
                                has_flag = True
                        if not has_flag:
                            alarm_groups.append([alarm_a, matched_alarm])
        LOG.info("Match pairs: {0}".format(len(alarm_groups)))
        LOG.info("Match info: Location - {0}, Snippet - {1}, Hash - {2}"
                 .format(self.alarm_matcher.location_num, self.alarm_matcher.snippet_num, self.alarm_matcher.hash_num))
        # 用于标记中间值
        alarm_flag_list = []
        # 接下来标记误报
        for alarm_group in alarm_groups:
            # 警告与出现的版本对应
            alarm_group_dict = {a.version: a for a in alarm_group}
            # 找到最后一个警告消失的版本
            version_index = len(self.versions) - 1
            while version_index >= 0 and alarm_group_dict.get(self.versions[version_index]) is not None:
                version_index -= 1
            # 如果警告没有消失，全部标记为误报，否则将之前的版本标记为正报
            for i in range(len(self.versions)):
                if self.versions[i] in alarm_group_dict.keys():
                    alarm_group_dict[self.versions[i]].label = Alarm.TP if i < version_index else Alarm.FP
            # 中间值测试
            alarm_flag_list.append([(alarm_group_dict[v].index if v in alarm_group_dict.keys() else None) for v in self.versions])
        # 保存中间值参考
        df = pd.DataFrame(alarm_flag_list, columns=self.versions)
        df.to_csv(PathUtils.report_path("temp.csv"))
        # 合并所有标记后的警告
        label_result = {}
        next_result = {}
        for alarm_group in alarm_groups:
            for i, alarm in enumerate(alarm_group):
                # 记录下一个警告ID
                if i < len(alarm_group) - 1:
                    next_result[alarm.index] = alarm_group[i + 1].index
                else:
                    next_result[alarm.index] = ""
                # 如果警告标记冲突，重新标为不确定
                if alarm.index in label_result.keys() and label_result[alarm.index] != alarm.label:
                    label_result[alarm.index] = Alarm.UNKNOWN
                else:
                    label_result[alarm.index] = alarm.label
        return label_result, next_result
