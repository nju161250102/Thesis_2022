from Config import Config
from utils import LOG, CommandUtils, PathUtils


class ReportData(object):

    @staticmethod
    def scan_project(project_name: str, commit=None, version=0):
        """
        [废弃] 进入项目文件夹之后切换版本并编译和扫描
        :param project_name: 项目名称
        :param commit: 版本SHA
        :param version: 版本名
        """
        if project_name not in Config.SCAN_CONF.keys():
            LOG.error("{0} not found in config".format(project_name))
            return
        conf = Config.SCAN_CONF[project_name]
        project_path = PathUtils.project_path(project_name)
        scan_path = PathUtils.project_path(project_name, conf["target"])
        xml_path = PathUtils.project_path("{0}_{1}.xml".format(project_name, version))
        # 切换项目版本
        if commit is None:
            CommandUtils.run("git checkout " + conf["default"], project_path)
        else:
            CommandUtils.run("git checkout " + commit, project_path)
        # 自动构建
        CommandUtils.run(conf["build"], project_path)
        # 扫描漏洞
        CommandUtils.find_bugs(scan_path, xml_path)

    @staticmethod
    def scan_jar(config: dict):
        """
        扫描同一个项目下不同版本的Jar包
        :param config: 项目配置dict
        """
        PathUtils.rebuild_dir(PathUtils.report_path(config["name"]))
        for version in config["versions"]:
            if "select" in config.keys() and version not in config["select"]:
                continue
            target_jar = PathUtils.project_path(config["name"], version["target"])
            CommandUtils.find_bugs(target_jar, PathUtils.report_path(config["name"], version + ".xml"))
            LOG.info("version: " + version)

    @staticmethod
    def scan_all_jar(config: dict):
        """
        扫描文件内部所有的Jar包
        :param config: 所有配置
        """
        for project, project_config in config.items():
            LOG.info("Start scan project: " + project)
            ReportData.scan_jar(project_config)

    @staticmethod
    def xml_to_csv():
        pass
