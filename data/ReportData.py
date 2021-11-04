from utils import LOG, CommandUtils, PathUtils


class ReportData(object):
    """
    扫描报告的相关操作
    """

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
