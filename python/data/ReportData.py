import copy
from typing import List, Dict
from xml.etree import ElementTree

import numpy as np
import pandas as pd

from Logger import LOG
from model import Alarm, ProjectConfig
from utils import CommandUtils, PathUtils


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
        PathUtils.rebuild_dir(PathUtils.report_path(config.name), skip=True)
        for version in config.versions:
            if config.select and version.number not in config.select:
                continue
            # 跳过已经扫描过的不再扫描
            if PathUtils.exist_path("report", config.name, version.number + ".xml"):
                continue
            target_jar = PathUtils.project_path(config.name, version.target)
            CommandUtils.run_findbugs(target_jar, PathUtils.report_path(config.name, version.number + ".xml"))
            LOG.info("Scan version: " + version.number)

    @staticmethod
    def scan_all_jars(config: Dict[str, ProjectConfig]):
        """
        扫描文件内部所有的Jar包
        :param config: 所有配置
        """
        for project, project_config in config.items():
            LOG.info("Scan project: " + project)
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
                try:
                    alarm = Alarm()
                    alarm.category = item.get("category")
                    alarm.priority = item.get("priority")
                    alarm.rank = item.get("rank")
                    alarm.type = item.get("type")
                    alarm.class_name = item.find("Class").get("classname")
                    alarm.version = version
                    # Method中存在与Class对应的方法，补充信息
                    for method_node in item.findall("Method"):
                        if method_node.get("classname") == alarm.class_name:
                            alarm.method = method_node.get("name")
                            alarm.signature = method_node.get("signature")
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
                            # [不同的SourceLine可能会出现相同的行号，需要避免重复添加]
                            if start == end and alarm.location != start:
                                alarm.location = start
                                result.append(copy.deepcopy(alarm))
                except Exception as e:
                    LOG.exception(e)
        # 按顺序标记警告编号
        for index, alarm in enumerate(result):
            alarm.index = "{0}#{1}#{2}".format(project_name, version, index)
        return result

    @staticmethod
    def read_all_reports(config: Dict[str, ProjectConfig]):
        """
        读取所有项目的扫描结果文件并按项目分别保存为csv文件
        注意：如果目标csv文件已经存在会自动跳过，节约时间
        :param config: 所有配置
        """
        for project, project_config in config.items():
            # 如果目标csv文件已经存在则自动跳过
            if PathUtils.exist_path("report", project_config.name + ".csv"):
                continue
            reports = []
            LOG.info("Read project: " + project_config.name)
            for version in project_config.select:
                LOG.info("Read version: " + version)
                reports.extend(ReportData.read_report(project_config.name, version))
            df = pd.DataFrame([alarm.__dict__ for alarm in reports])
            df.to_csv(PathUtils.report_path(project_config.name + ".csv"), index=False)

    @staticmethod
    def update_all_alarms(config: Dict[str, ProjectConfig]):
        """
        对警告涉及的 java 文件进行格式化，为了之后做差异块比较
        新文件会被保存到数据文件夹下的 file/{project_name} 目录，文件名为警告ID
        新文件中对应的行号会保存到 new_location 字段
        :param config: 所有配置
        """
        for project, project_config in config.items():
            df = pd.read_csv(PathUtils.report_path(project_config.name + ".csv"), index_col="index")
            PathUtils.rebuild_dir(PathUtils.file_path(project_config.name))
            # 以每个版本中的每个文件为单位进行处理
            for index, group_df in df.groupby(["path", "version"]):
                lines = group_df["location"].tolist()
                java_path = PathUtils.project_path(project_config.name, index[1], index[0])
                new_java_path = PathUtils.file_path(project_config.name, index[1], index[0])
                new_location = CommandUtils.reformat_java(java_path, new_java_path, lines)
                group_df["new_location"] = np.array(new_location)
                for row in group_df.itertuples():
                    df.at[row.Index, "new_location"] = row.new_location
            df.to_csv(PathUtils.report_path(project_config.name + ".csv"))
