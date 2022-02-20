from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np

from model import Alarm


def draw_detected_rate(save_path: str, label_dict: Dict[str, List[int]]):
    fig, ax = plt.subplots(1, 1)
    for name, labels in label_dict.items():
        tp_num = 0
        tp_count = []
        for label in labels:
            if label == Alarm.TP:
                tp_num += 1
            if label == Alarm.UNKNOWN:
                continue
            tp_count.append(tp_num)
        ax.plot(np.arange(1, len(tp_count) + 1), np.array(tp_count) / np.sum(np.array(labels) == Alarm.TP), label=name)
    fig.legend(loc="lower right")
    fig.savefig(save_path)
    plt.close(fig)
