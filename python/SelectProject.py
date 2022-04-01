"""
实验项目筛选脚本

直接运行，筛选结果保存在数据目录下的`project.csv`和`maven.csv`中。

- `project.csv`: 项目名、项目地址、Star数、创建时间、更新时间
- `maven.csv`: 项目名、子项目名、版本总数、实验选择范围内的版本数目

Maven仓库中各项目下有大量子项目，逐个筛选耗费时间，因此除原项目名外，
以特定后缀查找候选子项目，包括`-common`和`-core`。
"""
import pandas as pd

from data import GitData, MavenData
from utils import PathUtils

if __name__ == "__main__":
    maven_url = "https://repo1.maven.org/maven2/org/apache/"
    # 从project.csv中读取项目信息，不存在则从git查找
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
        sub_projects = MavenData.list_project_names(maven_url + repo["name"])
        # 以这些后缀查找候选子项目
        for suffix in ["", "-common", "-core"]:
            sub_name = repo["name"] + suffix
            if sub_name in sub_projects:
                project_config = MavenData.search_versions("{0}{1}/{2}/".format(maven_url, repo["name"], sub_name))
                maven_result.append({
                    "name": repo["name"],
                    "sub_name": sub_name,
                    "version_num": len(project_config.versions),
                    "select_num": len(project_config.select)
                })
        pd.DataFrame(maven_result).to_csv(PathUtils.join_path("maven.csv"), index=False, encoding="utf-8")
