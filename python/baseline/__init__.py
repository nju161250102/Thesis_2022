"""
BaseLine 对比实验模型

所有实验均继承自`BaseLineModel`类，实现`_rank_labels`方法完成标签预测与排序。
"""
from .BaseLineA import BaseLineA
from .BaseLineB import BaseLineB
from .BaseLineC import BaseLineC
from .BaseLineD import BaseLineD
from .BaseLineE import BaseLineE


__all__ = ["BaseLineA", "BaseLineB", "BaseLineC", "BaseLineD", "BaseLineE"]
