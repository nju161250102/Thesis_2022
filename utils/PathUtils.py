import os
from Config import Config


class PathUtils(object):

    @staticmethod
    def join_path(*path_args):
        return os.path.join(Config.DATA_DIR, *path_args)
