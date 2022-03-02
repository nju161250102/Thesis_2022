from model import WorkerModel


class WorkerService(object):

    @staticmethod
    def login(username: str, password: str) -> int:
        """
        登录系统，admin为管理员直接登录，否则作为工人处理
        :param username: 用户名
        :param password: 密码
        :return: 返回ID，管理员为-1，登录失败返回-2
        """
        if username == "admin":
            return -1
        worker = WorkerModel.get(WorkerModel.username == username)
        if worker is not None and worker.password == password:
            return worker.id
        return -2


class WorkerServiceStub(object):

    @staticmethod
    def login(username: str, password: str) -> int:
        if username == "admin" or password == "1":
            return -1
        else:
            return -2
