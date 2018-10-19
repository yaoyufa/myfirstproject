from celery import Celery
from django.core.mail import send_mail
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myfirst_web.settings")

app = Celery('celery_tasks.task', broker='redis://192.168.12.196:6379/3')

@app.task
def task_celery_tasks(subject,message,sender,receive,html_message):
    print("发邮件begin....")
    import time
    time.sleep(10)
    send_mail(subject, message, sender, receive, html_message=html_message)
    print("发邮件end....")