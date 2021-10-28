import os
import yaml


class Config(object):
    """
    配置类
    """
    test_flag = os.path.isdir("/home/qian")
    yaml_file = "/home/qian/config.yaml" if os.path.isdir("/home/qian") else "/home/qianmy/config.yaml"
    config_data = yaml.safe_load(open(yaml_file))

    # 工作目录：程序文件夹位置
    WORKING_DIR = config_data["workingDir"]
    # 数据目录：存放下载数据和训练数据
    DATA_DIR = config_data["dataDir"]
    # Jira服务器地址：Apache开源基金会
    JIRA_SITE = config_data["jiraSite"]
    # Git组织地址：Apache开源基金会
    GIT_SITE = config_data["gitSite"]
    # Git OAuth令牌：用于提升访问次数限制
    GIT_TOKEN = config_data["gitToken"]
    # 项目扫描配置
    SCAN_CONF = config_data["scanConf"]
    # Findbugs路径
    FINDBUGS_PATH = config_data["findBugsPath"]
