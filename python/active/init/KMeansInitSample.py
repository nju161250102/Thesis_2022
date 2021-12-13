import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from .InitSampleBase import InitSampleBase
from ..DataHandler import DataHandler


class KMeansInitSample(InitSampleBase):
    """
    基于聚类的初始化采样策略
    将样本划分为N个聚类，每个聚类选择与聚类中心最近的样本
    """

    def __init__(self, cluster_n: int, sample_n: int):
        """
        :param cluster_n: 聚类数目
        :param sample_n: 随机采样停止阈值
        """
        super().__init__("kmeans_init")
        self.cluster_n = cluster_n
        self.sample_n = sample_n
        self.data_handler = DataHandler()

    def get_sample_index(self, data_df: pd.DataFrame) -> pd.Index:
        data_x, _ = self.data_handler.preprocess(data_df, True)
        distances = KMeans(n_clusters=self.cluster_n).fit_transform(data_x)
        min_index = np.argmin(distances, axis=0)
        return data_df.iloc[min_index].index
