import linecache
from xml.etree import ElementTree

import pandas as pd

from Logger import LOG
from model import PackageMetric, ClassMetric, MethodMetric, FeatureType
from utils import CommandUtils, PathUtils
from .FeatureCategory import FeatureCategory


class CodeChr(FeatureCategory):
    """
    代码特征 - Code Characteristic
    """

    def __init__(self, alarm_df: pd.DataFrame, project_name: str, version: str):
        super().__init__(alarm_df, project_name, version)
        LOG.info("CodeChr in project {0}, version {1}".format(project_name, version))
        # 添加一列包名
        self.alarm_df["package"] = self.alarm_df["class_name"].map(lambda s: ".".join(s.split(".")[:-1]))
        project_path = PathUtils.project_path(project_name, version)
        report_path = PathUtils.report_path(project_name, "jhawk#" + version)
        if not PathUtils.exist_path("report", project_name, "jhawk#" + version + ".xml"):
            # 删除使用了枚举关键字的Java文件
            exclude_files = CommandUtils.grep_enumeration(project_path)
            CommandUtils.run_jhawk(project_path, report_path, exclude_files)
        # 完整包名 -> 度量指标
        self.package_map = {}
        # 完整类名 -> 度量指标
        self.class_map = {}
        # 完整类名.方法名 -> 度量指标
        self.method_map = {}
        # 从xml文件中读取度量数据
        if not PathUtils.exist_path("report", project_name, "jhawk#" + version + ".xml"):
            return
        xml_doc = ElementTree.parse(report_path + ".xml")
        for package_item in xml_doc.iterfind("./Packages/Package"):
            self.package_map[package_item.findtext("Name")] = PackageMetric(package_item.find("Metrics"))
        for class_item in xml_doc.iterfind("./Packages/Package/Classes/Class"):
            class_name = "{0}.{1}".format(class_item.findtext("OwningPackage"), class_item.findtext("ClassName"))
            self.class_map[class_name] = ClassMetric(class_item.find("Metrics"))
        for method_item in xml_doc.iterfind("./Packages/Package/Classes/Class/Methods/Method"):
            method_name = "{0}.{1}".format(method_item.findtext("ClassName"), method_item.findtext("Name"))
            self.method_map[method_name] = MethodMetric(method_item.find("Metrics"))
        LOG.info("package: {0}, class: {1}, method: {2}".
                 format(len(self.package_map), len(self.class_map), len(self.method_map)))

    def get_feature_df(self) -> pd.DataFrame:
        def func(row: pd.Series, code_chr: CodeChr) -> pd.Series:
            package_metric = code_chr.package_map.get(row["package"])
            class_metric = code_chr.class_map.get(row["class_name"])
            if row["method"] == "<init>":
                # 获取类或者内部类
                if "$" in row["class_name"]:
                    class_name = row["class_name"].split("$")[-1]
                else:
                    class_name = row["class_name"].split(".")[-1]
                method_metric = code_chr.method_map.get("{0}.{1}".format(row["class_name"], class_name))
            else:
                method_metric = code_chr.method_map.get("{0}.{1}".format(row["class_name"], row["method"]))
            # 读取警告行获取缩进空格数
            warning_line = linecache.getline(
                PathUtils.project_path(code_chr.project_name, code_chr.version, row["path"]), row["location"])
            indentation = 0
            for c in warning_line:
                if c == ' ':
                    indentation += 1
                elif c == '\t':
                    indentation += 4
                else:
                    break
            result = {
                FeatureType.F19: method_metric.statement_num if method_metric else None,
                FeatureType.F20: class_metric.statement_num if class_metric else None,
                FeatureType.F21: package_metric.statement_num if package_metric else None,
                FeatureType.F22: class_metric.comment_line if class_metric else None,
                FeatureType.F23: class_metric.comment_line * 1.0 / class_metric.code_line if class_metric else None,
                FeatureType.F28: class_metric.method_num if class_metric else None,
                FeatureType.F29: package_metric.method_num if package_metric else None,
                FeatureType.F31: package_metric.class_num if package_metric else None,
                FeatureType.F32: indentation,
                FeatureType.F33: method_metric.complexity if method_metric else None
            }
            return pd.Series(result)

        return self.alarm_df.apply(func, axis=1, args=(self,))
