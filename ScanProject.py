"""
项目漏洞扫描脚本
"""
import json
import os
import sys

from Config import Config
from data import ReportData
from utils import LOG

if __name__ == "__main__":
    with open(os.path.join(Config.DATA_DIR, "project.json"), "r") as f:
        project_list = json.loads(f.read())
        for project in project_list:
            if len(sys.argv) > 1 and project["name"] != sys.argv[1]:
                continue
            LOG.info("Start scan project: " + project["name"])
            for index, commit in enumerate(project["commit_list"]):
                ReportData.scan_project(project["name"], commit["sha"], index)
