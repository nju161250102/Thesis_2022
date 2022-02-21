import pandas as pd
from sklearn.metrics import *
from sklearn.utils.validation import check_is_fitted
from sklearn.exceptions import NotFittedError

from Logger import LOG
from model import Alarm
from .init import *
from .model import *
from .query import *
from .stop import *
from .DataHandler import DataHandler


class ActiveLearningModel(object):

    def __init__(self, config=None, query_func=None):
        """
        初始化主动学习模型
        :param config: 学习模型配置
        :param query_func: 查询标签的方法，默认为None表示直接从data_df中读取
        """
        self.data_df = None
        self.query_func = query_func
        # 数据预处理
        self.data_handler = DataHandler()
        # 组件默认配置
        self.config = {
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
        # 更新组件配置
        if config is not None and isinstance(config, dict):
            for k, v in self.config.items():
                if k in config.keys():
                    self.config[k].update(config[k])
        # 实验流程各组件
        self.init_sample = None
        self.learn_model = None
        self.query_strategy = None
        self.stop_strategy = None
        # 实验度量记录
        self.metrics_records = []
        # 实验审核记录
        self.sample_records = []

    def run(self, data_df: pd.DataFrame, metric_flag=True):
        """
        运行主动学习
        :param data_df: 原始csv保存的数据集
        """
        # 更新训练数据集
        self.data_df = data_df.copy()
        self.data_df["model_label"] = pd.Series(Alarm.UNKNOWN, index=self.data_df.index)
        self.data_df = self.data_df.dropna()
        # 更新实验流程组件，仅在第一次训练时更新模型
        self.init_sample = self._build_init_sample()
        if self.learn_model is None:
            self.learn_model = self._build_learning_model()
        self.query_strategy = self._build_query_strategy()
        self.stop_strategy = self._build_stop_strategy()
        # 更新记录列表
        self.metrics_records.clear()
        self.sample_records.clear()
        # 输出实验配置
        LOG.info("==== Run Active Learning ====")
        LOG.info("Init:  " + self.init_sample.name)
        LOG.info("Model: " + self.learn_model.name)
        LOG.info("Query: " + self.query_strategy.name)
        LOG.info("Size:  " + str(len(self.data_df[self.data_df["label"] == Alarm.TP])) + "/" + str(len(self.data_df)))
        # 如果是初次训练则使用初始化采样，否则选择已有的模型预测
        try:
            check_is_fitted(self.learn_model.model)
            x_data, y_label, _ = self.data_handler.preprocess(self.data_df, True)
            prob_series = pd.Series(self.learn_model.predict_prob(x_data), self.data_df.index)
            prob_series.sort_values(inplace=True, ascending=True)
            labeled_index_set = set(prob_series.iloc[:self.config["init_sample"]["sample_num"]].index)
        except NotFittedError:
            # 初始化采样标记一部分数据
            labeled_index_set = set(self.init_sample.get_sample_index(self.data_df))
        # 剩下的为未标记数据
        unlabeled_index_set = set(self.data_df.index.tolist()) - labeled_index_set
        # 查询标签
        self._query_labels(labeled_index_set)
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
            # 计算所有样本的预测结果
            pre_data, y_true, _ = self.data_handler.preprocess(self.data_df, False)
            self.data_df["model_label"] = pd.Series(self.learn_model.predict_label(pre_data), self.data_df.index)
            prob_series = pd.Series(self.learn_model.predict_prob(pre_data), self.data_df.index)
            # 使用查询策略得到下一批标记的数据
            label_index = self.query_strategy.query(labeled_index_set, prob_series)
            labeled_index_set = labeled_index_set | set(label_index.to_list())
            unlabeled_index_set = unlabeled_index_set - set(label_index.to_list())
            # 查询样本的标签值
            self._query_labels(set(label_index.to_list()))
            # 分别在已标记和未标记的数据集上评估模型效果
            if metric_flag:
                unlabeled_y_true = self.data_df.loc[unlabeled_index_set]["label"].to_numpy()
                unlabeled_y_pred = self.data_df.loc[unlabeled_index_set]["model_label"].to_numpy()
                labeled_y_true = self.data_df.loc[labeled_index_set]["label"].to_numpy()
                labeled_y_pred = self.data_df.loc[labeled_index_set]["model_label"].to_numpy()
                d = {}
                d.update(self._evaluate(unlabeled_y_true, unlabeled_y_pred, prefix="test_"))
                d.update(self._evaluate(labeled_y_true, labeled_y_pred, prefix="train_"))
                self.metrics_records.append(d)
            LOG.info(str(len(unlabeled_index_set)))
            # 剩余标签不足以再次查询
            if len(unlabeled_index_set) < self.config["query_strategy"]["max_num"]:
                break
            # break

    def rank_labels(self, data_df: pd.DataFrame = None):
        """
        获取所有标签排序
        :param data_df: 默认为None使用当前模型保存的数据集，否则使用提供的数据集
        """
        if data_df is None:
            return self.data_df.loc[self.sample_records, "label"].to_list()
        else:
            test_data, test_label, _ = self.data_handler.preprocess(data_df, False)
            data_df["rank_score"] = pd.Series(self.learn_model.predict_prob(test_data), data_df.index)
            data_df.sort_values("rank_score", ascending=False, inplace=True)
            return data_df["label"].to_list()

    def _build_init_sample(self) -> InitSampleBase:
        """
        设置初始化采样策略
        """
        config = self.config["init_sample"]
        if config["name"] == "kmeans":
            return KMeansInitSample(config["cluster_n"], config["sample_num"])
        return RandomInitSample(config["sample_num"], config["stop_threshold"])

    def _build_stop_strategy(self):
        """
        设置主动学习停止策略
        """
        return NeverStop()

    def _build_learning_model(self) -> ModelBase:
        """
        设置机器学习模型
        """
        config = self.config["learn_model"]
        if config["name"] == "one_class_svm":
            return OneClassSvmModel()
        elif config["name"] == "bagging":
            return BaggingClassifierModel()
        elif config["name"] == "stacking":
            return StackingClassifierModel()
        return MultiplyClassifierModel(config["name"])

    def _build_query_strategy(self):
        """
        设置查询策略
        """
        config = self.config["query_strategy"]
        if config["name"] == "certain_query":
            return CertainlyQuery(self.data_df, config["max_num"])
        return UncertainlyQuery(self.data_df, config["max_num"])

    def _query_labels(self, index_set: set):
        """
        查询样本的标签值，并记录采样的历史
        :param index_set: 需要查询标签的index
        """
        # 如果指定了查询标签的方法，则使用该方法获得标签值并填入data_df
        if self.query_func is not None:
            self.data_df.loc[index_set, "label"] = self.query_func(index_set)
        self.sample_records.extend(index_set)

    @staticmethod
    def _evaluate(y_true, y_pred, prefix="") -> dict:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        result = {
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
        return dict(map(lambda t: (prefix + t[0], t[1]), result.items()))
