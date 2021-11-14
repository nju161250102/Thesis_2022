import copy
import pandas as pd
from xml.etree import ElementTree

from typing import List, Dict

from model import Alarm, ProjectConfig
from utils import LOG, CommandUtils, PathUtils


class ReportData(object):
    """
    漏洞扫描报告的相关操作
    """

    @staticmethod
    def scan_jar(config: ProjectConfig):
        """
        扫描同一个项目下不同版本的Jar包
        :param config: 项目配置dict
        """
        PathUtils.rebuild_dir(PathUtils.report_path(config.name))
        for version in config.versions:
            if config.select and version.number not in config.select:
                continue
            target_jar = PathUtils.project_path(config.name, version.target)
            CommandUtils.find_bugs(target_jar, PathUtils.report_path(config.name, version.number + ".xml"))
            LOG.info("Scan version finished: " + version.number)

    @staticmethod
    def scan_all_jars(config: Dict[str, ProjectConfig]):
        """
        扫描文件内部所有的Jar包
        :param config: 所有配置
        """
        for project, project_config in config.items():
            LOG.info("Start scan project: " + project)
            ReportData.scan_jar(project_config)

    @staticmethod
    def read_report(project_name: str, version: str) -> List[Alarm]:
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
                alarm = Alarm()
                alarm.category = item.get("category")
                alarm.type = item.get("type")
                alarm.rank = item.get("rank")
                alarm.class_name = item.find("Class").get("classname")
                alarm.version = version
                # Method中存在与Class对应的方法，补充信息
                for method_node in item.findall("Method"):
                    if method_node.get("classname") == alarm.class_name:
                        alarm.method = method_node.get("name")
                        alarm.path = method_node.find("SourceLine").get("sourcepath")
                        break
                # Method中没有出现与Class对应的方法，忽略这个警告
                else:
                    continue
                # 保存有精确漏洞行的警告，可能存在多个
                for line_node in item.iterfind("SourceLine"):
                    if line_node.get("classname") == alarm.class_name:
                        start = int(line_node.get("start"))
                        end = int(line_node.get("end"))
                        if start == end:
                            alarm.location = start
                            result.append(copy.deepcopy(alarm))
        return result

    @staticmethod
    def read_all_reports(config: Dict[str, ProjectConfig]):
        """
        读取所有扫描文件并保存为csv
        :param config: 所有配置
        """
        for project, project_config in config.items():
            reports = []
            for version in project_config.select:
                reports.extend(ReportData.read_report(project_config.name, version))
            df = pd.DataFrame([alarm.__dict__ for alarm in reports])
            df.to_csv(PathUtils.report_path(project_config.name + ".csv"), index_label="index")

    @staticmethod
    def update_all_alarms(config: Dict[str, ProjectConfig]):
        """
        格式化警告涉及的java文件，并更新行号
        :param config: 所有配置
        """
        for project, project_config in config.items():
            df = pd.read_csv(PathUtils.report_path(project_config.name + ".csv"), index_col="index")
            for row in df.itertuples():
                # java文件地址
                java_path = PathUtils.project_path(project_config.name, row.version, row.path)
                new_location = CommandUtils.reformat_java(java_path, row.location)
                if new_location < 0:
                    LOG.warn("No match line in {0}-{1}".format(project_config.name, row.Index))
                    continue
                df.loc[row.Index, "location"] = new_location
            df.to_csv(PathUtils.report_path(project_config.name + ".csv"), index_label="index")
