from model import ProjectConfig, WarningType
from .PathUtils import PathUtils
from .JsonUtils import JsonUtils
import pandas as pd


class DataUtils(object):

    @staticmethod
    def iter_report_df():
        for project_name, project_config in JsonUtils.read_projects(PathUtils.join_path("project.json")).items():
            yield DataUtils._read_report_df(project_config)

    @staticmethod
    def train_and_test_df(project_config: ProjectConfig):
        report_df = DataUtils._read_report_df(project_config)
        for i in range(1, len(project_config.select) - 1):
            yield project_config.select[i], report_df[report_df["version"] < project_config.select[i]].copy(), \
                  report_df[report_df["version"] == project_config.select[i]].copy()

    @staticmethod
    def to_feature_df(project_config: ProjectConfig, index: pd.Index):
        feature_df = pd.read_csv(PathUtils.feature_path(project_config.name + ".csv"), index_col="index")
        return feature_df.loc[feature_df.index.intersection(index)]

    @staticmethod
    def read_project_config(project_name: str = None):
        config_dict = JsonUtils.read_projects(PathUtils.join_path("project.json"))
        return config_dict[project_name] if project_name else config_dict.values()

    @staticmethod
    def _read_report_df(project_config: ProjectConfig):
        report_df = pd.read_csv(PathUtils.report_path(project_config.name + ".csv"), index_col="index",
                                dtype={"next": object})
        version_type = pd.CategoricalDtype(project_config.select, ordered=True)
        report_df["version"] = report_df["version"].astype(version_type)
        report_df["addr"] = report_df.apply(lambda row: WarningType.to_addr(row["type"]), axis=1)
        report_df["_package"] = report_df["class_name"].map(lambda s: ".".join(s.split(".")[:-1]))
        report_df["_class"] = report_df["class_name"].map(lambda s: s.split("$")[0])
        report_df["_method"] = report_df.apply(lambda row: row["class_name"] + "." + row["method"], axis=1)
        return report_df
