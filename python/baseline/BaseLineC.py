from typing import List

import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

from model import FeatureType
from .BaseLineModel import BaseLineModel


class BaseLineC(BaseLineModel):

    def __init__(self, train_df: pd.DataFrame, test_df: pd.DataFrame):
        super(BaseLineC, self).__init__("KNN", train_df, test_df)
        self.choose_feature_list = FeatureType.to_str_list(
            [FeatureType.F94, FeatureType.F95, FeatureType.F96, FeatureType.F22, FeatureType.F23])
        self.model = KNeighborsClassifier(n_neighbors=5)
        self.model.fit(self.train_df[self.choose_feature_list].values, self.train_df["label"])
        self.rank_labels()

    def _rank_labels(self, data_df: pd.DataFrame) -> List[int]:
        return self.model.predict(data_df[self.choose_feature_list].values).tolist()
