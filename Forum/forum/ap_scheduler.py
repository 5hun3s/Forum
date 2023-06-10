from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from .my_chat_bot_2 import MyChatBot
from .models import Comment, Forum
from django.contrib.auth.models import User

def periodic_execution():
    all_forum = Forum.objects.all()
    for forum in all_forum:
        texts = Comment.objects.filter(forum=forum)
        text = texts.order_by("created_at").reverse().first().text
        response = MyChatBot(text)
        Bot = User.objects.get(username="れな")
        bot_comment = Comment(user=Bot, text=response, forum=forum)
        bot_comment.save()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(periodic_execution, 'interval', minutes=40)#40分おきに実行
    scheduler.start()