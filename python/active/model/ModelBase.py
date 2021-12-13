import abc

import pandas as pd

from ..DataHandler import DataHandler


class ModelBase(object):

    def __init__(self, name: str):
        self.name = name
        self.data_handler = DataHandler()

    @abc.abstractmethod
    def train(self, data_df: pd.DataFrame):
        """
        训练模型
        :param data_df: 数据集
        """
        pass

    @abc.abstractmethod
    def predict_label(self, data_df: pd.DataFrame) -> pd.Series:
        """
        使用模型预测分类
        :param data_df: 仅包含特征的数据集
        :return: 预测分类
        """
        pass

    @abc.abstractmethod
    def predict_prob(self, data_df: pd.DataFrame) -> pd.Series:
        """
        使用模型预测概率
        :param data_df: 仅包含特征的数据集
        :return: 预测概率
        """
        pass
