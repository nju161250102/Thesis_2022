from active import ActiveLearningModel
from pic import draw_detected_rate
from utils import DataUtils, PathUtils


if __name__ == "__main__":
    project_name = "lucene-core"#sys.argv[1]
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
    for version, pre_df, cur_df in DataUtils.iter_version_df(project_config):
        pre_feature_df = DataUtils.to_feature_df(project_config, pre_df.index)
        cur_feature_df = DataUtils.to_feature_df(project_config, cur_df.index)
        model = ActiveLearningModel(config=config)
        model.run(cur_feature_df)
        pic_data = {
            "train": model.rank_labels(),
            "test": model.rank_labels(pre_feature_df)
        }
        draw_detected_rate(PathUtils.feature_path("lucene#{0}.png".format(version)), pic_data)
