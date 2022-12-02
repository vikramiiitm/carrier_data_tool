import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carrier_data_tool.settings')

app = Celery('carrier_data_tool')

app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.beat_schedule = {
#     "every day between 8 AM & 11 PM": {
#         "task": "driver.tasks.driver_pool_selection_driver_notification",  # <---- Name of task
#         "schedule": crontab(hour='8,11',
#                             minute=0,
#                             ),
#         # 'args': (16, 16)
#     }
#
# }

app.autodiscover_tasks()


@app.task(bind=True)
def debug_tasks(self):
    print('Request: {0!r}'.format(self.request))
