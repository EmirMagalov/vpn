from django.db import models
from datetime import timedelta
# Create your models here.


class SubTime(models.Model):
    time=models.CharField(max_length=255)


    def __str__(self):
        return f"Time_{self.time}"
    class Meta:
        app_label = 'main'
class Device(models.Model):
    name=models.CharField(max_length=255)
    file_id=models.CharField(max_length=255,null=True,blank=True)
    added_time = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.pk}{self.name}"


class Subscription(models.Model):
    user_id=models.BigIntegerField(verbose_name="Id тпользователя в тг")
    look_promotion=models.CharField(blank=True,null=True,max_length=255)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата окончания подписки")
    days = models.IntegerField(default=0,verbose_name="Дни подписки")
    task = models.BooleanField(default=False,verbose_name="Запущена ли фоновая задача (Убавление времени)")
    replenished = models.IntegerField(default=0, verbose_name="Пополнено")
    company=models.CharField(max_length=255,blank=True,null=True,verbose_name="Кампания")
    pay = models.BooleanField(default=False, verbose_name="Пополнено ли средств")
    try_promocode=models.IntegerField(default=0,verbose_name="Попытка ввести промокод")
    promocode=models.TextField(blank=True,null=True,default=" ", verbose_name="Активный промокод")
    unique_code=models.CharField(max_length=255,blank=True,null=True,verbose_name="Код vless")
    def __str__(self):
        return f"User_{self.user_id}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
class SubscriptionDevice(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="subscription_devices")
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    added_time = models.DateTimeField(auto_now_add=True)  # Время добавления устройства

    class Meta:
        unique_together = ('subscription', 'device')

    def __str__(self):
        return f"Subscription_{self.subscription.user_id} -> Device_{self.device.name} at {self.added_time}"


class Promocode(models.Model):
    name=models.CharField(max_length=255,verbose_name="Название")
    promo=models.CharField(max_length=255,verbose_name="Сам промокод")
    days=models.IntegerField(default=0,verbose_name="Количество дней промокода")
    slug=models.CharField(max_length=255,verbose_name="ID рекламной кампании",blank=True,null=True)
    added_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Помокоды"
        verbose_name_plural = "Промокоды"

class Promotion(models.Model):
    promotion=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} {self.promotion}"

    def save(self, *args, **kwargs):
        # Проверяем, если объект уже существует, то не создаем новый
        if not self.pk and Promotion.objects.exists():
            raise ValueError("Можно создать только один объект модели Promotion.")
        super().save(*args, **kwargs)