import time

from peewee import AutoField, IntegerField, TextField

from .BaseModel import BaseModel


class ProjectModel(BaseModel):
    id = AutoField()
    name = TextField(null=True)
    version = TextField(null=True)
    description = TextField(null=True)
    # 0-检测中 1-审核中 2-审核完成
    state = IntegerField(null=True, default=0)
    create_time = TextField(null=True, default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    class Meta:
        table_name = "project"
