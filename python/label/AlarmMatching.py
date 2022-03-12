import difflib
import re
from typing import List, Tuple

from Logger import LOG
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
        # 参数配置
        self.location_delta = 3
        self.hash_delta = 100

    def same_file_match(self, alarm: Alarm, alarm_group: List[Alarm]) -> Alarm:
        """
        同一文件内，相同分类的警告匹配，如果存在多个，返回最匹配的
        :param alarm: 当前版本的警告
        :param alarm_group: 下一版本中同文件同类型的警告分组，默认非空
        :return: 下一版本中最匹配的警告，如果没有则返回None
        """
        if len(alarm_group) == 0:
            LOG.error("No alarm in group, current version is " + alarm.version)
        # 最匹配的警告
        matched_alarm = None
        # 前后版本的文件路径
        file_path_a = PathUtils.file_path(self.project_name, alarm.version, alarm.path)
        file_path_b = PathUtils.file_path(self.project_name, alarm_group[0].version, alarm_group[0].path)
        # 前后版本的文件内容
        file_content_a = open(file_path_a, "r").readlines()
        file_content_b = open(file_path_b, "r").readlines()
        # 标记了行号范围，必定从匹配块开始
        line_range_a = [0]
        line_range_b = [0]
        # 比较文件的差异并进行分块
        for line in difflib.unified_diff(file_content_a, file_content_b, n=0):
            if reg := re.match(r"@@ -(\d*),(\d*) \+(\d*),(\d*) @@", line):
                line_range_a.extend([int(reg.group(1)), int(reg.group(1)) + int(reg.group(2))])
                line_range_b.extend([int(reg.group(3)), int(reg.group(3)) + int(reg.group(4))])
            elif reg := re.match(r"@@ -(\d*) \+(\d*) @@", line):
                line_range_a.extend([int(reg.group(1)), int(reg.group(1)) + 1])
                line_range_b.extend([int(reg.group(2)), int(reg.group(2)) + 1])
            elif reg := re.match(r"@@ -(\d*),(\d*) \+(\d*) @@", line):
                line_range_a.extend([int(reg.group(1)), int(reg.group(1)) + int(reg.group(2))])
                line_range_b.extend([int(reg.group(3)), int(reg.group(3)) + 1])
            elif reg := re.match(r"@@ -(\d*) \+(\d*),(\d*) @@", line):
                line_range_a.extend([int(reg.group(1)), int(reg.group(1)) + 1])
                line_range_b.extend([int(reg.group(2)), int(reg.group(2)) + int(reg.group(3))])
        line_range_a.append(len(file_content_a))
        line_range_b.append(len(file_content_b))
        # 判断是匹配块还是差异块
        index = 0
        while line_range_a[index + 1] <= alarm.new_location:
            index += 1
        # 如果是匹配块
        if index % 2 == 0:
            # 找一个位置差相同的警告
            target_location = line_range_b[index] + (alarm.new_location - line_range_a[index])
            for alarm_b in alarm_group:
                if alarm_b.new_location == target_location:
                    matched_alarm = alarm_b
        # 如果是差异块
        else:
            delta_a = alarm.new_location - line_range_a[index]
            alarms_in_range = list(filter(
                lambda a: line_range_b[index] <= a.new_location < line_range_b[index + 1], alarm_group))
            alarms_in_range = list(filter(
                lambda a: abs(a.new_location - line_range_b[index] - delta_a) <= self.location_delta, alarms_in_range))
            alarms_in_range.sort(key=lambda a: abs(a.new_location - line_range_b[index] - delta_a))
            if len(alarms_in_range) > 0:
                matched_alarm = alarms_in_range[0]
        # 如果基于位置的算法失败，则采用基于片段的算法
        if matched_alarm is None:
            alarms_in_range = []
            for alarm_b in alarm_group:
                if file_content_b[alarm_b.new_location].strip() == file_content_a[alarm.new_location].strip():
                    alarms_in_range.append(alarm_b)
            alarms_in_range.sort(key=lambda a: abs(a.new_location - alarm.new_location))
            if len(alarms_in_range) > 0:
                matched_alarm = alarms_in_range[0]
                self.snippet_num += 1
        else:
            self.location_num += 1
        return matched_alarm

    def other_files_match(self, alarm: Alarm, alarm_group: List[Alarm]) -> Alarm:
        """
        基于哈希的匹配策略，在下一个版本中的所有同类警告中寻找匹配
        :param alarm: 当前版本的警告
        :param alarm_group: 下一版本中同类型的警告分组
        :return: 两个警告是否匹配
        """
        if len(alarm_group) == 0:
            LOG.error("No alarm in group, current version is " + alarm.version)
        # 最匹配的警告
        matched_alarm_group = []
        token_before, token_after = self._get_hash_token(alarm)
        hash_before = None if token_before is None else hash(" ".join(token_before))
        hash_after = None if token_after is None else hash(" ".join(token_after))
        for alarm_b in alarm_group:
            token_before, token_after = self._get_hash_token(alarm_b)
            if hash_before and token_before and hash(" ".join(token_before)) == hash_before:
                matched_alarm_group.append(alarm_b)
                continue
            if hash_after and token_after and hash(" ".join(token_after)) == hash_after:
                matched_alarm_group.append(alarm_b)
        if len(matched_alarm_group) == 1:
            self.hash_num += 1
            return matched_alarm_group[0]
        else:
            return None

    def _get_hash_token(self, alarm: Alarm) -> Tuple[List[str], List[str]]:
        """
        获取警告位置前后的token序列
        :param alarm:
        :return: 如果不足返回None
        """
        # 读取相应文件
        file_path = PathUtils.file_path(self.project_name, alarm.version, alarm.path)
        file_content = open(file_path, "r").readlines()
        # 分词得到token并去除空字符串
        token_lines = [re.split(r"[\{\};\+\*\[\]\.\\\|\(\)\?\^\-/:&<>\s]", line) for line in file_content]
        token_lines = [list(filter(lambda w: w != "", line)) for line in token_lines]
        # 警告位置之前的token
        token_before = []
        for i in range(alarm.new_location - 2, -1, -1):
            if len(token_before) + len(token_lines[i]) <= self.hash_delta:
                token_before = token_lines[i] + token_before
            else:
                token_before = token_lines[i][len(token_before) - self.hash_delta:] + token_before
        # 警告位置之后的token
        token_after = []
        for i in range(alarm.new_location - 1, len(token_lines)):
            if len(token_after) + len(token_lines[i]) <= self.hash_delta:
                token_after = token_after + token_lines[i]
            else:
                token_after = token_after + token_lines[i][:len(token_after) - self.hash_delta]
        if len(token_before) < self.hash_delta:
            token_before = None
        if len(token_after) < self.hash_delta:
            token_after = None
        return token_before, token_after
