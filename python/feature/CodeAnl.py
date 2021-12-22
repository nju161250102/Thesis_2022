import pandas as pd

from Logger import LOG
from model import FeatureType
from utils import CommandUtils, PathUtils
from .FeatureCategory import FeatureCategory


class CodeAnl(FeatureCategory):
    """
    代码分析 - Code Analysis
    """

    def __init__(self, alarm_df: pd.DataFrame, project_name: str, version: str):
        super().__init__(alarm_df, project_name, version)
        LOG.info("CodeAnl in project {0}, version {1}".format(project_name, version))
        self.info_dict = CommandUtils.analyse_project(PathUtils.project_path(project_name, version))

    def get_feature_df(self) -> pd.DataFrame:
        # 布尔值转数值
        def bool_to_int(d: dict, k: str):
            if d is None:
                return 0
            else:
                return int(d[k])
        def func(row: pd.Series, code_anl: CodeAnl) -> pd.Series:
            class_name = row["class_name"].replace("$", ".")
            class_info = code_anl.info_dict.get(class_name)
            method_info = code_anl.info_dict.get(class_name + "." + row["method"])
            return pd.Series({
                FeatureType.F84_public: bool_to_int(method_info, "public"),
                FeatureType.F84_default: bool_to_int(method_info, "default"),
                FeatureType.F84_protected: bool_to_int(method_info, "protected"),
                FeatureType.F84_private: bool_to_int(method_info, "private"),
                FeatureType.F85: method_info.get("returnType") if method_info else None,
                FeatureType.F86_static: bool_to_int(method_info, "public"),
                FeatureType.F86_final: bool_to_int(method_info, "final"),
                FeatureType.F86_abstract: bool_to_int(method_info, "abstract"),
                FeatureType.F86_protected: bool_to_int(method_info, "protected"),

                FeatureType.F87_public: bool_to_int(class_info, "public"),
                FeatureType.F87_default: bool_to_int(class_info, "default"),
                FeatureType.F87_protected: bool_to_int(class_info, "protected"),
                FeatureType.F87_private: bool_to_int(class_info, "private"),
                FeatureType.F88_abstract: bool_to_int(class_info, "abstract"),
                FeatureType.F88_interface: bool_to_int(class_info, "interface"),
                FeatureType.F88_enum: bool_to_int(class_info, "enum")
            })

        return self.alarm_df.apply(func, axis=1, args=(self,))
