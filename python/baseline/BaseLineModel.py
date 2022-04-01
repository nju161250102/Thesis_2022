from typing import List

import pandas as pd


class BaseLineModel(object):
    """
    BaseLine实验基类

    调用rank_labels方法将以优先级顺序排列的预测分类结果保存到train_labels和test_labels中。
    子类需要实现具体的_rank_labels方法完成分类预测和排序。
    """

    def __init__(self, name: str, train_df: pd.DataFrame, test_df: pd.DataFrame):
        """
        :param name: 实验名称
        :param train_df: 训练数据集
        :param test_df: 测试数据集
        """
        self.name = name
        self.train_df = train_df
        self.test_df = test_df
        self.train_labels = []
        self.test_labels = []

    def rank_labels(self):
        """
        分别在训练集和测试集上做预测，并按优先级顺序保存
        """
        self.train_labels = self._rank_labels(self.train_df)
        self.test_labels = self._rank_labels(self.test_df)

    def _rank_labels(self, data_df: pd.DataFrame) -> List[int]:
        """
        由子类实现此方法
        """
        pass
