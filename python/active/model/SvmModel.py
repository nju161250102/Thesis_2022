import numpy as np
import pandas as pd
from sklearn.svm import SVC

from .ModelBase import ModelBase


class SvmModel(ModelBase):
    """
    Support Vector Machine Model
    """

    def __init__(self):
        super().__init__("svm")
        self.model = SVC(kernel="linear", decision_function_shape="ovr", probability=True, tol=0.0001)

    def train(self, data_df: pd.DataFrame):
        x_data, x_label = self.data_handler.preprocess(data_df, True)
        print(x_data)
        self.model.fit(x_data, x_label)

    def predict_label(self, data_df: pd.DataFrame) -> pd.Series:
        return pd.Series(self.model.predict(self.data_handler.preprocess(data_df, False))[0], index=data_df.index)

    def predict_prob(self, data_df: pd.DataFrame) -> pd.Series:
        prob_result = self.model.predict_proba(self.data_handler.preprocess(data_df, False)[0])
        return pd.Series(np.apply_along_axis(np.max, 1, prob_result), index=data_df.index)
