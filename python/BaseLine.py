import traceback
from typing import List

import numpy as np
import pandas as pd
from sklearn.metrics import auc

from active import ActiveLearningModel
from baseline import *
from model import ProjectConfig
from utils import DataUtils, PathUtils


def handle_data(config: ProjectConfig, data_df: pd.DataFrame):
    """
    处理数据集，返回警报数据和对应的警报特征，保证数目相等
    """
    feature_df = DataUtils.to_feature_df(config, data_df.index)
    return data_df.loc[feature_df.index], feature_df


def experiment_metric(label_list: List[int]) -> dict:
    """
    每次实验得到警告的排序后，计算各项度量指标
    :param label_list: 排序的真实标签，只含0和1的序列
    :return: 度量值键值对
    """
    metric_dict = {}
    # 正报总数
    tp_sum = sum(label_list)
    # 累计正报达到指定recall值需要检查的警告数目
    tp_num = 0
    for i, label in enumerate(label_list):
        tp_num += label
        tp_percent = int(tp_num / tp_sum * 10) * 10
        metric_key = "p" + str(tp_percent)
        if tp_percent > 0 and metric_key not in metric_dict.keys():
            metric_dict[metric_key] = i + 1
    # 计算Fitness
    fitness = 0
    tp_num = 0
    for i, label in enumerate(label_list):
        tp_num += label
        if label == 1:
            target_i = tp_num
        else:
            target_i = tp_sum + i + 1 - tp_num
        fitness += (1 / (abs(i - target_i) + 1))
    metric_dict["Fitness"] = fitness / len(label_list)
    # 计算Kendell系数
    kendell = 0
    tp_num = 0
    for i, label in enumerate(label_list):
        tp_num += label
        if label == 0:
            kendell += (tp_sum - tp_num)
    metric_dict["Kendell"] = kendell * 2 / len(label_list) / (len(label_list) - 1)
    # 计算AUC
    tpr = []
    fpr = []
    tp_num = 0
    for i, label in enumerate(label_list):
        tp_num += label
        tpr.append(tp_num / tp_sum)
        fpr.append((i + 1) / len(label_list))
    metric_dict["AUC"] = auc(np.array(fpr), np.array(tpr))
    return metric_dict


def run_baseline(config: ProjectConfig, train_df: pd.DataFrame, test_df: pd.DataFrame):
    """
    以config指定的项目运行BaseLine实验，返回训练集与测试集上的排序结果
    :param config: 项目配置
    :param train_df: 训练集
    :param test_df: 测试集
    :return {实验名: List[排序结果对应的真实标签]}
    """
    if train_df is None:
        train_df = test_df.copy()
    train_df, train_feature_df = handle_data(config, train_df)
    test_df, test_feature_df = handle_data(config, test_df)
    baseline_list = [BaseLineA(train_df, test_df),
                     BaseLineB(train_df, test_df),
                     BaseLineC(train_feature_df, test_feature_df),
                     BaseLineD(train_df, test_df),
                     BaseLineE(train_df, test_df)]
    train_data = {b.name: b.train_labels for b in baseline_list}
    test_data = {b.name: b.test_labels for b in baseline_list}
    return train_data, test_data


def run_active_learning(config: ProjectConfig, model: ActiveLearningModel, cur_df: pd.DataFrame, pre_df: pd.DataFrame):
    """
    运行主动学习模型，注意此处训练集和测试集的定义
    :param config: 项目配置
    :param model: 主动学习模型
    :param cur_df: 当前版本数据
    :param pre_df: 之前版本数据
    :return: 当前版本数据集的标签排序，之前版本数据集的标签排序
    """
    cur_df, cur_feature_df = handle_data(config, cur_df)
    # 如果是第一个版本
    if pre_df is None:
        model.run(cur_feature_df)
        return model.rank_labels(), None
    else:
        pre_df, pre_feature_df = handle_data(config, pre_df)
        # 获得与上一版本中正报相同的警告，直接标记，不再进入主动学习
        tp_in_last_version = pre_df.loc[
            (pre_df["next"].isin(cur_feature_df.index.to_list())) & (pre_df["label"] == 1), "next"]
        # 在剩下的数据上主动学习
        model.run(cur_feature_df.loc[cur_feature_df.index.difference(tp_in_last_version)], metric_flag=False)
        return cur_feature_df.loc[tp_in_last_version, "label"].to_list() + model.rank_labels(), model.rank_labels(pre_feature_df)


def one_project_experiment(config: ProjectConfig, result: list):
    """
    在一个项目上运行实验，实验过程中及时保存
    :param config: 项目配置
    :param result: 实验结果
    """
    # 主动学习模型默认配置
    model_config = {
        "init_sample": {
            "name": "random",
            "sample_num": 10,
            "stop_threshold": 1,
            "cluster_n": 5
        },
        "learn_model": {
            "name": "bagging"
        },
        "query_strategy": {
            "name": "certain_query",
            "max_num": 5
        },
        "stop_strategy": {
            "name": "never"
        }
    }
    # 使用的所有主动学习模型列表
    active_learning_models = []
    # 生成主动学习模型
    for model_name in ["bagging", "stacking"]:
        model_config["learn_model"]["stacking"] = model_name
        active_learning_models.append(ActiveLearningModel(config=model_config))
    # 遍历版本训练，结果保存在result中
    for version, pre_df, cur_df in DataUtils.iter_version_df(config):

        def update_baseline(result_dict: dict, data_type):
            if result_dict is None:
                return
            for name, label_list in result_dict.items():
                info_dict = {
                    "project": config.name,
                    "version": version,
                    "method": name,
                    "type": data_type
                }
                info_dict.update(experiment_metric(label_list))
                result.append(info_dict)
        try:
            baseline_train_result, baseline_test_result = run_baseline(config, pre_df, cur_df)
            update_baseline(baseline_train_result, "pre")
            update_baseline(baseline_test_result, "cur")
        except:
            traceback.print_exc()

        for model in active_learning_models:
            try:
                train_label_list, test_label_list = run_active_learning(config, model, cur_df, pre_df)
            except:
                traceback.print_exc()
                continue

            def update_active_learning(label_list: list, data_type: str):
                if label_list is None:
                    return
                info_dict = {
                    "project": config.name,
                    "version": version,
                    "method": "AL",
                    "type": data_type,
                    "learn_model": model_name
                }
                info_dict.update(experiment_metric(label_list))
                result.append(info_dict)

            update_active_learning(train_label_list, "pre")
            update_active_learning(test_label_list, "cur")
        # 保存当前结果
        pd.DataFrame(result).to_csv(PathUtils.join_path("result.csv"), index=False, encoding="utf-8")
    return result


if __name__ == "__main__":
    project_config = DataUtils.read_project_config("lucene-core")
    all_result = []
    one_project_experiment(project_config, all_result)
