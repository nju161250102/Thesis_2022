import numpy as np
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import CategoricalNB
from sklearn.neural_network import MLPClassifier
from sklearn.calibration import CalibratedClassifierCV

from .ModelBase import ModelBase


class MultiplyClassModel(ModelBase):
    """
    Multiply Class Machine Model in scikit-learn
    """

    def __init__(self, name: str):
        model_dict = {
            "svm": CalibratedClassifierCV(base_estimator=LinearSVC()),
            "dt": DecisionTreeClassifier(),
            "nb": CategoricalNB(),
            "mlp": MLPClassifier(max_iter=1000)
        }
        # 默认的分类器
        if name not in model_dict.keys():
            name = "svm"
        self.model = model_dict[name]
        super().__init__("svm")

    def train(self, x_data: np.ndarray, x_label: np.ndarray):
        self.model.fit(x_data, x_label)

    def predict_label(self, x_data: np.ndarray) -> np.ndarray:
        return self.model.predict(x_data)

    def predict_prob(self, x_data: np.ndarray) -> np.ndarray:
        prob_result = self.model.predict_proba(x_data)
        return np.apply_along_axis(np.max, 1, prob_result)
