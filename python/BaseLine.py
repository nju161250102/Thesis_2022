"""
实验运行脚本，使用`-h`选项查看帮助，参数详细说明参见`main`函数。

短选项 | 长选项 | 参数 | 含义 | 默认值
----- | ----- | --- | --- | -----
-p | --projects      | [PROJECT_LIST [PROJECT_LIST ...]] | 项目名称 | []
-e | --experiments   | EXPERIMENTS | 实验类型 | "all"
-a | --active-models | ACTIVE_MODELS | 主动学习模型配置生成器 | "default"
-o | --output-file   | OUTPUT_FILE | 结果输出文件名 | "result.csv"

实验结果输出中包括实验配置信息和度量结果两部分，度量结果包括

度量项 | 含义
----- | ---
sum | 数据集总量
tp_sum | 数据集中正报的数量
p{N} | 正报召回率达到N%时需要检查的警告数目
Fitness | Fitness指标
Kendell | Kendell相关系数
AUC | 正报占比曲线下面积
"""
import argparse
import traceback
import sys
from typing import List

import numpy as np
import pandas as pd
from sklearn.metrics import auc

from Logger import LOG
from active import ActiveLearningModel
from baseline import *
from model import ProjectConfig
from utils import DataUtils, PathUtils

# 主动学习模型默认配置
model_config = ActiveLearningModel.default_config


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
    metric_dict["sum"] = len(label_list)
    metric_dict["tp_sum"] = tp_sum
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
    :return Dict{实验名: List[排序结果对应的真实标签]}
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
        model.run(cur_feature_df, metric_flag=False)
        return model.rank_labels(), None
    else:
        pre_df, pre_feature_df = handle_data(config, pre_df)
        # # 获得与上一版本中正报相同的警告，直接标记，不再进入主动学习
        # # 所以不能从第一个版本开始
        # tp_in_last_version = pre_df.loc[
        #     (pre_df["next"].isin(cur_feature_df.index.to_list())) & (pre_df["label"] == 1), "next"]
        # # 在剩下的数据上主动学习
        # model.run(cur_feature_df.loc[cur_feature_df.index.difference(tp_in_last_version)], metric_flag=False)
        # return cur_feature_df.loc[tp_in_last_version, "label"].to_list() + model.rank_labels(), model.rank_labels(pre_feature_df)
        model.run(cur_feature_df, metric_flag=False)
        return model.rank_labels(), model.rank_labels(pre_feature_df)


def one_project_baseline(config: ProjectConfig, result: list, output_file: str):
    for version, pre_df, cur_df in DataUtils.iter_version_df(config):
        #
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
            continue
        # 保存当前结果
        pd.DataFrame(result).to_csv(PathUtils.join_path(output_file), index=False, encoding="utf-8")


def one_project_active(config: ProjectConfig, config_generator, result: list, output_file: str):
    for al_config in config_generator():
        model = ActiveLearningModel(config=al_config)
        for version, pre_df, cur_df in DataUtils.iter_version_df(config):
            # if pre_df is None:
            #     continue
            LOG.info("{0} - {1}".format(config.name, version))

            def update_active_learning(label_list: list, data_type: str):
                if label_list is None:
                    return
                info_dict = {
                    "project": config.name,
                    "version": version,
                    "method": "AL",
                    "type": data_type,
                    "learn_model": model.config["learn_model"]["name"],
                    "query_num": model.config["query_strategy"]["max_num"],
                    "query_strategy": model.config["query_strategy"]["name"],
                }
                info_dict.update(experiment_metric(label_list))
                result.append(info_dict)

            try:
                train_label_list, test_label_list = run_active_learning(config, model, cur_df, pre_df)
                update_active_learning(train_label_list, "cur")
                update_active_learning(test_label_list, "pre")
            except:
                traceback.print_exc()
                continue
            # 保存当前结果
            pd.DataFrame(result).to_csv(PathUtils.join_path(output_file), index=False, encoding="utf-8")


def _default_generator():
    for model_name in ["bagging", "boosting"]:
        model_config["learn_model"]["name"] = model_name
        model_config["query_strategy"]["max_num"] = 20
        yield model_config


def _all_generator():
    for model_name in ["bagging", "boosting", "svm", "rt", "dt", "nb", "mlp"]:
        for sample_num in [20, 50, 100]:
            for query_name in ["certain", "uncertain"]:
                model_config["learn_model"]["name"] = model_name
                model_config["query_strategy"]["max_num"] = sample_num
                model_config["query_strategy"]["name"] = query_name
                yield model_config


def main(projects: List[str], experiments: str, active_models: str, output_file: str):
    """
    :param projects:
    项目名称，不指定时在所有项目上实验
    :param experiments:
    实验类型，不指定时默认为all，可指定为baseline或active
    :param active_models:
    主动学习模型配置生成器，默认为default，将在本文件中寻找名为"_{active_models}_generator"的生成器函数迭代生成主动学习模型配置
    :param output_file:
    结果输出文件名，默认为result.csv，保存位置在配置中的数据目录
    """
    # 结果
    all_result = []
    # 主动学习模型生成器
    try:
        config_generator = getattr(sys.modules[__name__], "_{0}_generator".format(active_models))
    except AttributeError:
        config_generator = getattr(sys.modules[__name__], "_default_generator")
    # 运行实验
    if projects is None or len(projects) == 0:
        project_config_list = DataUtils.read_projects(PathUtils.join_path("project.json")).values()
    else:
        project_config_list = [DataUtils.read_project_config(project_name) for project_name in projects]
    for project_config in project_config_list:
        if experiments == "all":
            one_project_baseline(project_config, all_result, output_file)
            one_project_active(project_config, config_generator, all_result, output_file)
        elif experiments == "baseline":
            one_project_baseline(project_config, all_result, output_file)
        elif experiments == "active":
            one_project_active(project_config, config_generator, all_result, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Experiments")
    parser.add_argument("-p", "--projects", dest="project_list", action="extend", nargs="*", type=str,
                        help="The project(s) to run experiments(default: run on all projects)")
    parser.add_argument("-e", "--experiments", action="store", default="all", type=str,
                        help="The type of experiments(default: both baseline and active)")
    parser.add_argument("-a", "--active-models", action="store", default="methods", type=str,
                        help="How to generate active learning models")
    parser.add_argument("-o", "--output-file", action="store", default="result.csv", type=str,
                        help="The output file name")
    args = parser.parse_args()

    # main(args.projects, args.experiments, args.active_models, args.output_file)

    import requests

    with open("/home/qian/Document/p", "r") as f:
        for line in f.readlines():
            r = requests.post("http://8.134.39.104:8080/nfsplatform/adduser", {
                "name": line.strip(),
                "password": "c4ca4238a0b923820dcc509a6f75849b",
                "email": "1"
            })
            if "注册失败" not in r.text:
                print(line)
