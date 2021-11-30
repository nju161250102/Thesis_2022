from data import DataBuilder, MavenData, GitData
from Config import Config
import json
import os

if __name__ == "__main__":
    # d = DataBuilder(PathUtils.join_path("giraph"), "Giraph")
    # d.save(PathUtils.join_path("giraph2.csv"))
    # j = JiraData()
    # d = GitData.get_interval_commits("https://api.github.com/repos/apache/kafka")
    # print(list(map(lambda c: c["sha"], d)))
    # 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
    project_urls = {
        "kafka": "https://repo1.maven.org/maven2/org/apache/kafka/kafka_2.12/",
        "": ""
    }
    versions = MavenData.search_versions("https://repo1.maven.org/maven2/org/apache/kafka/kafka_2.12/")
    with open(os.path.join(Config.DATA_DIR, "linshi.json"), "w") as f:
        f.write(json.dumps(versions))
