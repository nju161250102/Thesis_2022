from data import DataBuilder
from utils import PathUtils

if __name__ == "__main__":
    d = DataBuilder(PathUtils.join_path("giraph"), "Giraph")
    d.save(PathUtils.join_path("giraph2.csv"))
