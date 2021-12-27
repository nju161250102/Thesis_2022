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
    def exist_path(*path_args) -> bool:
        """
        判断路径是否存在
        """
        return os.path.exists(os.path.join(Config.DATA_DIR, *path_args))

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
    def file_path(*path_args):
        """
        Java文件副本目录下路径拼接
        """
        return os.path.join(Config.DATA_DIR, "file", *path_args)

    @staticmethod
    def report_path(*path_args):
        """
        扫描报告目录下路径拼接
        """
        return os.path.join(Config.DATA_DIR, "report", *path_args)

    @staticmethod
    def feature_path(*path_args):
        """
        警告特征目录下路径拼接
        """
        return os.path.join(Config.DATA_DIR, "feature", *path_args)

    @staticmethod
    def picture_path(*path_args):
        """
        输出图片目录下路径拼接
        """
        return os.path.join(Config.DATA_DIR, "pic", *path_args)

