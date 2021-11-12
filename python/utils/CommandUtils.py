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
        CommandUtils.run("java -jar {0} -textui -high -sortByClass -xml -output {1} {2}".
                         format(Config.FINDBUGS_PATH, report_path, jar_path))

    @staticmethod
    def java_tools(tool_type: str, *args):
        """
        使用Java编写的工具
        :param tool_type: 工具类型，详见Java项目
        :param args: 参数
        """
        CommandUtils.run("java -jar {0} {1} {2}".format(Config.JAVATOOLS_PATH, tool_type, " ".join(args)))
