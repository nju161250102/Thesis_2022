import pandas as pd

from Logger import LOG
from model import Alarm, FeatureType, WarningType
from .FeatureCategory import FeatureCategory


class WarningCmb(FeatureCategory):
    """
    警告联合 - Warning Combination
    """

    def __init__(self, alarm_df: pd.DataFrame, project_name: str, version: str):
        super().__init__(alarm_df, project_name, version)
        LOG.info("WarningCmb in project {0}, version {1}".format(project_name, version))
        # 统计各模式下正误报数目
        self.pattern_dict = {p: {"F": 0, "T": 0} for p in WarningType.type_list}
        for index, df in alarm_df.groupby(["type", "label"]):
            if index[0] not in self.pattern_dict.keys():
                continue
            if index[1] == Alarm.FP:
                self.pattern_dict[index[0]]["F"] += 1
            elif index[1] == Alarm.TP:
                self.pattern_dict[index[0]]["T"] += 1
        for pattern in self.pattern_dict.keys():
            kind = WarningType.type_dict[pattern]
            F, T = self.pattern_dict[pattern]["F"], self.pattern_dict[pattern]["T"]
            self.pattern_dict[pattern]["S"] = F + T
            D = F / (F + T) if F + T > 0 else 0
            self.pattern_dict[pattern]["D"] = D
            self.pattern_dict[pattern]["V"] = D * (1 - D) / len(WarningType.kind_dict[kind])
        #
        self.kind_dict = {k: {"D": 0, "S": 0} for k in WarningType.kind_dict.keys()}
        for kind in self.kind_dict.keys():
            kind_sum = sum(map(lambda p: self.pattern_dict[p]["S"], WarningType.kind_dict[kind]))
            if kind_sum > 0:
                self.kind_dict[kind]["D"] = sum(map(lambda p: self.pattern_dict[p]["D"] * self.pattern_dict[p]["S"], WarningType.kind_dict[kind])) / kind_sum
            else:
                self.kind_dict[kind]["D"] = 0
            if len(WarningType.kind_dict[kind]) == 1:
                self.kind_dict[kind]["S"] = 0
            else:
                self.kind_dict[kind]["S"] = sum(map(lambda p: pow(self.pattern_dict[p]["D"] - self.kind_dict[kind]["D"], 2), WarningType.kind_dict[kind])) / \
                                            (len(WarningType.kind_dict[kind]) - 1)

    def get_feature_df(self) -> pd.DataFrame:
        def func(row: pd.Series, warning_cmb: WarningCmb) -> pd.Series:
            pattern = row["type"]
            kind = WarningType.type_dict[pattern]
            return pd.Series({
                FeatureType.F112: warning_cmb.pattern_dict[pattern]["D"],
                FeatureType.F113: warning_cmb.pattern_dict[pattern]["V"],
                FeatureType.F114: warning_cmb.kind_dict[kind]["D"],
                FeatureType.F115: warning_cmb.kind_dict[kind]["S"]
            })

        return self.alarm_df.apply(func, axis=1, args=(self,))
