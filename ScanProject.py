"""
项目漏洞扫描脚本
"""
import json
import os

from Config import Config
from data import MavenData

if __name__ == "__main__":
    with open(os.path.join(Config.DATA_DIR, "project.json"), "r") as f:
        MavenData.download_all(json.load(f))
