"""
实验流程中使用的封装对象：

- Alarm: 警告信息，来自扫描报告xml文件中的BugInstance
- ClassMetric: 类级别度量值，来自JHawk得到的xml文件结果
- FeatureType： 特征分类，用于特征提取与存储
- MethodMetric: 方法级别度量值，来自JHawk得到的xml文件结果
- PackageMetric: 包级别度量值，来自JHawk得到的xml文件结果
- ProjectConfig: 实验项目配置，默认来自project.json配置文件
- Version: 实验版本信息，默认来自project.json配置文件
- WarningType: 警告类别，来自静态分析工具的文档

系统中使用的持久化对象，均继承自BaseModel以实现相同的数据库配置：

- AlarmModel: 警告信息
- LabelModel: 审核任务
- ProjectModel: 项目信息
- WorkerModel: 工人信息

"""
from .Alarm import Alarm
from .AlarmModel import AlarmModel
from .ClassMetric import ClassMetric
from .FeatureType import FeatureType
from .LabelModel import LabelModel
from .MethodMetric import MethodMetric
from .PackageMetric import PackageMetric
from .ProjectConfig import ProjectConfig
from .ProjectModel import ProjectModel
from .Version import Version
from .WarningType import WarningType
from .WorkerModel import WorkerModel
