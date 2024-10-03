from app.database.models import *
from random import randint, choice
from config import *

# with db:
#     User.insert({"tg_id": 12, "available_time": 13, "all_uploaded_time": 122}).execute()
with db:
    db.create_tables([User, Video])


async def registration(tg_id):
    with db:
        if User.get_or_none(User.tg_id == tg_id) is None:
            User.insert({"tg_id": tg_id,
                         "available_time": 300,
                         "all_uploaded_time": 0,
                         "admin": False,
                         "mode": "default"}).execute()

            return True
        return False


async def get_profile(tg_id):
    with db:
        user = User.get(User.tg_id == tg_id)
        return user.available_time, user.all_uploaded_time, user.admin


async def is_user_admin(tg_id):
    with db:
        if User.get_or_none(User.tg_id == tg_id) is None:
            return False
        else:
            return User.get(User.tg_id == tg_id).admin


async def get_available_time(tg_id):
    with db:
        return User.get(User.tg_id == tg_id).available_time


async def reduce_time(tg_id, video_duration):
    with db:
        user = User.get(User.tg_id == tg_id)
        user.available_time = user.available_time - video_duration
        user.save()


async def add_time(tg_id, time, buy=False):
    with db:
        user = User.get(User.tg_id == tg_id)
        user.available_time = user.available_time + time
        if not buy:
            user.all_uploaded_time = user.all_uploaded_time + time
        user.save()


async def get_user_mode(tg_id):
    with db:
        user = User.get_or_none(User.tg_id == tg_id)
        if user is not None:
            return User.get(User.tg_id == tg_id).mode
        else:
            return "default"     # для пользователей которых нет в базе


async def set_mode(tg_id, mode):
    with db:
        user = User.get(User.tg_id == tg_id)
        User.set_by_id(user.id, {"mode": mode})


async def upload_video_to_datadase(message):
    with db:
        video = Video.get_or_none(Video.tg_hash == message.video.file_id)
        if video:
            pass
            # await message.answer("Такое видео уже есть в базе. Время за него не начислено")
        else:
            Video.insert({"user_uploaded_id": message.from_user.id, "tg_hash": message.video.file_id, "duration": message.video.duration, "likes": 0, "dislikes": 0, "requires_verification": False}).execute()
            # await message.answer(f"+{round(message.video.duration/60, 2)} минут")     # сделать, чтобы писалось итоговое время
            await add_time(message.from_user.id, message.video.duration)


async def remove_video(video_hash):
    with db:
        # video = Video.get(Video.tg_hash == video_hash)
        Video.delete().where(Video.tg_hash == video_hash).execute()


async def get_random_video():
    # database_len = Video.select().count()
    # while True:     # чтобы скипались видео на которые пожаловались
    #     video_id = randint(1, database_len - 1)
    #     video = Video.get(Video.id == video_id)
    #     print(video.requires_verification)
    #     if not video.requires_verification:
    #         return video
    videos = Video.select().where(Video.requires_verification == 0)
    return choice(videos)


async def get_likes_and_dislikes(video_hash):
    with db:
        video = Video.get(Video.tg_hash == video_hash)
        return video.likes, video.dislikes
        # return 1, 1


async def add_new_like(video_hash):
    with db:
        video = Video.get(Video.tg_hash == video_hash)
        video.likes = video.likes + 1
        video.save()


async def add_new_dislike(video_hash):
    with db:
        video = Video.get(Video.tg_hash == video_hash)
        video.dislikes = video.dislikes + 1
        video.save()


async def mark_dangerous(video_hash):
    with db:
        video = Video.get(Video.tg_hash == video_hash)
        video.requires_verification = True
        video.save()


async def mark_non_dangerous(video_hash):
    with db:
        video = Video.get(Video.tg_hash == video_hash)
        video.requires_verification = False
        video.save()


async def get_count_of_dangerous_videos():
    with db:
        return Video.select().where(Video.requires_verification == 1).count()


async def get_requires_verification_video():
    with db:
        return Video.select().where(Video.requires_verification == 1)[0].tg_hash


async def permanent_ban_user(video_hash):
    with db:
        user = User.get(User.tg_id == Video.get(Video.tg_hash == video_hash).user_uploaded_id)
        user.mode = "ban"
        user.save()
