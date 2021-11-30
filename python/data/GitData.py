import json
from datetime import datetime

import requests

from Config import Config
from Logger import LOG


class GitData(object):
    """
    使用Api从网络获取Git仓库信息
    """

    header = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token " + Config.GIT_TOKEN
    }

    @staticmethod
    def filter_projects() -> list:
        """
        过滤出符合条件的Git项目，按Star数排序
        返回格式参见 https://docs.github.com/cn/rest/reference/repos#list-organization-repositories
        :return:
        """
        result = []
        req = requests.get(Config.GIT_SITE, headers=GitData.header)
        org_data = json.loads(req.text)
        page_size = 100
        for i in range(1, int(org_data["public_repos"] / page_size) + 2):
            req = requests.get(org_data["repos_url"], params={"per_page": page_size, "page": i}, headers=GitData.header)
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

    @staticmethod
    def get_interval_commits(api_url: str):
        """
        2019.01.01到2021.01.01两年内的提交按4个月为间隔，选择出6个版本
        返回格式参见 https://docs.github.com/cn/rest/reference/repos#list-commits
        :param api_url: 仓库对应的API路径
        :return: 选取的commit列表
        """
        datetime_list = ["2019-01-01T00:00:00Z", "2019-05-01T00:00:00Z", "2019-09-01T00:00:00Z", "2020-01-01T00:00:00Z",
                         "2020-05-01T00:00:00Z", "2021-01-01T00:00:00Z"]
        time_intervals = [180000] * len(datetime_list)
        commit_result = [""] * len(datetime_list)
        for i in range(len(datetime_list) - 1):
            all_pages = []
            page_num = 1
            # 通过分页拉取时间段内的commit信息
            while True:
                req = requests.get(api_url + "/commits", headers=GitData.header, params={
                    "since": datetime_list[i],
                    "until": datetime_list[i + 1],
                    "per_page": 100,
                    "page": page_num
                })
                req_data = json.loads(req.text)
                if len(req_data) == 0:
                    break
                else:
                    page_num += 1
                    all_pages.extend(req_data)
            # 计算时间差，选择最接近的版本
            if len(all_pages) == 0:
                continue
            first_date = datetime.strptime(all_pages[0]["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")
            last_date = datetime.strptime(all_pages[-1]["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")
            first_delta = (first_date - datetime.strptime(datetime_list[i], "%Y-%m-%dT%H:%M:%SZ")).seconds
            last_delta = (datetime.strptime(datetime_list[i], "%Y-%m-%dT%H:%M:%SZ") - last_date).seconds
            if first_delta < time_intervals[i]:
                commit_result[i] = all_pages[0]
            if last_delta < time_intervals[i + 1]:
                commit_result[i + 1] = all_pages[-1]
        return commit_result
