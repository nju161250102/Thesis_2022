import os

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
        LOG.info(path + ": " + command)
        if path is not None:
            os.chdir(path)
        with os.popen(command) as p:
            return p.readlines()
