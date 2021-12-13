import pandas as pd

from .StopBase import StopBase
from model import Alarm


class NeverStop(StopBase):
    """
    直到全部标注结束才停止
    """

    @staticmethod
    def judge_stop(actual_label: pd.Series, model_label: pd.Series) -> bool:
        return False
