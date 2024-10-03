from peewee import *

db = SqliteDatabase("C:/Users/Михаил/PycharmProjects/video_exchange_tg_bot/app/database/database.db")


class User(Model):
    id = PrimaryKeyField(unique=True)
    tg_id = IntegerField()
    available_time = IntegerField()
    all_uploaded_time = IntegerField()
    admin = BooleanField()
    mode = CharField()

    class Meta:
        database = db
        order_by = "tg_id"
        db_table = "users"


class Video(Model):
    id = PrimaryKeyField(unique=True)
    user_uploaded_id = IntegerField()
    tg_hash = CharField()
    duration = IntegerField()
    likes = IntegerField()
    dislikes = IntegerField()
    requires_verification = BooleanField()

    class Meta:
        database = db
        db_table = "videos"


