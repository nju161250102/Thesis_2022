"""
项目下载与扫描脚本
"""
import sys

from data import MavenData, ReportData
from utils import PathUtils, JsonUtils


def collect():
    """
    从Maven仓库中收集项目的版本数据等信息，保存到 project.json 文件
    """
    project_config = MavenData.search_all_versions()
    JsonUtils.save_projects(project_config, PathUtils.join_path("project.json"))


def download():
    """
    依据 project.json 文件下载jar包和源码jar包，并解压源码
    """
    project_config = JsonUtils.read_projects(PathUtils.join_path("project.json"))
    MavenData.download_all(project_config)


def scan():
    """
    依据 project.json 文件扫描相应下载好的jar包
    """
    project_config = JsonUtils.read_projects(PathUtils.join_path("project.json"))
    ReportData.scan_all_jars(project_config)
    ReportData.read_all_reports(project_config)


def update():
    """
    依据 project.json 文件整合警告并对相关java文件预处理
    """
    project_config = JsonUtils.read_projects(PathUtils.join_path("project.json"))
    ReportData.update_all_alarms(project_config)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        for arg in sys.argv[1:]:
            if arg == "collect":
                collect()
            if arg == "download":
                download()
            if arg == "scan":
                scan()
            if arg == "update":
                update()
