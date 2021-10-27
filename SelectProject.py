"""
实验项目筛选脚本
筛选结果保存在数据目录下的 result.json
"""
import json
import os

from Config import Config
from data import JiraData, GitData
from utils import LOG

if __name__ == "__main__":
    jira_data = JiraData()
    jira_projects = jira_data.get_projects()
    project_dict = {p.key: p for p in jira_projects}
    result = []
    for repo in GitData.filter_projects():
        if repo["name"].upper() in project_dict.keys():
            issues = jira_data.get_issues(repo["name"].upper(), 100)
            LOG.info("{0} issues: {1}".format(repo["name"], len(issues)))
            if len(issues) == 100:
                result.append({
                    "name": repo["name"],
                    "url": repo["url"],
                    "default_branch": repo["default_branch"]
                })
            if len(result) >= 20:
                break
    print(result)
    with open(os.path.join(Config.DATA_DIR, "project.json"), "w") as f:
        f.write(json.dumps(result))
    # ['kafka', 'flink', 'rocketmq', 'hadoop', 'zookeeper',
    # 'cassandra', 'storm', 'zeppelin', 'beam', 'groovy', 'hbase',
    # 'ignite', 'hive', 'camel', 'shiro', 'kylin', 'nifi', 'calcite', 'curator', 'hudi']
