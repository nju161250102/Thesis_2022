from datetime import datetime
import json
import requests

from Config import Config
from utils import LOG


class GitData(object):
    """
    使用Api从网络获取Git仓库信息
    """

    @staticmethod
    def filter_projects() -> list:
        """
        过滤出符合条件的Git项目，按Star数排序
        返回格式参见 https://docs.github.com/cn/rest/reference/repos#list-repository-languages
        :return:
        """
        header = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token " + Config.GIT_TOKEN
        }
        result = []
        req = requests.get(Config.GIT_SITE, headers=header)
        org_data = json.loads(req.text)
        page_size = 100
        for i in range(1, int(org_data["public_repos"] / page_size) + 2):
            req = requests.get(org_data["repos_url"],  params={"per_page": page_size, "page": i}, headers=header)
            for repo in json.loads(req.text):
                # 条件0:项目未被归档
                if repo["archived"]:
                    continue
                # 条件1:主要语言为Java
                if repo["language"] != "Java":
                    continue
                create_time = datetime.strptime(repo["created_at"], "%Y-%m-%dT%H:%M:%SZ")
                update_time = datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                # 条件2:创建距今大于两年
                if (datetime.now() - create_time).days < 365 * 2:
                    continue
                # 条件3:近一年内有更新
                if (datetime.now() - update_time).days > 365:
                    continue
                result.append(repo)
        LOG.info("Inclusion of projects:" + str(len(result)))
        result.sort(key=lambda r: r["stargazers_count"], reverse=True)
        return result
