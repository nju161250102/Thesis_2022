from peewee import AutoField, TextField, IntegerField

from .BaseModel import BaseModel


class AlarmModel(BaseModel):
    id = AutoField()
    project_id = IntegerField(null=True)
    category = TextField(null=True)
    type = TextField(null=True)
    rank = IntegerField(null=True)
    path = TextField(null=True)
    classname = TextField(null=True)
    location = IntegerField(null=True)
    method = TextField(null=True)
    signature = TextField(null=True)
    create_time = TextField(null=True)

    class Meta:
        table_name = "alarm"
