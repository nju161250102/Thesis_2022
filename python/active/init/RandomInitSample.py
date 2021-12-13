import pandas as pd
from .InitSampleBase import InitSampleBase
from model import Alarm


class RandomInitSample(InitSampleBase):
    """
    随机初始化采样策略
    每批次随机从样本总体中抽取N个样本作为初始化样本，直到正报个数达到停止的阈值
    """

    def __init__(self, batch_n: int, stop_threshold: int):
        """
        :param batch_n: 每批次随机采样数量
        :param stop_threshold: 随机采样停止阈值
        """
        super().__init__("random_init")
        self.batch_n = batch_n
        self.stop_threshold = stop_threshold

    def get_sample_index(self, data_df: pd.DataFrame) -> pd.Index:
        data_label = data_df["label"].copy()
        return_sample = pd.Series([], dtype="int64")
        TP_num = 0
        while TP_num < self.stop_threshold:
            new_sample = data_label.sample(self.batch_n)
            return_sample = return_sample.append(new_sample)
            data_label = data_label.drop(index=new_sample.index)
            TP_num = return_sample.sum() / Alarm.TP
        return return_sample.index
