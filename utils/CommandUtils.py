# uncompyle6 version 3.7.4
# Python bytecode 3.8 (3413)
# Decompiled from: Python 3.8.5 (default, Sep  4 2020, 07:30:14) 
# [GCC 7.3.0]
# Embedded file name: /home/qian/Document/研究生毕业论文/Thesis_2022/utils/CommandUtils.py
# Compiled at: 2021-08-13 20:16:07
# Size of source mod 2**32: 465 bytes
import os

class CommandUtils(object):
    __doc__ = '\n    命令行工具\n    '

    @staticmethod
    def run(command: str, path=None) -> list:
        """
        切换到指定目录下并执行命令
        :param command: 命令
        :param path: 需要切换的路径
        :return: 按行划分的命令执行结果
        """
        if path is not None:
            os.chdir(path)
        com_res = os.popen(command)
        return com_res.readlines()