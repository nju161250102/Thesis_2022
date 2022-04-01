"""
主动学习模块

各子模块均采用策略模式编写，在ActiveLearningModel中通过配置字典构造，
详情查看各子模块的策略父类。

- init: 初始化采样
- model: 内置的机器学习模型
- query: 查询策略
- stop: 停止策略，目前只有一种，即不停止
- ActiveLearningModel: 主动学习模型
- DataHandler: 数据预处理
"""
from .ActiveLearningModel import ActiveLearningModel
from .DataHandler import DataHandler
