"""
项目漏洞下载与扫描脚本
"""
import json
import os

from Config import Config
from data import MavenData, ReportData

if __name__ == "__main__":
    with open(os.path.join(Config.DATA_DIR, "project.json"), "r") as f:
        MavenData.download_all(json.load(f))
        ReportData.scan_all_jar(json.load(f))
