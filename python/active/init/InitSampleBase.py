import pandas as pd


class InitSampleBase(object):
    """
    初始化采样策略的基类
    """

    def __init__(self, name: str):
        self.name = name

    def get_sample_index(self, data_df: pd.DataFrame) -> pd.Index:
        """
        :return: 采样样本的索引列表
        """
        pass
