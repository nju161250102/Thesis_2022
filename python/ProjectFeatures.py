"""
项目特征分类效果研究脚本
"""
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier

from Logger import LOG
from model import FeatureType, Alarm
from utils import PathUtils, JsonUtils


def check_common_features(df: pd.DataFrame, feature_list: List[str]):
    """
    研究一般的特征
    绘制正报和误报的特征值箱型图
    根据Gini指标确定一个阈值
    度量阈值分类的有效性：F1-score
    :param df: 特征数据
    :param feature_list: 特征列表
    :return: 阈值列表，度量值列表
    """
    # 预处理
    transformer = MinMaxScaler()
    x_data = transformer.fit_transform(df[feature_list].to_numpy())
    y_data = df["label"].to_numpy()
    # 绘图数据
    true_data = [x_data[y_data == Alarm.TP, i] for i in range(len(feature_list))]
    false_data = [x_data[y_data == Alarm.FP, i] for i in range(len(feature_list))]
    # 绘图
    fig, ax = plt.subplots()
    ax.boxplot(true_data, positions=np.arange(len(feature_list)) + 0.9, widths=0.2)
    ax.boxplot(false_data, positions=np.arange(len(feature_list)) + 1.1, widths=0.2)
    ax.set_xticks(ticks=np.arange(len(feature_list)) + 1, labels=[FeatureType.to_id(f) for f in feature_list])
    fig.savefig(PathUtils.picture_path("feature", project_config.name + ".png"))
    # 单层决策树做阈值二分类
    threshold_list = []
    metric_list = []
    for i in range(len(feature_list)):
        clf = DecisionTreeClassifier(max_depth=1)
        clf.fit(x_data[:, i].reshape(-1, 1), y_data)
        # y_predict = clf.apply(x_data[:, i].reshape(-1, 1)) - 1
        # 决策树两个节点对应的label可能都为0，所以改用阈值判断
        y_predict = np.int32(x_data[:, i] > clf.tree_.threshold[0])
        threshold_list.append(clf.tree_.threshold[0])
        metric_list.append(f1_score(y_data, y_predict))
    original_threshold_list = transformer.inverse_transform(np.array([threshold_list]))[0]
    return metric_list, original_threshold_list


def check_boolean_feature(df: pd.DataFrame, feature_list: List[str]):
    """
    研究布尔取值的特征，即只有0和1两种取值
    :param df: 特征数据
    :param feature_list: 特征列表
    :return: 1值应当被预测成何值，度量值列表
    """
    positive_list = []
    metric_list = []
    for i, feature in enumerate(feature_list):
        # 1预测成1
        y_true = df[feature].to_numpy()
        # 1预测成0
        y_false = 1 - y_true
        f1_true = f1_score(df["label"].to_numpy(), y_true)
        f1_false = f1_score(df["label"].to_numpy(), y_false)
        positive_list.append(int(f1_true > f1_false))
        metric_list.append(max(f1_true, f1_false))
    return metric_list, positive_list


if __name__ == "__main__":
    common_feature_list = [FeatureType.F19, FeatureType.F20, FeatureType.F21, FeatureType.F22, FeatureType.F23, FeatureType.F28, FeatureType.F29, FeatureType.F31, FeatureType.F33]
    boolean_feature_list = list(filter(lambda s: s.split("_")[0] in ["F84", "F86", "F87", "F88"], FeatureType.to_list()))
    metric_df = pd.DataFrame(columns=common_feature_list + boolean_feature_list)
    threshold_df = pd.DataFrame(columns=common_feature_list + boolean_feature_list)
    for project_config in JsonUtils.read_projects(PathUtils.join_path("project.json")).values():
        if not PathUtils.exist_path("feature", project_config.name + ".csv"):
            continue
        data_df = pd.read_csv(PathUtils.feature_path(project_config.name + ".csv"), index_col="index")
        # 确保有两类标签
        if data_df["label"].sum() == 0 or data_df["label"].sum() == len(data_df):
            continue
        LOG.info("Project: " + project_config.name)
        # 研究特征分类效果并拼接结果，注意顺序
        m1, t1 = check_common_features(data_df, common_feature_list)
        m2, t2 = check_boolean_feature(data_df, boolean_feature_list)
        metric_df.loc[project_config.name] = m1 + m2
        threshold_df.loc[project_config.name] = t1 + t2
    # 保存结果
    metric_df.to_csv(PathUtils.feature_path("feature_metric.csv"), index=False)
    threshold_df.to_csv(PathUtils.feature_path("feature_threshold.csv"), index=False)
