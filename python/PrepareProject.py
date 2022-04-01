"""
项目下载与扫描脚本，使用`-h`选项查看帮助，使用选项即执行相关命令，可同时执行多个。

短选项 | 长选项 | 含义
----- | ----- | ---
-c | --collect  | 从Maven仓库中收集项目的版本数据等信息，保存到 project.json 文件
-d | --download   | 下载jar包和源码jar包，并解压源码
-s | --scan | 扫描下载好的jar包
-u | --update   | 整合警告并对相关java文件预处理
"""
import argparse

from data import MavenData, ReportData
from utils import PathUtils, DataUtils


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and scan projects")
    parser.add_argument("-c", "--collect", action="store_true",
                        help="Collect version information of projects from Maven repository")
    parser.add_argument("-d", "--download", action="store_true",
                        help="Download two jars and unzip them")
    parser.add_argument("-s", "--scan", action="store_true",
                        help="Scan jars")
    parser.add_argument("-u", "--update", action="store_true",
                        help="Reformat java file and update the line number of alarm")
    args = parser.parse_args()

    project_config = DataUtils.read_projects(PathUtils.join_path("project.json"))
    # 从Maven仓库中收集项目的版本数据等信息，保存到 project.json 文件
    if args.collect:
        project_config = MavenData.search_all_versions()
        DataUtils.save_projects(project_config, PathUtils.join_path("project.json"))
    # 下载jar包和源码jar包，并解压源码
    if args.download:
        MavenData.download_all(project_config)
    # 扫描下载好的jar包
    if args.scan:
        ReportData.scan_all_jars(project_config)
        ReportData.read_all_reports(project_config)
    # 整合警告并对相关java文件预处理
    if args.update:
        ReportData.update_all_alarms(project_config)
