import os

from Config import Config
from .LogUtils import LOG


class CommandUtils(object):
    """
    命令行工具
    """

    @staticmethod
    def run(command: str, path=None) -> list:
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
        CommandUtils.run("{0} -textui -jvmArgs \"-Xmx4096m\" -high -sortByClass -xml -output {1} {2}".
                         format(Config.FINDBUGS_PATH, report_path, jar_path))
