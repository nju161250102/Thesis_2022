from typing import List

import pandas as pd


class BaseLineModel(object):
    """
    BaseLine实验模型基类
    """

    def __init__(self, name: str, train_df: pd.DataFrame, test_df: pd.DataFrame):
        self.name = name
        self.train_df = train_df
        self.test_df = test_df
        self.train_labels = []
        self.test_labels = []

    def rank_labels(self):
        self.train_labels = self._rank_labels(self.train_df)
        self.test_labels = self._rank_labels(self.test_df)

    def _rank_labels(self, data_df: pd.DataFrame) -> List[int]:
        pass
