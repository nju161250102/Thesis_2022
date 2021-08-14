from datetime import datetime

import jira

from utils import LOG


class JiraData(object):
    """
    获取jira服务器的数据
    """

    def __init__(self, project_name: str, jira_home="https://issues.apache.org/jira"):
        """
        :param project_name: 项目名：不是全部大写的项目key
        :param jira_home: jira服务器，默认为apache的
        """
        client = jira.JIRA(jira_home)
        for project in client.projects():
            if project.name == project_name:
                self.project_key = project.key
                break
        else:
            self.project_key = None
            LOG.error("Project {0} not found".format(project_name))
        self._issues = client.search_issues(
            "project={0} AND type=Bug AND (status=resolved OR status=closed)".format(project_name),
            maxResults=False)
        LOG.info("Found {0} issues".format(len(self._issues)))

    def issue_data(self) -> dict:
        def transform_datetime(datetime_str: str):
            d = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            return d.strftime("%Y-%m-%d %H:%M:%S")

        def transform_versions(version_list: list):
            return "|".join([v.name for v in version_list])

        return {d.key: {
            "issue_key": d.key,
            "priority": d.fields.priority.name,
            "resolution": d.fields.resolution.name,
            "resolution_date": transform_datetime(d.fields.resolutiondate),
            "affect_versions": transform_versions(d.fields.versions),
            "fix_versions": transform_versions(d.fields.fixVersions)
        } for d in self._issues}
