import json


class Config(object):
    """
    配置类，项目配置以json格式保存在外部文件
    """
    # 配置文件的地址
    with open("/home/qianmy/ThesisData/config.json", "r") as f:
        config_data = json.load(f)

    # 数据目录：存放下载数据和训练数据
    DATA_DIR = config_data["dataDir"]
    # Jira服务器地址：Apache开源基金会
    JIRA_SITE = config_data["jiraSite"]
    # Git组织地址：Apache开源基金会
    GIT_SITE = config_data["gitSite"]
    # Git OAuth令牌：用于提升访问次数限制
    GIT_TOKEN = config_data["gitToken"]
    # Findbugs路径
    FINDBUGS_PATH = config_data["findBugsPath"]
    # Java编写的处理工具jar包路径
    JAVATOOLS_PATH = config_data["javaToolsPath"]
    # Maven仓库项目URL，select标明需要扫描的版本信息
    MAVEN_URL = config_data["mavenURL"]
