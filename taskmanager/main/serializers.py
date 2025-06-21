from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from .models import *

class SubSerializer(serializers.ModelSerializer):
    class Meta:
        model=Subscription
        fields="__all__"

class TimeSerializer(serializers.ModelSerializer):
    class Meta:
        model=SubTime
        fields="__all__"

class PromocodeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Promocode
        fields="__all__"

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model=Device
        fields="__all__"

class SubscriptionDeviceSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name',read_only=True)
    device_id = serializers.CharField(source='device.id', read_only=True)
    # device = DeviceSerializer(read_only=True)
    class Meta:
        model=SubscriptionDevice
        fields = ['subscription',"device","added_time",'device_name',"device_id"]

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Promotion
        fields="__all__"