import random
from typing import List

import pandas as pd

from .BaseLineModel import BaseLineModel


class BaseLineD(BaseLineModel):
    """
    随机排序
    """

    def __init__(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        super(BaseLineD, self).__init__("Random", train_df, test_df)
        self.rank_labels()

    def _rank_labels(self, data_df: pd.DataFrame) -> List[int]:
        labels = data_df["label"].to_list()
        random.shuffle(labels)
        return labels
