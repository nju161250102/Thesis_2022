import sys
import pandas as pd

from active import ActiveLearningModel
from utils import PathUtils


if __name__ == "__main__":
    project_name = sys.argv[1]
    feature_df = pd.read_csv(PathUtils.feature_path(project_name + ".csv"), index_col="index")
    report_df = pd.read_csv(PathUtils.report_path(project_name + ".csv"), index_col="index")
    config = {
        "init_sample": {
            "name": "random",
            "sample_num": 10,
            "stop_threshold": 2,
            "cluster_n": 15
        },
        "learn_model": {
            "name": "bagging"
        },
        "query_strategy": {
            "name": "certain_query",
            "max_num": 100
        },
        "stop_strategy": {
            "name": "never"
        }
    }
    model = ActiveLearningModel(feature_df, next_dict=report_df["next"].to_dict(), config=config)
    model.run()
    data_df = pd.DataFrame(model.metrics_records)
    data_df.to_csv(PathUtils.report_path("temp_mlp.csv"))
