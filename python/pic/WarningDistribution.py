from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def num_in_method(data_df: pd.DataFrame, save_path: str):
    result = defaultdict(int)
    for method_index, method_df in data_df.groupby(["class_name"]):
        count_axis = (len(method_df[method_df["label"] == 0]), len(method_df[method_df["label"] == 1]))
        result[count_axis] += 1
    x, y = zip(*result.keys())
    sizes = list(result.values())
    fig, ax = plt.subplots()
    ax.scatter(x, y, s=sizes, vmin=0, vmax=20)
    ax.set(xlim=(-1, max(5, max(x))), xticks=np.arange(0, max(x) + 1),
           ylim=(-1, max(5, max(y))), yticks=np.arange(0, max(y) + 1))
    ax.grid(True)
    fig.savefig(save_path)
    plt.close(fig)
