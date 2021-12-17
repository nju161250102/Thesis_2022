import sys
import pandas as pd

from active import ActiveLearningModel
from utils import PathUtils


if __name__ == "__main__":
    project_name = sys.argv[1]
    df = pd.read_csv(PathUtils.feature_path(project_name + ".csv"), index_col="index")
    config = {
        "init_sample": {
            "name": "kmeans",
            "sample_num": 10,
            "stop_threshold": 2,
            "cluster_n": 15
        },
        "learn_model": {
            "name": "one_class_svm"
        },
        "query_strategy": {
            "name": "uncertain",
            "max_num": 50
        },
        "stop_strategy": {
            "name": "never"
        }
    }
    model = ActiveLearningModel(df, config=config)
    model.run()
    data_df = pd.DataFrame(model.metrics_records)
    data_df.to_csv(PathUtils.report_path("temp.csv"))
