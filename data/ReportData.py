from xml.etree import ElementTree

from utils import LOG, CommandUtils, PathUtils


class ReportData(object):
    """
    漏洞扫描报告的相关操作
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

    @staticmethod
    def read_report(project_name: str, version: str) -> list:
        """
        读取xml报告，获取漏洞列表
        :param project_name: 项目名
        :param version: 版本名
        :return: 漏洞列表
        """
        result = []
        xml_doc = ElementTree.parse(PathUtils.report_path(project_name, version + ".xml"))
        for item in xml_doc.iterfind("BugInstance"):
            # 保证结果中有漏洞行
            if item.find("SourceLine") is not None:
                bug = {
                    "Category": item.get("category"),
                    "Type": item.get("type"),
                    "Rank": item.get("rank"),
                    "Class": item.find("Class").get("classname"),
                    # 误报标记，-1未知，0误报，1正报
                    "Label": -1,
                    "Version": version
                }
                for method_node in item.findall("Method"):
                    # Method中存在与Class对应的方法，补充信息
                    if method_node.get("classname") == bug["Class"]:
                        bug["Method"] = method_node.get("name")
                        bug["Signature"] = method_node.get("signature")
                        bug["Start"] = int(method_node.find("SourceLine").get("start"))
                        bug["End"] = int(method_node.find("SourceLine").get("end"))
                        break
                # Method中没有出现与Class对应的方法，忽略这个警告
                else:
                    continue
                # 暂不记录漏洞行
                # for source_line in item.findall("SourceLine"):
                #     if bug["Start"] <= int(source_line.get("start")) <= bug["End"]:
                #         bug["Line"] = int(source_line.get("start"))
                result.append(bug)
        return result
