from celery import Celery

#第一步 创建celery
celery_app = Celery("lg")
#导入config
celery_app.config_from_object("celery_task.config")
#注册任务
celery_app.autodiscover_tasks(["celery_task.sms",])