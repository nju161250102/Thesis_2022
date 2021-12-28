import numpy as np
import sklearn.ensemble._bagging as bagging
from sklearn.ensemble import BaggingClassifier

from .ModelBase import ModelBase


def modified_parallel_build_estimators(
    n_estimators, ensemble, X, y, sample_weight, seeds, total_n_estimators, verbose
):
    """
    修改了原有BaggingClassifier的抽样过程，使得抽样结果是较为平衡的数据集
    原代码：https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/ensemble/_bagging.py
    Private function used to build a batch of estimators within a job.
    """
    # Retrieve settings
    n_samples, n_features = X.shape
    max_features = ensemble._max_features
    max_samples = ensemble._max_samples
    bootstrap = ensemble.bootstrap
    bootstrap_features = ensemble.bootstrap_features
    support_sample_weight = bagging.has_fit_parameter(ensemble.base_estimator_, "sample_weight")
    if not support_sample_weight and sample_weight is not None:
        raise ValueError("The base estimator doesn't support sample weight")

    # Build estimators
    estimators = []
    estimators_features = []

    # 固定选择的少数类样本
    X_marjority = X[y == 0]
    X_minority = X[y == 1]

    for i in range(n_estimators):
        if verbose > 1:
            print(
                "Building estimator %d of %d for this parallel run (total %d)..."
                % (i + 1, n_estimators, total_n_estimators)
            )

        random_state = seeds[i]
        estimator = ensemble._make_estimator(append=False, random_state=random_state)

        # Draw random feature, sample indices
        # 改为从少数类与多数类中分别抽样
        if len(X_minority) > int(max_samples / 2):
            # 少数类样本较为充足时可以抽取近似1：1的样本
            minority_indices = bagging._generate_bagging_indices(
                random_state,
                bootstrap_features,
                bootstrap,
                n_features,
                X_minority.shape[0],
                max_features,
                int(max_samples / 2),
            )[1]
        else:
            # 否则只能选择所有少数类样本
            minority_indices = np.arange(X_minority.shape[0])
        features, majority_indices = bagging._generate_bagging_indices(
            random_state,
            bootstrap_features,
            bootstrap,
            n_features,
            X_marjority.shape[0],
            max_features,
            max_samples - int(max_samples / 2),
        )
        # 拼接数据集和下标，注意后续下标要加上偏移量
        X = np.concatenate((X_minority, X_marjority))
        indices = np.concatenate((minority_indices, majority_indices + len(X_minority)))

        # Draw samples, using sample weights, and then fit
        if support_sample_weight:
            if sample_weight is None:
                curr_sample_weight = np.ones((n_samples,))
            else:
                curr_sample_weight = sample_weight.copy()

            if bootstrap:
                sample_counts = np.bincount(indices, minlength=n_samples)
                curr_sample_weight *= sample_counts
            else:
                not_indices_mask = ~bagging.indices_to_mask(indices, n_samples)
                curr_sample_weight[not_indices_mask] = 0

            estimator.fit(X[:, features], y, sample_weight=curr_sample_weight)

        else:
            estimator.fit((X[indices])[:, features], y[indices])

        estimators.append(estimator)
        estimators_features.append(features)

    return estimators, estimators_features


class BaggingClassifierModel(ModelBase):
    """
    Bagging Classifier Model
    """

    def __init__(self):
        super().__init__("bagging")
        bagging._parallel_build_estimators = modified_parallel_build_estimators
        self.model = BaggingClassifier(bootstrap=False, n_estimators=10, max_samples=0.1)

    def train(self, x_data: np.ndarray, x_label: np.ndarray):
        self.model.fit(x_data, x_label)

    def predict_label(self, x_data: np.ndarray) -> np.ndarray:
        return 0.5 - self.model.predict(x_data) / 2

    def predict_prob(self, x_data: np.ndarray) -> np.ndarray:
        return np.abs(self.model.decision_function(x_data))
