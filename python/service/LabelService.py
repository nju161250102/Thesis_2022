import time
from typing import List

from model import WorkerModel, LabelModel


class LabelService(object):
    items_per_page = 15

    @staticmethod
    def _get_my_alarms(worker_id: int, label_flag: bool):
        if label_flag:
            return LabelModel.select().where((LabelModel.worker_id == worker_id) & (LabelModel.value != -1))
        else:
            return LabelModel.select().where((LabelModel.worker_id == worker_id) & (LabelModel.value == -1))

    @staticmethod
    def get_my_alarms(worker_id: int, label_flag: bool, page: int) -> List[str]:
        """获取工人被分配的待标记警告列表"""
        label_list = LabelService._get_my_alarms(worker_id, label_flag).paginate(page, LabelService.items_per_page)
        return [label.alarm_id for label in label_list]

    @staticmethod
    def page_count_my_alarms(worker_id: int, label_flag: bool) -> int:
        return int(LabelService._get_my_alarms(worker_id, label_flag).count() / LabelService.items_per_page)

    @staticmethod
    def get_by_alarm(alarm_id: str) -> dict:
        """根据警告ID获取对应的标记记录"""
        return LabelModel.select().where(LabelModel.alarm_id == alarm_id).dicts().get()

    @staticmethod
    def add_labels(alarm_id_set: set):
        """增加警告审核任务"""
        # 平均分配给系统的每个工人
        worker_id_list = WorkerModel.select(WorkerModel.id).distinct()
        for i, alarm_id in enumerate(alarm_id_set):
            label = LabelModel(alarm_id=alarm_id, worker_id=worker_id_list[i % len(worker_id_list)])
            label.save()

    @staticmethod
    def update_label(alarm_id: str, label_value: int):
        """更新警告的标记值"""
        label = LabelModel.get_or_none(LabelModel.alarm_id == alarm_id)
        label.value = label_value
        label.label_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        label.save()

    @staticmethod
    def check_all_labeled(alarm_id_set: set) -> bool:
        """检查集合中的警告是否都已经被标记过"""
        for label in LabelModel.select().where(LabelModel.alarm_id << alarm_id_set):
            if label.value == -1:
                return False
        return True


class LabelServiceStub(object):

    @staticmethod
    def get_my_alarms(worker_id: int, label_flag: bool, page: int) -> List[str]:
        return [""]

    @staticmethod
    def page_count_my_alarms(worker_id: int, label_flag: bool) -> int:
        return 2

    @staticmethod
    def get_by_alarm(alarm_id: str) -> dict:
        return {
            "alarm_id": alarm_id,
            "worker_id": 1,
            "value": 1,
            "create_time": "2022-03-04 14:26:09",
            "label_time": "2022-03-05 09:19:32"
        }

    @staticmethod
    def add_labels(alarm_id_set: set):
        pass

    @staticmethod
    def update_label(label_id: int, label_value: int):
        pass

    @staticmethod
    def check_all_labeled(alarm_id_set: set) -> bool:
        return True
