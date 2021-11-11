import linecache

from model import Alarm
from utils import PathUtils


class AlarmMatching(object):

    def __init__(self, project_name: str):
        self.project_name = project_name
        # 记录匹配总数
        self.all_handle_num = 0
        # 记录匹配策略的命中次数
        self.location_num = 0
        self.snippet_num = 0
        self.hash_num = 0

    def handle(self, alarm_a: Alarm, alarm_b: Alarm) -> bool:
        """
        按照策略顺序判断警告是否匹配
        :param alarm_a: 警告a
        :param alarm_b: 警告b
        :return: 两个警告是否匹配
        """
        self.all_handle_num += 1
        return self.location_strategy(alarm_a, alarm_b) or \
            self.snippet_strategy(alarm_a, alarm_b) or \
            self.hash_strategy(alarm_a, alarm_b)

    def location_strategy(self, alarm_a: Alarm, alarm_b: Alarm) -> bool:
        """
        基于位置的匹配策略
        :return: 两个警告是否匹配
        """
        pass

    def snippet_strategy(self, alarm_a: Alarm, alarm_b: Alarm) -> bool:
        """
        基于片段的匹配策略
        :return: 两个警告是否匹配
        """
        file_a_path = PathUtils.project_path(self.project_name, alarm_a.version, alarm_a.path)
        file_b_path = PathUtils.project_path(self.project_name, alarm_b.version, alarm_b.path)
        code_a = linecache.getline(file_a_path, alarm_a.location)
        code_b = linecache.getline(file_b_path, alarm_b.location)
        return code_a.strip() == code_b.strip()

    def hash_strategy(self, alarm_a: Alarm, alarm_b: Alarm) -> bool:
        """
        基于哈希的匹配策略
        :return: 两个警告是否匹配
        """
        pass
