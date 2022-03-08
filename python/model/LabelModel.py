import time

from peewee import AutoField, TextField, IntegerField

from .BaseModel import BaseModel


class LabelModel(BaseModel):
    id = AutoField()
    alarm_id = TextField()
    worker_id = IntegerField(null=True)
    value = IntegerField(null=True, default=-1)
    label_time = TextField(null=True, default="")
    create_time = TextField(null=True, default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    class Meta:
        table_name = "label"
