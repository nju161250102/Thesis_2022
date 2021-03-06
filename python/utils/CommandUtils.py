""" 命令行工具 """
import json
import os
from typing import List, Dict

from Config import Config
from Logger import LOG


def run(command: str, path=None, out=False) -> List[str]:
    """
    切换到指定目录下并执行命令
    :param command: 命令
    :param path: 需要切换的路径
    :param out: 是否打印命令语句
    :return: 按行划分的命令执行结果
    """
    if out:
        LOG.info(command if path is None else path + ": " + command)
    if path is not None:
        os.chdir(path)
    with os.popen(command) as p:
        return [s.strip() for s in p.readlines()]


def run_findbugs(jar_path: str, report_path: str):
    """
    使用Findbugs扫描得到xml格式的扫描报告
    :param jar_path: 目标Jar路径
    :param report_path: 扫描报告保存路径
    """
    run("java -jar {0} -textui -low -sortByClass -xml -output {1} {2}".
        format(Config.FINDBUGS_PATH, report_path, jar_path))


def run_spotbugs(jar_path: str, report_path: str):
    """
    使用Findbugs扫描得到xml格式的扫描报告
    :param jar_path: 目标Jar路径
    :param report_path: 扫描报告保存路径
    """
    run("java -jar {0} -textui -low -sortByClass -xml:withMessages={1} -quiet {2}".
        format(Config.FINDBUGS_PATH, report_path, jar_path))


def run_jhawk(project_path: str, report_path: str, exclude_files: List[str]):
    """
    使用JHawk命令行工具计算代码度量，并输出为xml文件
    :param project_path: 扫描项目路径
    :param report_path: 度量报告保存路径 [注意：末尾不需要.xml后缀名]
    :param exclude_files: 排除不扫描的文件路径列表
    """
    run("java -jar {0}/JHawkCommandLine.jar -x {1} -f .*\.java -r -s {2} -l pcm -a -p {0}/jhawk.properties -xf \"\\Q{3}\\E\"".
        format(Config.JHAWK_PATH, report_path, project_path, "\\E|\\Q".join(exclude_files)))


def grep_enumeration(project_path: str) -> List[str]:
    """
    获取项目下带有枚举类的文件路径列表
    :param project_path: 扫描项目路径
    """
    return run('grep -w "enum" {0} -r -l'.format(project_path))


def reformat_java(file_path: str, save_path: str, lines: List[int]) -> List[int]:
    """
    调用Jar格式化处理Java文件，并返回修改后行号的变化
    :param file_path: 原始的Java文件路径
    :param save_path: 修改后的Java文件路径
    :param lines: 原来的行号列表
    :return 修改后对应的行号列表
    """
    try:
        lines_str = [str(line) for line in lines]
        cmd_result = run("java -jar {0} format {1} {2} {3}"
                         .format(Config.JAVATOOLS_PATH, file_path, save_path, " ".join(lines_str)))
        if len(cmd_result) == 0:
            return [-1] * len(lines)
        return [int(line) for line in cmd_result]
    except IndexError or ValueError:
        return [-1] * len(lines)


def analyse_project(project_path: str) -> Dict[str, dict]:
    """
    调用Jar分析项目下类和方法的属性
    :param project_path: 项目路径
    :return: [类/方法的完全限定名: 属性字典]
    """
    cmd_result = run("java -jar {0} analyse {1}".format(Config.JAVATOOLS_PATH, project_path))
    return {cmd_result[2 * i]: json.loads(cmd_result[2 * i + 1]) for i in range(int(len(cmd_result) / 2))}
