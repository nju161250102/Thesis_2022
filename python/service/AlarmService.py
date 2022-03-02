from typing import List

from utils import PathUtils
from model import AlarmModel, Alarm


class AlarmService(object):

    @staticmethod
    def get_sum(project_id: int) -> int:
        return AlarmModel.select().where(AlarmModel.project_id == project_id).count()

    @staticmethod
    def get_by_id(alarm_id: int) -> AlarmModel:
        return AlarmModel.select().where(AlarmModel.id == alarm_id).dicts().get()

    @staticmethod
    def get_by_project(project_id: int) -> List[int]:
        return [alarm.id for alarm in AlarmModel.select().where(AlarmModel.project_id == project_id)]

    @staticmethod
    def get_code(alarm_id: int) -> str:
        alarm = AlarmService.get_by_id(alarm_id)
        try:
            with open(PathUtils.file_path(alarm.name, alarm.version, alarm.path)) as f:
                return "\n".join(f.readlines())
        except FileNotFoundError:
            return ""

    @staticmethod
    def save(alarm: Alarm, project_id: int) -> int:
        alarm_model = AlarmModel(category=alarm.category, type=alarm.type, rank=alarm.rank, path=alarm.path,
                                 classname=alarm.class_name, method=alarm.method, signature=alarm.signature,
                                 location=alarm.new_location, project_id=project_id)
        alarm_model.save()
        return alarm_model.id


class AlarmServiceStub(object):

    @staticmethod
    def get_alarm_sum(project_id: int):
        return 0

    @staticmethod
    def get_by_id(alarm_id: int):
        return {
            "id": 1,
            "project_id": 0,
            "category": "CORRECTNESS",
            "type": "NP_NULL_PARAM_DEREF",
            "classname": "FuckThesis",
            "method": "test",
            "signature": "(IZIIIZZ)Lorg/apache/lucene/codecs/blocktree/BlockTreeTermsWriter$PendingBlock;",
            "location": 2,
            "path": "/src/test/FuckThesis.java"
        }

    @staticmethod
    def get_by_project(project_id: int) -> List[int]:
        return [1]

    @staticmethod
    def get_code(alarm_id: int) -> str:
        return "public static void main() {\n    return;\n}"

    @staticmethod
    def save(alarm: Alarm, project_id: int) -> int:
        return 0
