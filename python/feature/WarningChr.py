import pandas as pd

from Logger import LOG
from model import FeatureType
from .FeatureCategory import FeatureCategory


class WarningChr(FeatureCategory):
    """
    警告特征 - Warning Characteristics
    """

    def __init__(self, alarm_df: pd.DataFrame, project_name: str, version: str):
        super().__init__(alarm_df, project_name, version)
        LOG.info("WarningChr in project {0}, version {1}".format(project_name, version))

    def get_feature_df(self) -> pd.DataFrame:
        columns = [self._warning_type(), self._warning_priority(), self._warning_rank(), self._num_in_method(), self._num_in_class(), self._num_in_package()]
        feature_df = pd.DataFrame({s.name: s for s in columns}, index=self.alarm_df.index)
        return feature_df

    def _warning_type(self) -> pd.Series:
        """
        F90 warning type
        """
        return self._warning_property("type", FeatureType.F90)

    def _warning_priority(self) -> pd.Series:
        """
        F91 warning priority
        """
        return self._warning_property("priority", FeatureType.F91)

    def _warning_rank(self) -> pd.Series:
        """
        F92 warning rank
        """
        return self._warning_property("rank", FeatureType.F92)

    def _num_in_method(self) -> pd.Series:
        """
        F94 number of warnings in the method
        """
        method_num = self.alarm_df.groupby(["class_name", "method"])["version"].count()
        series = self.alarm_df.apply(lambda row: method_num[(row["class_name"], row["method"])], axis=1)
        series.name = FeatureType.F94
        return series

    def _num_in_class(self) -> pd.Series:
        """
        F95 number of warnings in the class
        """
        # 内部类以外部类为准，取分隔符$前字符串
        self.alarm_df["class"] = self.alarm_df["class_name"].map(lambda s: s.split("$")[0])
        class_num = self.alarm_df.groupby("class")["version"].count()
        series = self.alarm_df["class"].map(lambda s: class_num[s])
        series.name = FeatureType.F95
        return series

    def _num_in_package(self) -> pd.Series:
        """
        F96 number of warnings in the package
        """
        # 取最后一个.号前面的字符串作为包名
        self.alarm_df["package"] = self.alarm_df["class_name"].map(lambda s: ".".join(s.split(".")[:-1]))
        package_num = self.alarm_df.groupby("package")["version"].count()
        series = self.alarm_df["package"].map(lambda s: package_num[s])
        series.name = FeatureType.F96
        return series

    def _warning_property(self, column: str, feature_type: str) -> pd.Series:
        """
        获取警告自身属性列
        """
        series = self.alarm_df[column].copy()
        series.name = feature_type
        return series
