from collections import defaultdict
from typing import List

from data import ReportData
from model import Alarm, ProjectConfig
from utils import LOG
from .AlarmMatching import AlarmMatching


class AlarmClassifier(object):
    """
    警告分类器：用于标注正误报
    """

    def __init__(self, config: ProjectConfig):
        self.project_name = config.name
        # 按版本先后顺序排列的扫描报告
        self.report_list = [ReportData.read_report(config.name, version) for version in config.select]
        self.alarm_matcher = AlarmMatching()

    def handle(self) -> List[Alarm]:
        """
        不同版本扫描报告中的警告标记出正误报
        :return: 所有标记完的警告列表
        """
        # 首先，在不同版本的警告中找出相同的警告
        all_alarm_dict = defaultdict(list)
        for report in self.report_list:
            alarm_dict = defaultdict(list)
            for alarm in report:
                # 使用警告路径和类型的组合做初步的筛选
                alarm_key = alarm.path + "|" + alarm.type
                alarm_dict[alarm_key].append(alarm)
            for key, value in alarm_dict.items():
                all_alarm_dict[key].append(value)
        # 去除仅出现在一个版本的警告
        for key in list(all_alarm_dict.keys()):
            if len(all_alarm_dict[key]) <= 1:
                del (all_alarm_dict[key])
        LOG.info("filter by path and alarm type: {0} keys".format(len(all_alarm_dict)))
        result = []
        for alarm_key, alarm_list in all_alarm_dict.items():
            # 每对相邻版本之间警告的匹配关系
            link_list = []
            for i in range(len(alarm_list) - 1):
                # 相邻版本的警告尝试交叉匹配
                link_list.append({})
                for j in range(len(alarm_list[i])):
                    for k in range(len(alarm_list[i + 1])):
                        # 如果匹配成功则加入一个匹配对
                        if AlarmMatching.handle(alarm_list[i][j], alarm_list[i + 1][k]):
                            link_list[-1][j] = [k]
            # 所有警告匹配对
            matched_alarms = []
            for i in range(len(link_list)):
                for index in link_list[i].keys():
                    matched_alarm_pair = [alarm_list[i][index]]
                    p = i
                    while p < len(link_list) and index in link_list[p].keys():
                        matched_alarm_pair.append(alarm_list[p + 1][link_list[p][index]])
                        del (link_list[p][index])
                        p += 1
                    matched_alarms.append(matched_alarm_pair)
            LOG.info("{0} match pairs: {1}".format(alarm_key, len(matched_alarms)))
            #
        return result
