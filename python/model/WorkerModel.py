from peewee import AutoField, TextField

from .BaseModel import BaseModel


class WorkerModel(BaseModel):
    id = AutoField()
    name = TextField(null=True)
    email = TextField(null=True)
    password = TextField(null=True)

    class Meta:
        table_name = "worker"
