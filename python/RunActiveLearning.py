import sys
import pandas as pd

from active import ActiveLearningModel
from utils import PathUtils


if __name__ == "__main__":
    project_name = sys.argv[1]
    df = pd.read_csv(PathUtils.feature_path(project_name + ".csv"), index_col="index")
    model = ActiveLearningModel(df)
    model.set_init_sample(name="random", sample_num=10, stop_threshold=1)
    model.set_stop_strategy(name="never")
    model.set_learning_model(name="svm")
    model.set_query_strategy(name="uncertain", max_num=20)
    model.run()
    data_df = pd.DataFrame(model.metrics_records)
    data_df.to_csv(PathUtils.report_path("temp.csv"))
