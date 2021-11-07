"""
项目下载与扫描脚本
"""
from datetime import datetime
import json
import sys

from data import MavenData, ReportData
from utils import PathUtils
from Config import Config


def collect():
    """
    从Maven仓库中收集项目的版本数据等信息，保存到 project.json 文件
    """
    result = {}
    for p, config in Config.MAVEN_URL.items():
        # 获取包含版本信息的配置数据
        info = MavenData.search_versions(config["url"])
        # 如果指定了筛选的版本，合并
        if "select" in config.keys() and len(config["select"]) > 0:
            info["select"] = config["select"]
        # 如果指定了保留的版本的时间范围，筛选
        select_versions = info["versions"][:]
        if "startDate" in config.keys() and config["startDate"] is not None:
            start_date = datetime.strptime(config["startDate"], "%Y-%m-%d")
            select_versions = list(filter(
                lambda v: datetime.strptime(v["updateTime"], "%Y-%m-%d %H:%M:%S") >= start_date, select_versions))
        if "endDate" in config.keys() and config["endDate"] is not None:
            end_date = datetime.strptime(config["endDate"], "%Y-%m-%d")
            select_versions = list(filter(
                lambda v: datetime.strptime(v["updateTime"], "%Y-%m-%d %H:%M:%S") <= end_date, select_versions))
        # 将符合条件的版本号保存
        if len(select_versions) != len(info["versions"]):
            info["select"] = list(map(lambda v: v["number"], select_versions))
        result[p] = info
    # 保存json到数据目录
    with open(PathUtils.join_path("project.json"), "w") as f:
        f.write(json.dumps(result, indent=4, separators=(',', ':')))


def download():
    """
    依据 project.json 文件下载jar包和源码jar包，并解压源码
    """
    with open(PathUtils.join_path("project.json"), "r") as f:
        MavenData.download_all(json.load(f))


def scan():
    """
    依据 project.json 文件扫描相应下载好的jar包
    """
    with open(PathUtils.join_path("project.json"), "r") as f:
        ReportData.scan_all_jar(json.load(f))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "collect":
            collect()
        if sys.argv[1] == "download":
            download()
        if sys.argv[1] == "scan":
            scan()
