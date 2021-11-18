import pandas as pd


class Alarm(object):
    """
    警告类
    """

    # 标记未知
    UNKNOWN = -1
    # 误报
    FP = 0
    # 正报
    TP = 1

    def __init__(self):
        self.category = ""
        self.type = ""
        self.rank = 0
        # 路径
        self.path = ""
        # 类名
        self.class_name = ""
        # 方法名
        self.method = ""
        # 漏洞行位置
        self.location = -1
        # 警告标记
        self.label = Alarm.UNKNOWN
        # 所在版本
        self.version = ""

    def from_dict(self, d: dict):
        for k, v in d.items():
            if k in self.__dict__.keys():
                setattr(self, k, v)
        return self

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> list:
        return [Alarm().from_dict(row) for row in df.to_dict("records")]
