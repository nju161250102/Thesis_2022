import numpy as np
import sklearn.ensemble._base as base
import sklearn.ensemble._stacking as s
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression

from .ModelBase import ModelBase
from Logger import LOG


def modified_fit_single_estimator(estimator, X, y, sample_weight=None, message_clsname=None, message=None):
    """Private function used to fit an estimator within a job."""
    if sample_weight is not None:
        try:
            with base._print_elapsed_time(message_clsname, message):
                estimator.fit(X, y, sample_weight=sample_weight)
        except TypeError as exc:
            if "unexpected keyword argument 'sample_weight'" in str(exc):
                raise TypeError(
                    "Underlying estimator {} does not support sample weights.".format(
                        estimator.__class__.__name__
                    )
                ) from exc
            raise
    else:
        majority_indices = np.argwhere(y == 0).reshape(-1)
        minority_indices = np.argwhere(y == 1).reshape(-1)
        minority_indices = np.repeat(minority_indices, [int(len(majority_indices) / len(minority_indices))
                                                        for _ in range(len(minority_indices))], axis=0)

        indices = np.concatenate((minority_indices, majority_indices))
        # LOG.info(y[indices])
        with base._print_elapsed_time(message_clsname, message):
            estimator.fit(X[indices], y[indices])
    return estimator


class StackingClassifierModel(ModelBase):
    """
    Bagging Classifier Model
    """

    def __init__(self):
        super().__init__("stacking")
        s._fit_single_estimator = modified_fit_single_estimator
        self.model = s.StackingClassifier([
            ("svm", CalibratedClassifierCV(base_estimator=LinearSVC(max_iter=20000))),
            ("dt", DecisionTreeClassifier()),
            ("nb", GaussianNB()),
            ("mlp", MLPClassifier(max_iter=1000))
        ], final_estimator=LogisticRegression(), cv=2)

    def train(self, x_data: np.ndarray, x_label: np.ndarray):
        # self.model.cv = min(5, len(x_data))
        # LOG.info(self.model.cv)
        self.model.fit(x_data, x_label)

    def predict_label(self, x_data: np.ndarray) -> np.ndarray:
        return self.model.predict(x_data)

    def predict_prob(self, x_data: np.ndarray) -> np.ndarray:
        return np.abs(self.model.decision_function(x_data))
