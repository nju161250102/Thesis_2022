import os
from typing import List

from Config import Config
from .LogUtils import LOG


class CommandUtils(object):
    """
    命令行工具
    """

    @staticmethod
    def run(command: str, path=None) -> List[str]:
        """
        切换到指定目录下并执行命令
        :param command: 命令
        :param path: 需要切换的路径
        :return: 按行划分的命令执行结果
        """
        LOG.info(command if path is None else path + ": " + command)
        if path is not None:
            os.chdir(path)
        with os.popen(command) as p:
            return p.readlines()

    @staticmethod
    def find_bugs(jar_path: str, report_path: str):
        """
        使用Findbugs扫描得到扫描报告
        :param jar_path: 目标Jar地址
        :param report_path: 扫描报告目标路径
        """
        CommandUtils.run("java -jar {0} -textui -low -sortByClass -xml -output {1} {2}".
                         format(Config.FINDBUGS_PATH, report_path, jar_path))

    @staticmethod
    def reformat_java(file_path: str, line: int) -> int:
        """
        格式化处理Java文件，并返回修改后行号的变化
        :param file_path: Java文件路径
        :param line: 原来的行号
        :return 修改后的行号
        """
        return int(CommandUtils.run("java -jar {0} format {1} {2}".format(Config.JAVATOOLS_PATH, file_path, line))[0])
