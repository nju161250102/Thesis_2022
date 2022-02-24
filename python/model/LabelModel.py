from peewee import AutoField, TextField, IntegerField

from .BaseModel import BaseModel


class LabelModel(BaseModel):
    id = AutoField()
    alarm_id = IntegerField(null=True)
    worker_id = IntegerField(null=True)
    value = IntegerField(null=True)
    create_time = TextField(null=True)

    class Meta:
        table_name = "worker"
