import pandas as pd
from sklearn.metrics import *

from Logger import LOG
from model import Alarm, FeatureType
from .init import *
from .model import *
from .query import *
from .stop import *
from .DataHandler import DataHandler


class ActiveLearningModel(object):

    def __init__(self, data_df: pd.DataFrame, config=None):
        """
        初始化主动学习模型
        data_df 只包含index和特征
        label_series 真实标签
        model_label_series 模型预测标签
        :param data_df: 原始csv保存的数据集
        """
        self.data_df = data_df.copy()
        self.data_df["model_label"] = pd.Series(Alarm.UNKNOWN, index=self.data_df.index)
        self.data_df.dropna(inplace=True)
        self.data_df = self.data_df[self.data_df["label"] != Alarm.UNKNOWN]
        # 数据预处理
        use_features = {FeatureType.F23, FeatureType.F95, FeatureType.F96, FeatureType.F92, FeatureType.F21, FeatureType.F29, FeatureType.F31}
        self.data_handler = DataHandler(use_features)
        # self.data_handler = DataHandler()
        # 组件默认配置
        default_config = {
            "init_sample": {
                "name": "random",
                "sample_num": 10,
                "stop_threshold": 1,
                "cluster_n": 6
            },
            "learn_model": {
                "name": "svm"
            },
            "query_strategy": {
                "name": "uncertain",
                "max_num": 20
            },
            "stop_strategy": {
                "name": "never"
            }
        }
        if config is not None and isinstance(config, dict):
            for k, v in default_config.items():
                if k in config.keys():
                    default_config[k].update(config[k])
        # 实验流程各组件
        self.init_sample = self._build_init_sample(default_config["init_sample"])
        self.learn_model = self._build_learning_model(default_config["learn_model"])
        self.query_strategy = self._build_query_strategy(default_config["query_strategy"])
        self.stop_strategy = self._build_stop_strategy(default_config["stop_strategy"])
        # 实验度量记录
        self.metrics_records = []

    def run(self):
        # 输出实验配置
        LOG.info("==== Run Active Learning ====")
        LOG.info("Init:  " + self.init_sample.name)
        LOG.info("Model: " + self.learn_model.name)
        LOG.info("Query: " + self.query_strategy.name)
        LOG.info("Size:  " + str(len(self.data_df)))
        LOG.info("TA:    " + str(len(self.data_df[self.data_df["label"] == Alarm.TP])))
        # 参数初始化
        batch_num = 1
        self.metrics_records.clear()
        # 初始化采样标记一部分数据，剩下的为未标记数据
        labeled_index_set = set(self.init_sample.get_sample_index(self.data_df))
        unlabeled_index_set = set(self.data_df.index.tolist()).difference(labeled_index_set)
        # 开始主动学习步骤
        while len(unlabeled_index_set) > 0:
            # 根据停止策略决定是否终止主动学习循环
            if self.stop_strategy.judge_stop(self.data_df["label"], self.data_df["model_label"]):
                LOG.info("Stop strategy activate")
                break
            # 获取训练集和标签
            train_df = self.data_df.loc[labeled_index_set]
            train_data, train_label, _ = self.data_handler.preprocess(train_df, True)
            # 模型训练
            self.learn_model.train(train_data, train_label)
            # 对所有样本的预测结果
            pre_data, y_true, _ = self.data_handler.preprocess(self.data_df, False)
            self.data_df["model_label"] = pd.Series(self.learn_model.predict_label(pre_data), self.data_df.index)
            prob_series = pd.Series(self.learn_model.predict_prob(pre_data), self.data_df.index)
            # 使用查询策略得到下一批标记的数据
            label_index = self.query_strategy.query(labeled_index_set, prob_series)
            labeled_index_set = labeled_index_set.union(set(label_index.to_list()))
            unlabeled_index_set = unlabeled_index_set.difference(set(label_index.to_list()))
            # 评估模型效果
            y_true = self.data_df["label"].to_numpy()
            y_pred = self.data_df["model_label"].to_numpy()
            self.metrics_records.append(self._evaluate(y_true, y_pred))
            LOG.info(str(len(unlabeled_index_set)) + "\n" + str(self.metrics_records[-1]))
            batch_num += 1
            # break

    @staticmethod
    def _build_init_sample(config: dict) -> InitSampleBase:
        """
        设置初始化采样策略
        """
        if config["name"] == "kmeans":
            return KMeansInitSample(config["cluster_n"], config["sample_num"])
        return RandomInitSample(config["sample_num"], config["stop_threshold"])

    @staticmethod
    def _build_stop_strategy(config: dict):
        """
        设置主动学习停止策略
        """
        return NeverStop()

    @staticmethod
    def _build_learning_model(config: dict):
        """
        设置机器学习模型
        """
        if config["name"] == "one_class_svm":
            return OneClassSvmModel()
        return MultiplyClassModel(config["name"])

    def _build_query_strategy(self, config: dict):
        """
        设置查询策略
        """
        return UncertainlyQuery(self.data_df, config["max_num"])

    @staticmethod
    def _evaluate(y_true, y_pred):
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        return {
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "accuracy": accuracy_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred),
            "mcc": matthews_corrcoef(y_true, y_pred)
        }
