from celery_task.main import celery_app
from django.core.mail import send_mail
from django.conf import settings


#retry_backoff 间隔时间
@celery_app.tasks(bind=True,name="send_email",retry_backoff=3)
def send_email(self,email,verify_url):
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
    try:
        send_mail(subject="LG商城邮箱验证",message="",from_email=settings.EMAIL_FROM,recipient_list=[email],html_message=html_message)
    except Exception as e:
        raise self.retry(exc=e,max_retries=3)
