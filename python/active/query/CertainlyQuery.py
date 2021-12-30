import pandas as pd

from .QueryBase import QueryBase


class CertainlyQuery(QueryBase):
    """
    不确定性采样查询策略
    选取预测概率最不确定，即在0.5附近的样本作为需要人工审核的标记对象
    """

    def __init__(self, data_df: pd.DataFrame, max_num: int):
        super().__init__(data_df, max_num, "certain_query")

    def query(self, labeled_index_set: set, predict_prob: pd.Series) -> pd.Index:
        unlabeled_index_set = set(self.data_df.index.to_list()) - labeled_index_set
        unlabeled_prob = predict_prob[unlabeled_index_set]
        unlabeled_prob.sort_values(inplace=True, key=lambda p: - abs(p - 0.5))
        if len(unlabeled_prob) > self.max_num:
            return unlabeled_prob.iloc[:self.max_num].index
        else:
            return unlabeled_prob.index
