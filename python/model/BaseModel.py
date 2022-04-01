from peewee import Model, SqliteDatabase

database = SqliteDatabase('./default.db')


class BaseModel(Model):
    class Meta:
        database = database
