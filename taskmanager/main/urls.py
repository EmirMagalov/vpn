from django.urls import path,include
from .views import *
from rest_framework import routers


router=routers.DefaultRouter()
router.register(r'sub',SubViewsSet)
router.register(r'time',TimeViewsSet)
router.register(r'device',DeviceViewsSet)
router.register(r'subdevice',SubscriptionDeviceViewsSet)
router.register(r'promo',PromocodeViewsSet),
router.register(r'promotion',PromotionViewsSet)
print(router.urls)
urlpatterns = [

    path("api/",include(router.urls)),
    # path('start-task/<int:user_id>/', start_decrease_days_task, name='start_decrease_days_task'),
    path('stop-task/<int:user_id>/', stop_task_view, name='stop_task'),
    path('start_mailing_task/',start_mailing_task,name='start_mailing_task')
]