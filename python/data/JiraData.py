from datetime import datetime

import jira

from utils import LOG
from Config import Config


class JiraData(object):
    """
    获取jira服务器的数据
    """

    def __init__(self):
        self._jira = jira.JIRA(Config.JIRA_SITE)

    def get_projects(self) -> list:
        """
        :return: 服务器的所有管理项目列表
        """
        return self._jira.projects()

    def get_issues(self, project_name, max_results=100):
        """
        :param project_name: 项目名（Key）
        :param max_results: 最大返回结果（数字 / False）
        :return: 查询issue列表
        """
        return self._jira.search_issues(
            "project={0} AND type=Bug AND (status=resolved OR status=closed)".format(project_name),
            maxResults=max_results)
