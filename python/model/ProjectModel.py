from peewee import AutoField, TextField

from .BaseModel import BaseModel


class ProjectModel(BaseModel):
    id = AutoField()
    name = TextField(null=True)
    version = TextField(null=True)
    description = TextField(null=True)
    create_time = TextField(null=True)

    class Meta:
        table_name = "worker"
