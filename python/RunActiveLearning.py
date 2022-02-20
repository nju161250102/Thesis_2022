from active import ActiveLearningModel
from pic import draw_detected_rate
from utils import DataUtils, PathUtils


if __name__ == "__main__":
    project_name = "lucene-core"#sys.argv[1]
    # feature_df = pd.read_csv(PathUtils.feature_path(project_name + ".csv"), index_col="index")
    # report_df = pd.read_csv(PathUtils.report_path(project_name + ".csv"), index_col="index")
    config = {
        "init_sample": {
            "name": "random",
            "sample_num": 10,
            "stop_threshold": 1,
            "cluster_n": 5
        },
        "learn_model": {
            "name": "bagging"
        },
        "query_strategy": {
            "name": "certain_query",
            "max_num": 5
        },
        "stop_strategy": {
            "name": "never"
        }
    }
    project_config = DataUtils.read_project_config("lucene-core")
    for version, train_df, test_df in DataUtils.train_and_test_df(project_config):
        train_feature_df = DataUtils.to_feature_df(project_config, train_df.index)
        test_feature_df = DataUtils.to_feature_df(project_config, test_df.index)
        model = ActiveLearningModel(train_feature_df, config=config)
        model.run()
        pic_data = {
            "train": model.rank_labels(),
            "test": model.rank_labels(test_feature_df)
        }
        draw_detected_rate(PathUtils.feature_path("lucene#{0}.png".format(version)), pic_data)
