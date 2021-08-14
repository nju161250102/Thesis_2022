# uncompyle6 version 3.7.4
# Python bytecode 3.8 (3413)
# Decompiled from: Python 3.8.5 (default, Sep  4 2020, 07:30:14) 
# [GCC 7.3.0]
# Embedded file name: /home/qian/Document/研究生毕业论文/Thesis_2022/utils/PathUtils.py
# Compiled at: 2021-08-14 15:36:15
# Size of source mod 2**32: 173 bytes
import os
from Config import Config

class PathUtils(object):

    @staticmethod
    def join_path(*path_args):
        return (os.path.join)(Config.WORKING_DIR, *path_args)