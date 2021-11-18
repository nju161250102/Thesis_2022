import pandas as pd
from pandas.api.types import CategoricalDtype
from typing import List

from model import Alarm, ProjectConfig
from utils import LOG, PathUtils
from .AlarmMatching import AlarmMatching


class AlarmClassifier(object):
    """
    警告分类器：用于标注正误报
    """

    def __init__(self, config: ProjectConfig):
        self.project_name = config.name
        # 按版本先后顺序排列的扫描报告
        self.versions = config.select
        self.version_type = CategoricalDtype(config.select, ordered=True)
        self.report_df = pd.read_csv(PathUtils.report_path(config.name + ".csv"), index_col="index")
        self.report_df["version"] = self.report_df["version"].astype(self.version_type)
        self.alarm_matcher = AlarmMatching(config.name)

    def handle(self) -> List[Alarm]:
        """
        不同版本扫描报告中的警告标记出正误报
        :return: 所有标记完的警告列表
        """
        alarm_groups = []
        # 首先，在不同版本的警告中找出相同的警告
        for alarm_index, df in self.report_df.groupby(["path", "type"]):
            grouped = list(df.groupby("version"))
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
                        for alarm_group in alarm_groups:
                            if alarm_group[-1] == alarm_a:
                                has_flag = True
                                alarm_group.append(matched_alarm)
                        if not has_flag:
                            alarm_groups.append([alarm_a, matched_alarm])
        LOG.info("Match pairs: {0}".format(len(alarm_groups)))
        # 接下来标记误报
        for alarm_group in alarm_groups:
            # 警告在对应版本中是否出现，-1表示未出现，否则为警告的索引
            alarm_flags = []
            # 文件在对应版本中是否出现，检查前面版本中最接近的警告所在的文件
            file_flags = []
            alarm_index = 0
            for version in self.versions:
                if alarm_group[alarm_index].version != version:
                    alarm_flags.append(-1)
                    # 检查前面版本中最接近的警告所在的文件
                    if alarm_index == 0:
                        file_flags.append(False)
                    else:
                        file_flags.append(PathUtils.exist_path("project", self.project_name, alarm_group[alarm_index - 1].path))
                else:
                    # 警告存在则文件一定存在
                    alarm_flags.append(alarm_index)
                    file_flags.append(True)
                    alarm_index += 1
            # 中间值测试

            # 最终两个flag列表长度与versions相同
            p = 0
            while alarm_flags[p] < 0:
                p += 1
            last_alarm_index = alarm_flags[p]
            while p < len(alarm_flags):
                if alarm_flags[p] < 0:
                    if file_flags[p]:
                        # 如果警告在文件存在的情况下消失，说明得到了修复，所以之前的都标记为正报
                        for i in range(last_alarm_index + 1):
                            alarm_group[i].label = Alarm.TP
                else:
                    last_alarm_index = alarm_flags[p]
                p += 1
            # 到当前版本仍然存在，或者因文件删除而消失的警告，标记为误报
            if last_alarm_index != len(alarm_group) - 1:
                for i in range(len(alarm_group)):
                    if alarm_group[i].label == Alarm.UNKNOWN:
                        alarm_group[i].label = Alarm.FP
        # 合并所有标记后的警告
        result = []
        for alarm_group in alarm_groups:
            result.extend(alarm_group)
        return result
