from model import ProjectModel
from .AlarmService import AlarmService


def state_str(s: int):
    if s == 0:
        return "检测中"
    elif s == 1:
        return "审核中"
    elif s == 2:
        return "审核完成"
    else:
        return "未知"


class ProjectService(object):

    @staticmethod
    def get_list(state: int = -1) -> list:
        if state < 0:
            project_list = ProjectModel.select()
        else:
            project_list = ProjectModel.select().where(ProjectModel.state == state)
        project_list = project_list.order_by(-ProjectModel.create_time).dicts()
        for i in range(len(project_list)):
            project_list[i]["alarm_num"] = AlarmService.get_sum(project_list[i]["id"])
        return project_list

    @staticmethod
    def get_by_id(project_id: int) -> dict:
        project = ProjectModel.select().where(ProjectModel.id == project_id).dicts().get()
        project["state"] = state_str(project["state"])
        return project

    @staticmethod
    def get_by_name(project_name: str, version: str) -> dict:
        return ProjectModel.select().where(
            (ProjectModel.name == project_name) & (ProjectModel.version == version)).dicts().get()

    @staticmethod
    def save(**kwargs) -> int:
        project = ProjectModel(**kwargs)
        project.save()
        return project.id

    @staticmethod
    def get_last_version(name: str) -> str:
        project_list = ProjectModel.select().where(ProjectModel.name == name).order_by(-ProjectModel.create_time)
        if len(project_list) == 0:
            return ""
        else:
            return project_list.first().version

    @staticmethod
    def change_state(project_id: int, new_state: int):
        project = ProjectModel.get_by_id(project_id)
        project.state = new_state
        project.save()


class ProjectServiceStub(object):

    @staticmethod
    def get_list(state: int = -1) -> list:
        return [ProjectServiceStub.get_by_id(-1)]

    @staticmethod
    def get_by_id(project_id: int) -> dict:
        return {
            "name": "lucene",
            "version": "7.7.0",
            "upload_time": "2022-03-05 18:32:47",
            "description": "Just for Test",
            "state": 0,
            "alarm_num": "-",
        }

    @staticmethod
    def save(**kwargs):
        return True

    @staticmethod
    def get_last_version(name: str) -> str:
        return ""

    @staticmethod
    def get_by_name(project_name: str, version: str) -> dict:
        return ProjectServiceStub.get_by_id(-1)

    @staticmethod
    def change_state(project_id: int, new_state: int):
        pass
