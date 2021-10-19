# 实验项目筛选脚本
from data import JiraData, GitData

if __name__ == "__main__":
    jira_projects = JiraData().get_projects()
    names_list = list(map(lambda p: p.key, jira_projects))
    result = []
    for repo in GitData.filter_projects():
        if repo["name"].upper() in names_list:
            result.append({
                "name": repo["name"],
                "star": repo["stargazers_count"]
            })
        if len(result) >= 20:
            break
    print(result)
    # [{'name': 'dubbo', 'star': 36300}, {'name': 'kafka', 'star': 20127}, {'name': 'flink', 'star': 17324}, {'name': 'rocketmq', 'star': 15634}, {'name': 'hadoop', 'star': 12009}, {'name': 'zookeeper', 'star': 9914}, {'name': 'pulsar', 'star': 9756}, {'name': 'cassandra', 'star': 6912}, {'name': 'storm', 'star': 6279}, {'name': 'zeppelin', 'star': 5420}, {'name': 'beam', 'star': 5031}, {'name': 'groovy', 'star': 4303}, {'name': 'hbase', 'star': 4229}, {'name': 'ignite', 'star': 4003}, {'name': 'hive', 'star': 3946}, {'name': 'camel', 'star': 3945}, {'name': 'shiro', 'star': 3632}, {'name': 'pinot', 'star': 3604}, {'name': 'kylin', 'star': 3168}, {'name': 'nifi', 'star': 2837}]
