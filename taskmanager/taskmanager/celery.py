from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем переменные окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')

# Создаем экземпляр Celery
app = Celery('taskmanager')

# Загружаем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Опции брокера
# app.conf.update(
#     broker_transport_options={
#         'visibility_timeout': 300,  # 5 минут для перезапуска зависших задач
#         'retry_on_timeout': True,   # Повторная попытка при таймауте
#     },
#     broker_connection_retry_on_startup=True
# )
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
# Автоматически находим задачи
