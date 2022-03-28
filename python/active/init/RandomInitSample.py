import random

import pandas as pd

from Logger import LOG
from model import Alarm
from .InitSampleBase import InitSampleBase


class RandomInitSample(InitSampleBase):
    """
    随机初始化采样策略
    每批次随机从样本总体中抽取N个样本作为初始化样本，直到正报个数达到停止的阈值
    """

    def __init__(self, batch_n: int, stop_threshold: int, query_func=None):
        """
        :param batch_n: 每批次随机采样数量
        :param stop_threshold: 随机采样停止阈值
        """
        super().__init__("random_init")
        self.batch_n = batch_n
        self.stop_threshold = stop_threshold
        self.query_func = query_func

    def get_sample_index(self, data_df: pd.DataFrame) -> pd.Index:
        TP_num = 0
        return_sample = pd.Index([], dtype="object")
        all_index = data_df.copy().index
        while TP_num < self.stop_threshold and len(all_index) >= self.batch_n:
            new_sample = random.sample(all_index.to_list(), self.batch_n)
            all_index = all_index.difference(new_sample)
            return_sample = return_sample.append(pd.Index(new_sample, dtype="object"))
            if self.query_func is None:
                TP_num = data_df.loc[return_sample, "label"].sum() / Alarm.TP
            else:
                self.query_func(new_sample)
        LOG.info(len(return_sample))
        return return_sample
