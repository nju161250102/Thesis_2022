from typing import List

import pandas as pd

from .BaseLineModel import BaseLineModel


class BaseLineE(BaseLineModel):
    """
    随机排序
    """

    def __init__(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        super(BaseLineE, self).__init__("Rank", train_df, test_df)
        self.rank_labels()

    def _rank_labels(self, data_df: pd.DataFrame) -> List[int]:
        data_df.sort_values("rank", inplace=True)
        return data_df["label"].to_list()
