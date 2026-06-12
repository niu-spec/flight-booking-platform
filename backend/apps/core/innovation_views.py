from decimal import Decimal

from django.db.models import Min
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.innovation import generate_checklist
from apps.core.llm_chat import get_chat_reply
from apps.core.models import PriceWatch, TravelChecklist
from apps.core.serializers import PriceWatchSerializer, TravelChecklistSerializer
from apps.flight.models import Flight
from apps.flight.serializers import FlightSerializer
from apps.itinerary.models import Itinerary


class ChatAssistantView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = request.data.get('message', '')
        history = request.data.get('history', [])
        if not message.strip():
            return Response({'error': '请输入问题'}, status=400)
        user = request.user if request.user.is_authenticated else None
        reply, mode = get_chat_reply(message, history=history, user=user)
        return Response({'reply': reply, 'mode': mode})


class PriceWatchListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PriceWatchSerializer

    def get_queryset(self):
        return PriceWatch.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PriceWatchDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, watch_id):
        deleted, _ = PriceWatch.objects.filter(id=watch_id, user=request.user).delete()
        if deleted:
            return Response({'message': '已取消降价提醒'})
        return Response({'error': '记录不存在'}, status=404)


class FlightCompareView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ids = request.data.get('flight_ids', [])
        if not ids or len(ids) > 3:
            return Response({'error': '请选择1-3个航班对比'}, status=400)
        flights = Flight.objects.filter(id__in=ids)
        return Response({
            'flights': FlightSerializer(flights, many=True).data,
        })


class TravelChecklistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, itinerary_id=None):
        if itinerary_id:
            try:
                itinerary = Itinerary.objects.get(id=itinerary_id, user=request.user)
            except Itinerary.DoesNotExist:
                return Response({'error': '行程不存在'}, status=404)
            checklist, _ = TravelChecklist.objects.get_or_create(
                user=request.user,
                itinerary=itinerary,
                defaults={'items': generate_checklist(itinerary)},
            )
            return Response(TravelChecklistSerializer(checklist).data)

        checklists = TravelChecklist.objects.filter(user=request.user)
        return Response(TravelChecklistSerializer(checklists, many=True).data)

    def patch(self, request, itinerary_id):
        try:
            checklist = TravelChecklist.objects.get(
                itinerary_id=itinerary_id, user=request.user
            )
        except TravelChecklist.DoesNotExist:
            return Response({'error': '清单不存在'}, status=404)
        items = request.data.get('items')
        if items is not None:
            checklist.items = items
            checklist.save(update_fields=['items'])
        return Response(TravelChecklistSerializer(checklist).data)


class CheckPriceWatchesView(APIView):
    """检查降价提醒并发送通知（管理/定时调用）"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.core.services import create_notification
        triggered = 0
        for watch in PriceWatch.objects.filter(user=request.user, is_active=True):
            agg = Flight.objects.filter(
                departure_city__icontains=watch.departure_city,
                arrival_city__icontains=watch.arrival_city,
                status='normal',
                available_seats__gt=0,
            ).aggregate(min_price=Min('base_price'))
            min_price = agg['min_price']
            if min_price and min_price <= watch.target_price:
                create_notification(
                    request.user,
                    '降价提醒 🔔',
                    f'{watch.departure_city}→{watch.arrival_city} 航线最低价已降至 ¥{min_price}，低于您的目标价 ¥{watch.target_price}！',
                    'flight',
                    f'{watch.departure_city}-{watch.arrival_city}',
                )
                triggered += 1
        return Response({'message': f'已检查，触发 {triggered} 条提醒'})


class WeatherView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.core.weather import get_weather
        city = request.query_params.get('city', '')
        if not city:
            return Response({'error': '请提供 city 参数'}, status=400)
        return Response(get_weather(city))
