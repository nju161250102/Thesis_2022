from collections import defaultdict
from typing import List

import pandas as pd

from feature import WarningCmb
from .BaseLineModel import BaseLineModel


class BaseLineB(BaseLineModel):

    def __init__(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        self.pattern_dict = defaultdict(lambda a: {"D": 0})
        self.pattern_dict.update(WarningCmb(train_df, "", "").pattern_dict)
        super(BaseLineB, self).__init__("pattern", train_df, test_df)
        self.rank_labels()

    def _rank_labels(self, data_df: pd.DataFrame) -> List[int]:
        data_df["rank_score"] = data_df.apply(lambda row: self.pattern_dict[row["type"]]["D"], axis=1)
        data_df.sort_values("rank_score", inplace=True)
        return data_df["label"].to_list()
