""" 项目下载与扫描脚本 """
import sys

from data import MavenData, ReportData
from utils import PathUtils, DataUtils


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        for arg in sys.argv[1:]:
            project_config = DataUtils.read_projects(PathUtils.join_path("project.json"))
            # 从Maven仓库中收集项目的版本数据等信息，保存到 project.json 文件
            if arg == "collect":
                project_config = MavenData.search_all_versions()
                DataUtils.save_projects(project_config, PathUtils.join_path("project.json"))
            # 下载jar包和源码jar包，并解压源码
            if arg == "download":
                MavenData.download_all(project_config)
            # 扫描下载好的jar包
            if arg == "scan":
                ReportData.scan_all_jars(project_config)
                ReportData.read_all_reports(project_config)
            # 整合警告并对相关java文件预处理
            if arg == "update":
                ReportData.update_all_alarms(project_config)
