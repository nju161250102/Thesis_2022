import numpy as np
from sklearn.svm import OneClassSVM

from .ModelBase import ModelBase


class OneClassSvmModel(ModelBase):
    """
    Support Vector Machine Model
    """

    def __init__(self):
        super().__init__("svm")
        self.model = OneClassSVM(kernel="linear", gamma='auto')

    def train(self, x_data: np.ndarray, x_label: np.ndarray):
        self.model.fit(x_data, x_label)

    def predict_label(self, x_data: np.ndarray) -> np.ndarray:
        return 0.5 - self.model.predict(x_data) / 2

    def predict_prob(self, x_data: np.ndarray) -> np.ndarray:
        return np.abs(self.model.decision_function(x_data))
