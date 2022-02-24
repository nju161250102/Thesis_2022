from peewee import Model, SqliteDatabase

database = SqliteDatabase('../my.db')


class BaseModel(Model):
    class Meta:
        database = database
