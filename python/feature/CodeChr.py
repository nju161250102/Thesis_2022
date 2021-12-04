import linecache
from xml.etree import ElementTree

import pandas as pd

from Logger import LOG
from model import PackageMetric, ClassMetric, MethodMetric
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
        CommandUtils.run_jhawk(project_path, report_path)
        # 完整包名 -> 度量指标
        self.package_map = {}
        # 完整类名 -> 度量指标
        self.class_map = {}
        # 完整类名.方法名 -> 度量指标
        self.method_map = {}
        # 从xml文件中读取度量数据
        xml_doc = ElementTree.parse(report_path + ".xml")
        for package_item in xml_doc.iterfind("./Packages/Package/Metrics"):
            package_metric = PackageMetric(package_item)
            self.package_map[package_metric.name] = package_metric
        for class_item in xml_doc.iterfind("./Packages/Package/Classes/Class"):
            class_metric = ClassMetric(class_item.find("Metrics"))
            self.class_map[class_metric.name] = class_metric
            for method_item in class_item.iterfind("./Methods/Method/Metrics"):
                method_metric = MethodMetric(method_item)
                self.method_map["{0}.{1}".format(class_metric.name, method_metric.name)] = method_metric
        LOG.info("package: {0}, class: {1}, method: {2}".
                 format(len(self.package_map), len(self.class_map), len(self.method_map)))

    def get_feature_df(self) -> pd.DataFrame:
        def func(row: pd.Series, code_chr: CodeChr) -> pd.Series:
            package_metric = code_chr.package_map[row["package"]]
            class_metric = code_chr.class_map[row["class"]]
            method_metric = code_chr.method_map["{0}.{1}".format(row["class"], row["method"])]
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
                # *注：原论文中的文件级别均被替换为类级别
                # F19 number of non-comment source code statements in method
                "code_method_statement": method_metric.statement_num,
                # *F20 number of non-comment source code statements in class
                "code_class_statement": class_metric.statement_num,
                # F21 number of non-comment source code statements in package
                "code_package_statement": package_metric.statement_num,
                # *F22 number of comment lines in class
                "code_class_comment": class_metric.comment_line,
                # *F23 ratio of comment length and code length in class
                "code_class_comment_ratio": class_metric.comment_line * 1.0 / class_metric.code_line,
                # *F28 number of methods in class
                "code_class_method": class_metric.method_num,
                # F29 number of methods in package
                "code_package_method": package_metric.method_num,
                # F31 number of classed in package
                "code_package_class": package_metric.class_num,
                # F32 space indenting warned line
                "code_indentation": indentation,
                # F33 cyclomatic complexity
                "code_cyclomatic_complexity": method_metric.complexity
            }
            return pd.Series(result)

        return self.alarm_df.apply(func, axis=1, args=(self,))
