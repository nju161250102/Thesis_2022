import abc

import pandas as pd


class QueryBase(object):
    """
    查询策略基类
    """

    def __init__(self, data_df: pd.DataFrame, max_num: int, name: str):
        """
        :param data_df: 数据集
        :param max_num: 每次采样的最大值
        """
        self.data_df = data_df
        # self.label_series = data_df["label"].copy()
        self.max_num = max_num
        self.name = name

    @abc.abstractmethod
    def query(self, labeled_index_set: set, predict_prob: pd.Series) -> pd.Index:
        """
        :param labeled_index_set: 已知标记的样本索引
        :param predict_prob: 对所有样本的预测概率
        :return:
        """
        pass
