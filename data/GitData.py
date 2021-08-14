from datetime import datetime
from typing import List

from pydriller import Repository, Commit

from utils import LOG


class GitData(object):
    """
    从git的commit中提取信息
    """

    def __init__(self, repo_path: str):
        """
        :param repo_path: 本地仓库目录
        """
        self._repo = Repository(repo_path, 
                                to=(datetime(2021, 6, 30)),
                                only_modifications_with_file_types=[".java"])
        LOG.info("Git commit log from " + repo_path)

    def log_data(self) -> List[Commit]:
        return [m for m in self._repo.traverse_commits() if m.in_main_branch]
