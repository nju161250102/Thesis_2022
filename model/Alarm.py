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
        # 起始行
        self.start = -1
        # 结束行
        self.end = -1
        # 警告标记
        self.label = Alarm.UNKNOWN
        # 所在版本
        self.version = ""
