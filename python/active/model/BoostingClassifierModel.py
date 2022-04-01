import numpy as np
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier

from .ModelBase import ModelBase


class BoostingClassifierModel(ModelBase):
    """
    Multiply Class Machine Model in scikit-learn
    """

    def __init__(self):
        self.model = AdaBoostClassifier(DecisionTreeClassifier(max_depth=2, min_samples_split=5, min_samples_leaf=5),
                                        algorithm="SAMME.R", n_estimators=50, learning_rate=0.8)
        super().__init__("boosting")

    def train(self, x_data: np.ndarray, x_label: np.ndarray):
        self.model.fit(x_data, x_label)

    def predict_label(self, x_data: np.ndarray) -> np.ndarray:
        return self.model.predict(x_data)

    def predict_prob(self, x_data: np.ndarray) -> np.ndarray:
        prob_result = self.model.predict_proba(x_data)
        return np.apply_along_axis(np.max, 1, prob_result)
