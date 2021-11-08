from collections import defaultdict
from typing import List

from model import Alarm
from utils import PathUtils


class AlarmClassifier(object):
    """
    警告分类器：用于标注正误报
    """

    @staticmethod
    def handle(report_list: List[List[Alarm]]) -> List[Alarm]:
        """
        不同版本扫描报告中的警告标记出正误报
        :param report_list: 按版本先后顺序排列的扫描报告
        :return: 所有标记完的警告列表
        """
        # 首先，在不同版本的警告中找出相同的警告
        all_alarm_dict = defaultdict(list)
        for report in report_list:
            alarm_dict = defaultdict(list)
            for alarm in report:
                # 使用警告路径和类型的组合做初步的筛选
                alarm_key = alarm.path + "|" + alarm.type
                alarm_dict[alarm_key].append(alarm)
            for key, value in alarm_dict.items():
                all_alarm_dict[key].append(value)
        # 初步筛选结束
        for alarm_key, alarms in all_alarm_dict.items():
            pass

    @staticmethod
    def add_report(report_map: dict, report: list, version_sum: int, version_index: int):
        """
        将报告中的漏洞以 类名.方法名 聚合成 Map，保留版本顺序
        :param report_map: 聚合 Map
        :param report: 漏洞报告
        :param version_sum: 版本总数
        :param version_index: 当前版本在序列中的序号
        """
        for alarm in report:
            alarm_index = alarm["Class"] + "." + alarm["Type"]
            if alarm_index not in report_map.keys():
                report_map[alarm_index] = [None] * version_sum
            report_map[alarm_index][version_index] = alarm

