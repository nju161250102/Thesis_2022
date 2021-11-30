import re

import pandas as pd

from data import LocalGitData, JiraData
from Logger import LOG


class DataBuilder(object):
    """
    根据Issue key合并commit和issue记录
    """

    def __init__(self, local_path: str, jira_name: str):
        """
        :param local_path: 本地Git仓库目录
        :param jira_name: jira上的项目名
        """
        git_data = LocalGitData(local_path)
        jira_data = JiraData(jira_name)
        project_id = jira_data.project_key
        jira_dict = jira_data.issue_data()
        self._data = []
        pattern = re.compile('{0}-(\\d+)'.format(project_id))
        for commit in git_data.log_data():
            match = pattern.match(commit.msg)
            if match and match.group(0) in jira_dict.keys():
                d = jira_dict[match.group(0)]
                d.update({'commit_id': commit.hash,
                          'commit_title': commit.msg.split('\n')[0],
                          'commit_date': commit.committer_date.strftime('%Y-%m-%d %H:%M:%S'),
                          'changed_files': commit.files,
                          'insertions': commit.insertions,
                          'deletions': commit.deletions})
                self._data.append(d)
        else:
            LOG.info('Commits and issues matched {0}'.format(len(self._data)))

    def save(self, target_path):
        df = pd.DataFrame(self._data)
        df.to_csv(target_path, index=False)
