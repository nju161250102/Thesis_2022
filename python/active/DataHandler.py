from typing import Tuple

import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler, PowerTransformer, StandardScaler

from model import Alarm, FeatureType


class DataHandler(object):

    def __init__(self, all_columns=None):
        # 数据预处理
        self.preprocess_dict = {
            MinMaxScaler(): [FeatureType.F21, FeatureType.F32, FeatureType.F92],
            PowerTransformer(method="box-cox"): [FeatureType.F19, FeatureType.F20, FeatureType.F33],
            PowerTransformer(method="yeo-johnson"): [FeatureType.F22],
            StandardScaler(): [FeatureType.F28, FeatureType.F29, FeatureType.F31, FeatureType.F94, FeatureType.F95, FeatureType.F96]
        }
        # 所有特征列名，默认为全部
        self.all_columns = all_columns if all_columns else set(FeatureType.to_list())
        # 需要去除的列名
        self.remove_columns = ["warning_type", "label"]

    @staticmethod
    def cleanse(data_df: pd.DataFrame):
        """
        数据清洗
        :param data_df: 数据DataFrame
        """
        data_df = data_df.dropna()
        data_df = data_df[data_df["label"] != Alarm.UNKNOWN]
        return data_df

    def preprocess(self, data_df: pd.DataFrame, need_fit: bool) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        数据预处理
        :param data_df: 数据DataFrame
        :param need_fit: 是否需要fit，否则直接transform
        :return: 预处理后的 (数据, 标签, 特征名)
        """
        x_labels = data_df["label"].to_numpy()
        transform_result = []
        transform_columns = []
        # 保存所有特征列
        all_columns = self.all_columns.union(set(data_df.columns.tolist()))
        for column in self.remove_columns:
            all_columns.remove(column)
        for transformer, columns in self.preprocess_dict.items():
            if len(columns) > 0:
                transform_columns.extend(columns)
                if need_fit:
                    transform_result.append(transformer.fit_transform(data_df[columns].to_numpy()))
                else:
                    transform_result.append(transformer.transform(data_df[columns].to_numpy()))
            # 去除已经处理过的列名
            all_columns = all_columns.difference(columns)
        # 最后将剩下的列合并到结果中
        transform_result.append(data_df[all_columns].to_numpy())
        transform_columns.extend(all_columns)
        return np.concatenate(transform_result, axis=1), x_labels, np.array(transform_columns, dtype=object)
