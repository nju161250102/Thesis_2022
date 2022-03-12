from typing import List

from utils import PathUtils
from model import AlarmModel, Alarm


class AlarmService(object):

    @staticmethod
    def get_sum(project_id: int) -> int:
        return AlarmModel.select().where(AlarmModel.project_id == project_id).count()

    @staticmethod
    def get_by_id(alarm_id: str) -> AlarmModel:
        return AlarmModel.select().where(AlarmModel.id == alarm_id).dicts().get()

    @staticmethod
    def get_by_project(project_id: int) -> List[int]:
        return [alarm.id for alarm in AlarmModel.select().where(AlarmModel.project_id == project_id)]

    @staticmethod
    def get_code(alarm_id: str) -> str:
        alarm = AlarmService.get_by_id(alarm_id)
        try:
            with open(PathUtils.file_path(alarm.name, alarm.version, alarm.path)) as f:
                return "\n".join(f.readlines())
        except FileNotFoundError:
            return ""

    @staticmethod
    def save(alarm: Alarm, project_id: int) -> int:
        AlarmModel.create(id=alarm.index, category=alarm.category, type=alarm.type, rank=alarm.rank, path=alarm.path,
                          classname=alarm.class_name, method=alarm.method, signature=alarm.signature,
                          location=alarm.new_location, project_id=project_id)
        return alarm.index


class AlarmServiceStub(object):

    @staticmethod
    def get_alarm_sum(project_id: int):
        return 0

    @staticmethod
    def get_by_id(alarm_id: str):
        return {
            "id": 1,
            "project_id": 0,
            "category": "MALICIOUS_CODE",
            "type": "EI_EXPOSE_REP",
            "classname": "StopwordAnalyzerBase",
            "method": "getStopwordSet",
            "signature": "()Lorg/apache/lucene/analysis/CharArraySet;",
            "location": 2,
            "rank": 18,
            "priority": 2,
            "path": "org.apache.lucene.analysis.StopwordAnalyzerBase",
            "create_time": "2022-03-04 11:56:32"
        }

    @staticmethod
    def get_by_project(project_id: int) -> List[int]:
        return [1]

    @staticmethod
    def get_code(alarm_id: str) -> str:
        return "public static void main() {\n    return;\n}"

    @staticmethod
    def save(alarm: Alarm, project_id: int) -> int:
        return 0
