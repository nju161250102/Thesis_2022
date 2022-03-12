"""
实验项目筛选脚本
筛选结果保存在数据目录下的 result.json
"""
import pandas as pd

from data import GitData, MavenData
from utils import PathUtils

if __name__ == "__main__":
    maven_url = "https://repo1.maven.org/maven2/org/apache/"
    if PathUtils.exist_path("project.csv"):
        git_result = pd.read_csv(PathUtils.join_path("project.csv")).to_dict(orient="records")
    else:
        git_result = []
        maven_projects = MavenData.list_project_names(maven_url)
        for repo in GitData.filter_projects():
            if repo["name"] not in maven_projects:
                continue
            git_result.append({
                "name": repo["name"],
                "url": repo["url"],
                "stars": repo["stargazers_count"],
                "create_time": repo["created_at"],
                "update_time": repo["updated_at"]
            })
        pd.DataFrame(git_result).to_csv(PathUtils.join_path("project.csv"), index=False, encoding="utf-8")
    maven_result = []
    for repo in git_result:
        print(repo["name"])
        sub_projects = MavenData.list_project_names(maven_url + repo["name"])
        for sub_name in ["", "-common", "-core"]:
            sub_name = repo["name"] + sub_name
            if sub_name in sub_projects:
                project_config = MavenData.search_versions("{0}{1}/{2}/".format(maven_url, repo["name"], sub_name))
                maven_result.append({
                    "name": repo["name"],
                    "sub_name": sub_name,
                    "version_num": len(project_config.versions),
                    "select_num": len(project_config.select)
                })
        pd.DataFrame(maven_result).to_csv(PathUtils.join_path("maven.csv"), index=False, encoding="utf-8")
