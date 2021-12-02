import pandas as pd


class FeatureCategory(object):
    """
    特征类别，作为特征提取的父类
    """

    def __init__(self, alarm_df: pd.DataFrame, project_name: str, version: str):
        """
        :param alarm_df: 当前版本的所有警告
        :param project_name: 项目名称
        :param version: 项目版本
        """
        self.alarm_df = alarm_df.copy()
        self.project_name = project_name
        self.version = version

    def get_feature_df(self) -> pd.DataFrame:
        """
        :return: 当前特征类别下的特征矩阵
        """
        pass
