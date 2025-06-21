from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from datetime import datetime
import pytz
from rest_framework import generics,viewsets
from .serializers import *
from .tasks import stop_task,mailing_list
from django.http import JsonResponse
from asgiref.sync import async_to_sync

class PromotionViewsSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all()
    serializer_class = PromotionSerializer

    @action(methods=["get"], detail=False)
    def getpromotion(self, request):
        # user_id = request.query_params.get("user_id")
        try:
            sub = Promotion.objects.get(id=1)
            serializer = PromotionSerializer(sub)
            return Response(serializer.data)
        except Promotion.DoesNotExist:
            return Response({"detail": "Пост не найден."}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=["put"], detail=False)
    def putpromotion(self, request):
        # user_id = request.data.get("user_id")

        try:
            # Получаем пост по message_id
            post = Promotion.objects.get(id=1)
        except Promotion.DoesNotExist:
            return Response({"detail": "Пост не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Используем сериализатор для валидации и обновления
        serializer = PromotionSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Сохраняем изменения в БД
            return Response(serializer.data)  # Возвращаем обновлённые данные
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceViewsSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    def get_queryset(self):
        pk = self.kwargs.get("pk")

        if pk:
            return Device.objects.filter(pk=pk)
        else:
            return Device.objects.all().order_by("added_time")


class TimeViewsSet(viewsets.ModelViewSet):
    queryset = SubTime.objects.all()
    serializer_class = TimeSerializer
    def get_queryset(self):
        pk = self.kwargs.get("pk")

        if pk:
            return SubTime.objects.filter(pk=pk)
        else:
            return SubTime.objects.all()


class SubViewsSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubSerializer
    def get_queryset(self):
        pk = self.kwargs.get("pk")

        if pk:
            return Subscription.objects.filter(pk=pk)
        else:
            return Subscription.objects.all()

    @action(methods=["get"], detail=False)
    def getusersub(self, request):
        user_id = request.query_params.get("user_id")
        try:
            sub = Subscription.objects.get(user_id=user_id)
            serializer = SubSerializer(sub)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response({"detail": "Пост не найден."}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=["get"], detail=False)
    def getusercompany(self, request):
        company = request.query_params.get("company")
        try:
            sub = Subscription.objects.filter(company=company)
            serializer = SubSerializer(sub,many=True)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response({"detail": "Пост не найден."}, status=status.HTTP_404_NOT_FOUND)
    @action(methods=["get"], detail=False)
    def getuserpromo(self, request):
        promo = request.query_params.get("promo")
        print(promo)
        sub = Subscription.objects.filter(promocode=promo)
        serializer = SubSerializer(sub,many=True)
        return Response(serializer.data)

    @action(methods=["get"], detail=False)
    def getusernotpromo(self, request):
        promo = request.query_params.get("promo")

        sub = Subscription.objects.exclude(promocode=promo)
        serializer = SubSerializer(sub,many=True)
        return Response(serializer.data)

    @action(methods=["post"], detail=False)
    def subpost(self, request):
        user_id = request.data.get("user_id")
        expires_at_str = request.data.get("expires_at")
        company = request.data.get("company")
        days = request.data.get("days")
        if not expires_at_str:
            return Response({"error": "expires_at не указан"}, status=400)

        try:
            # Конвертация строки в datetime (ожидается ISO формат)
            expires_at = datetime.fromisoformat(expires_at_str)

            # Если нужно, добавь локализацию (например, Москва)
            moscow_tz = pytz.timezone("Europe/Moscow")
            if expires_at.tzinfo is None:
                expires_at = moscow_tz.localize(expires_at)
            else:
                expires_at = expires_at.astimezone(moscow_tz)

        except ValueError:
            return Response({"error": "Некорректный формат expires_at"}, status=400)

        post, created = Subscription.objects.get_or_create(
            user_id=user_id,
            company=company,
            days=days,
            defaults={"expires_at": expires_at}
        )

        serializer = SubSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(methods=["put"], detail=False)
    def subput(self, request):
        user_id = request.data.get("user_id")

        try:
            # Получаем пост по message_id
            post = Subscription.objects.get(user_id=user_id)
        except Subscription.DoesNotExist:
            return Response({"detail": "Пост не найден."}, status=status.HTTP_404_NOT_FOUND)

        # Используем сериализатор для валидации и обновления
        serializer = SubSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Сохраняем изменения в БД
            return Response(serializer.data)  # Возвращаем обновлённые данные
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubscriptionDeviceViewsSet(viewsets.ModelViewSet):
    queryset = SubscriptionDevice.objects.all()
    serializer_class = SubscriptionDeviceSerializer

    @action(methods=["get"], detail=False)
    def getsubdev(self, request):
        user_id = request.query_params.get("user_id")

        sub = SubscriptionDevice.objects.filter(subscription__user_id=user_id)
        serializer = SubscriptionDeviceSerializer(sub, many=True)
        return Response(serializer.data)



    @action(methods=["post"], detail=False)
    def subdevicepost(self, request):
        subscription_id= request.data.get("subscription")
        device_id = request.data.get("device")
        # Проверяем, что оба идентификатора были переданы
        if not subscription_id or not device_id:
            return Response({"error": "'subscription' and 'device' are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Получаем объекты Subscription и Device из базы данных
            subscription = Subscription.objects.get(id=subscription_id)
            device = Device.objects.get(id=device_id)
        except Subscription.DoesNotExist:
            return Response({"error": "Subscription not found."}, status=status.HTTP_404_NOT_FOUND)
        except Device.DoesNotExist:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)

        # Используем get_or_create для создания записи или получения существующей
        post, created = SubscriptionDevice.objects.get_or_create(subscription=subscription, device=device)

        # Если запись уже существует, возвращаем ошибку
        if not created:
            return Response({"error": "This subscription-device pair already exists."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Если запись была создана, сериализуем и возвращаем данные
        serializer = SubscriptionDeviceSerializer(post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=["delete"], detail=False)
    def deletesubdev(self, request):
        user_id = request.query_params.get("user_id")
        device=request.query_params.get("device")
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем записи для удаления
        sub_devices = SubscriptionDevice.objects.filter(subscription__user_id=user_id,device__name=device)

        if not sub_devices.exists():
            return Response({"message": "No subscription devices found for the user"}, status=status.HTTP_404_NOT_FOUND)

        # Удаляем записи
        deleted_count, _ = sub_devices.delete()

        return Response({"message": f"Deleted {deleted_count} subscription devices successfully"},
                        status=status.HTTP_200_OK)

    @action(methods=["delete"], detail=False)
    def deletesubdevall(self, request):
        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Получаем записи для удаления
        sub_devices_all = SubscriptionDevice.objects.filter(subscription__user_id=user_id)

        if not sub_devices_all.exists():
            return Response({"message": "No subscription devices found for the user"}, status=status.HTTP_404_NOT_FOUND)

        # Удаляем записи
        deleted_count, _ = sub_devices_all.delete()

        return Response({"message": f"Deleted {deleted_count} subscription devices successfully"},
                        status=status.HTTP_200_OK)


class PromocodeViewsSet(viewsets.ModelViewSet):
    queryset = Promocode.objects.all()
    serializer_class = PromocodeSerializer
    def get_queryset(self):
        pk = self.kwargs.get("pk")

        if pk:
            return Promocode.objects.filter(pk=pk)
        else:
            return Promocode.objects.all()

    @action(methods=["post"], detail=False)
    def postpromocode(self, request):
        name = request.data.get("name")
        promo=request.data.get("promo")
        days = request.data.get("days")
        slug = request.data.get("slug")
        print(name)
        print(promo)
        print(days)
        print(slug)
        # Проверяем, что оба идентификатора были переданы
        if not name or not promo:
            return Response({"error": "'subscription' and 'device' are required."},
                            status=status.HTTP_400_BAD_REQUEST)



        # Используем get_or_create для создания записи или получения существующей
        promocode, created = Promocode.objects.get_or_create(name=name,promo=promo,days=days,slug=slug)
        serializer = self.get_serializer(promocode)
        return Response(
            {"message": "Promocode created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

        # Если запись уже существует, возвращаем ошибку
        # if not created:
        #     return Response({"error": "This subscription-device pair already exists."},
        #                     status=status.HTTP_400_BAD_REQUEST)
    @action(methods=["get"], detail=False)
    def getpromocode(self, request):
        promo = request.query_params.get("promo")

        sub = Promocode.objects.get(promo=promo)
        serializer = PromocodeSerializer(sub)
        return Response(serializer.data)

    @action(methods=["put"], detail=False)
    def promocodeput(self, request):
        promo = request.data.get("promo")

        try:
            # Получаем пост по message_id
            post = Promocode.objects.get(promo=promo)
        except Promocode.DoesNotExist:
            return Response({"detail": "Пост не найден."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PromocodeSerializer(post, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # Сохраняем изменения в БД
            return Response(serializer.data)  # Возвращаем обновлённые данные
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






from django.views.decorators.csrf import csrf_exempt
# @csrf_exempt
# def start_decrease_days_task(request, user_id):
#     """
#     API для запуска задачи decrease_days.
#     """
#     if request.method == 'POST':
#         try:
#             # Запускаем задачу Celery
#             task = decrease_days.apply_async((user_id,), countdown=3)
#
#             # Сохраняем task_id в кэше или базе данных (опционально)
#             # cache.set(f"task_{user_id}", task.id, timeout=1805)  # Храним task_id на час
#
#             return JsonResponse({
#                 'message': f'Task started for user_id {user_id}',
#                 'task_id': task.id,
#                 'status': 'Task started successfully',
#             })
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def stop_task_view(request, user_id):
    if request.method == 'POST':
        try:
            # Вызываем stop_task через async_to_sync
            async_to_sync(stop_task)(user_id)
            return JsonResponse({"status": "success", "message": f"Task for user_id {user_id} stopped."}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=400)
import json
@csrf_exempt
def start_mailing_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        mailing_data = data.get('mailing_data', [])

        try:
            mailing_list.apply_async((mailing_data,),countdown=165600)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)