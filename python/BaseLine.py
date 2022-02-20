from typing import List
import numpy as np
from sklearn.metrics import auc
import traceback

from active import ActiveLearningModel
from baseline import *
import pandas as pd
from model import ProjectConfig
from pic import draw_detected_rate
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
    :return {实验名: List[排序结果对应的真实标签]}
    """
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


def run_active_learning(config: ProjectConfig, model_config: dict, train_df: pd.DataFrame, test_df: pd.DataFrame):
    train_df, train_feature_df = handle_data(config, train_df)
    test_df, test_feature_df = handle_data(config, test_df)
    tp_in_last_version = train_df.loc[
        (train_df["next"].isin(test_feature_df.index.to_list())) & (train_df["label"] == 1), "next"]
    model = ActiveLearningModel(train_feature_df, config=model_config)
    model.run()
    return model.rank_labels(), test_feature_df.loc[tp_in_last_version, "label"].to_list() + \
           model.rank_labels(test_feature_df.loc[test_feature_df.index.difference(tp_in_last_version)])


def one_project_experiment(project_config: ProjectConfig):
    """

    :return:
    """
    result = []
    for version, train_df, test_df in DataUtils.train_and_test_df(project_config):
        try:
            baseline_train_result, baseline_test_result = run_baseline(project_config, train_df, test_df)
        except:
            traceback.print_exc()
            continue

        def update_baseline(result_dict: dict, data_type):
            for name, label_list in result_dict.items():
                info_dict = {
                    "project": project_config.name,
                    "version": version,
                    "method": name,
                    "type": data_type
                }
                info_dict.update(experiment_metric(label_list))
                result.append(info_dict)

        update_baseline(baseline_train_result, "train")
        update_baseline(baseline_test_result, "test")

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
        for model_name in ["bagging", "stacking"]:
            model_config["learn_model"]["stacking"] = model_name
            try:
                train_label_list, test_label_list = run_active_learning(project_config, model_config, train_df, test_df)
            except:
                traceback.print_exc()
                continue

            def update_active_learning(label_list: list, data_type: str):
                info_dict = {
                    "project": project_config.name,
                    "version": version,
                    "method": "AL",
                    "type": data_type,
                    "learn_model": model_name
                }
                info_dict.update(experiment_metric(label_list))
                result.append(info_dict)

            update_active_learning(train_label_list, "train")
            update_active_learning(test_label_list, "test")
        # draw_detected_rate(PathUtils.feature_path("train#{0}.png".format(version)), train_pic_data)
        # draw_detected_rate(PathUtils.feature_path("test#{0}.png".format(version)), test_pic_data)

    return result


if __name__ == "__main__":
    project_config = DataUtils.read_project_config("lucene-core")
    result = []
    result.extend(one_project_experiment(project_config))
    pd.DataFrame(result).to_csv(PathUtils.join_path("result.csv"), index=False, encoding="utf-8")
