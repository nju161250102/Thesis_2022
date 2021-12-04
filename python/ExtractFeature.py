"""
项目警告特征提取脚本
"""
import pandas as pd

from feature import CodeChr, WarningChr
from utils import PathUtils, JsonUtils

if __name__ == "__main__":
    for project_name, project_config in JsonUtils.read_projects(PathUtils.join_path("project.json")).items():
        df = pd.read_csv(PathUtils.report_path(project_config.name + ".csv"), index_col="index")
        result_df = pd.DataFrame()
        for version, group_df in df.groupby("version"):
            feature_df = pd.DataFrame()
            code_chr_df = CodeChr(group_df, project_config.name, version).get_feature_df()
            warning_chr_df = WarningChr(group_df, project_config.name, version).get_feature_df()
            # 合并不同类的特征DataFrame
            feature_df = feature_df.join(code_chr_df, how="right")
            feature_df = feature_df.join(warning_chr_df, how="right")
            # 合并到项目整体DataFrame
            result_df = result_df.append(feature_df)
        result_df.to_csv(PathUtils.feature_path(project_config.name + ".csv"), index_label="index")