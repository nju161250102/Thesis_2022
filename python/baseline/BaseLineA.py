from collections import defaultdict
from typing import List

import pandas as pd

from model import Alarm
from .BaseLineModel import BaseLineModel


class BaseLineA(BaseLineModel):
    """
    根据论文中的公式计算警告的ATA和CL值进行排序。

    实验来源：Adaptively Ranking Alerts Generated from Automated Static Analysis
    """

    def __init__(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        super(BaseLineA, self).__init__("ATA", train_df, test_df)
        self.BC_type, self.DC_type = self._calculate_context("addr")
        self.BC_sf, self.DC_sf = self._calculate_context("_package")
        self.BC_c, self.DC_c = self._calculate_context("_class")
        self.BC_m, self.DC_m = self._calculate_context("_method")
        self.rank_labels()

    def _calculate_context(self, key_word: str):
        # 警告数目
        warnings_num = self.train_df.groupby(key_word).count().iloc[:, 0].to_dict(into=defaultdict(int))
        # 误报数目
        false_alarms_num = self.train_df[self.train_df["label"] == Alarm.FP].groupby(key_word).count().iloc[:,
                           0].to_dict(into=defaultdict(int))
        # BC
        baseline_context = defaultdict(int)
        baseline_context.update({k: v / len(self.train_df) for k, v in warnings_num.items()})
        # DC
        developer_context = defaultdict(int)
        developer_context.update({k: (2 * false_alarms_num[k] - v) / v for k, v in warnings_num.items()})
        return baseline_context, developer_context

    def _rank_labels(self, data_df: pd.DataFrame) -> List[int]:
        beta_BC, beta_DC = 0.5, 0.5
        gama_sf, gama_c, gama_m = 0.06, 0.65, 0.29

        def calculate_ATA(row, _self):
            return beta_BC * _self.BC_type[row["addr"]] + beta_DC * _self.DC_type[row["addr"]]

        def calculate_CL(row, _self):
            return beta_BC * (gama_sf * _self.BC_sf[row["_package"]] + gama_c * _self.BC_c[row["_class"]] + gama_m *
                              _self.BC_m[row["_method"]]) + \
                   beta_DC * (gama_sf * _self.DC_sf[row["_package"]] + gama_c * _self.DC_c[row["_class"]] + gama_m *
                              _self.DC_m[row["_method"]])

        data_df["rank_score"] = data_df.apply(lambda row: (calculate_ATA(row, self)) / 2,
                                              axis=1)
        data_df.sort_values("rank_score", inplace=True)
        return data_df["label"].to_list()
