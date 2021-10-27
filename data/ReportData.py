import os
import subprocess

from Config import Config
from utils import LOG


class ReportData(object):

    @staticmethod
    def scan_project(project_name: str, commit=None, version=0):
        if project_name not in Config.SCAN_CONF.keys():
            LOG.error("{0} not found in config".format(project_name))
            return
        conf = Config.SCAN_CONF[project_name]
        project_path = os.path.join(Config.DATA_DIR, "project", project_name)
        scan_path = os.path.join(project_path, conf["target"])
        xml_path = os.path.join(Config.DATA_DIR, "report", "{0}_{1}.xml".format(project_name, version))
        # 切换项目版本
        if commit is None:
            cmd = "cd {0} && git checkout {1}".format(project_path, conf["default"])
        else:
            cmd = "cd {0} && git checkout {1}".format(project_path, commit)
        LOG.info(cmd)
        subprocess.call(cmd)
        # 自动构建
        subprocess.call(conf["build"])
        # 扫描漏洞
        subprocess.call("{0} -textui -jvmArgs \"-Xmx4096m\" -high -sortByClass -xml -output {1} {2}".
                        format(Config.FINDBUGS_PATH, xml_path, scan_path))
