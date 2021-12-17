import abc

import numpy as np


class ModelBase(object):

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    def train(self, x_data: np.ndarray, x_label: np.ndarray):
        """
        训练模型
        """
        pass

    @abc.abstractmethod
    def predict_label(self, x_data: np.ndarray) -> np.ndarray:
        """
        使用模型预测分类
        :return: 预测分类
        """
        pass

    @abc.abstractmethod
    def predict_prob(self, x_data: np.ndarray) -> np.ndarray:
        """
        使用模型预测概率
        :return: 预测概率
        """
        pass
