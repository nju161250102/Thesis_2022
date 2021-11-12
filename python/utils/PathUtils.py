import os
import shutil

from Config import Config


class PathUtils(object):

    @staticmethod
    def rebuild_dir(dir_path: str, skip=False) -> bool:
        """
        删除并重新建立文件夹
        :param dir_path: 文件夹路径
        :param skip: 文件夹存在时是否跳过
        :return 是否新建了文件夹
        """
        if os.path.exists(dir_path):
            if skip:
                return False
            else:
                shutil.rmtree(dir_path)
        os.mkdir(dir_path)
        return True

    @staticmethod
    def join_path(*path_args):
        """
        数据目录下路径拼接
        """
        return os.path.join(Config.DATA_DIR, *path_args)

    @staticmethod
    def project_path(*path_args):
        """
        项目目录下路径拼接
        """
        return os.path.join(Config.DATA_DIR, "project", *path_args)

    @staticmethod
    def report_path(*path_args):
        """
        扫描报告目录下路径拼接
        """
        return os.path.join(Config.DATA_DIR, "report", *path_args)

    @staticmethod
    def alarm_path(*path_args):
        """
        误报警告目录下路径拼接
        """
        return os.path.join(Config.DATA_DIR, "alarm", *path_args)


