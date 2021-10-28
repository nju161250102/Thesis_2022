import os

from Config import Config
from utils import LOG, CommandUtils


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
            CommandUtils.run("git checkout " + conf["default"], project_path)
        else:
            CommandUtils.run("git checkout " + commit, project_path)
        # 自动构建
        CommandUtils.run(conf["build"], project_path)
        # 扫描漏洞
        CommandUtils.run("{0} -textui -jvmArgs \"-Xmx4096m\" -high -sortByClass -xml -output {1} {2}".
                         format(Config.FINDBUGS_PATH, xml_path, scan_path))

    @staticmethod
    def xml_to_csv():
        pass
