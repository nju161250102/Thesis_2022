import pandas as pd


class StopBase(object):
    """
    停止策略基类
    """

    @staticmethod
    def judge_stop(actual_label: pd.Series, model_label: pd.Series) -> bool:
        """
        判断主动学习循环是否需要终止
        :param actual_label: 实际标签值
        :param model_label: 模型预测的标签值
        :return: 是否需要停止学习循环
        """
        pass
