from django.contrib import admin
from django.utils import timezone
from .models import *


admin.site.register(Device)
admin.site.register(SubTime)
admin.site.register(SubscriptionDevice)
admin.site.register(Promotion)
@admin.register(Promocode)
class PromoAdmin(admin.ModelAdmin):
    # readonly_fields = ('replenished',)
    # prepopulated_fields = {"slug": ("company",)}
    list_display = ("name","promo","days","added_time")
@admin.register(Subscription)
class YourModelAdmin(admin.ModelAdmin):
    readonly_fields = ("user_id",)
    list_display = ('user_id',"company","try_promocode","promocode","unique_code")
    search_fields = ('user_id',)

    # def save_model(self, request, obj, form, change):
    #     if obj.days:
    #         obj.expires_at = timezone.now() + obj.days
    #     super().save_model(request, obj, form, change)


