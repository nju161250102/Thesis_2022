from typing import List

from model import LabelModel


class LabelService(object):

    @staticmethod
    def get_my_alarms(worker_id: int, label_flag: bool) -> List[int]:
        if label_flag:
            return [label.alarm_id for label in LabelModel.select()
                .where((LabelModel.worker_id == worker_id) & (LabelModel.value != -1))]
        else:
            return [label.alarm_id for label in LabelModel.select()
                .where((LabelModel.worker_id == worker_id) & (LabelModel.value == -1))]

    @staticmethod
    def get_by_alarm(alarm_id: int) -> dict:
        return LabelModel.select().where(LabelModel.alarm_id == alarm_id).dicts().get()

    @staticmethod
    def update_label(alarm_id: int, label_value: int):
        label = LabelModel.get_or_none(LabelModel.alarm_id == alarm_id)
        label.value = label_value
        label.save()


class LabelServiceStub(object):

    @staticmethod
    def get_my_alarms(worker_id: int, label_flag: bool) -> List[int]:
        return [0]

    @staticmethod
    def get_by_alarm(alarm_id: int) -> dict:
        return {
            "alarm_id": alarm_id,
            "worker_id": 1,
            "value": 1
        }

    @staticmethod
    def update_label(label_id: int, label_value: int):
        pass
