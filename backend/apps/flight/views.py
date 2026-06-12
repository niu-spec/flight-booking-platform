from datetime import datetime, timedelta

from django.db.models import Avg, Min
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.core.innovation import recommend_flights
from apps.core.services import check_flight_alerts, get_seat_map
from apps.flight.models import Flight
from apps.flight.models import FlightReview
from apps.flight.transfer import search_transfer_itineraries
from apps.flight.serializers import (
    FlightSerializer,
    FlightSearchSerializer,
    FlightReviewSerializer,
    FlightReviewCreateSerializer,
)


SORT_MAP = {
    'price_asc': 'base_price',
    'price_desc': '-base_price',
    'time_asc': 'departure_time',
    'time_desc': '-departure_time',
}


def filter_flights(params):
    include_sold_out = params.get('include_sold_out') in (True, 'true', '1', 1)
    if include_sold_out:
        queryset = Flight.objects.filter(status='normal', available_seats=0)
    else:
        queryset = Flight.objects.filter(status='normal', available_seats__gt=0)
    if params.get('departure_city'):
        queryset = queryset.filter(departure_city__icontains=params['departure_city'])
    if params.get('arrival_city'):
        queryset = queryset.filter(arrival_city__icontains=params['arrival_city'])
    if params.get('departure_date'):
        date = params['departure_date']
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        queryset = queryset.filter(departure_time__date=date)
    if params.get('min_price'):
        queryset = queryset.filter(base_price__gte=params['min_price'])
    if params.get('max_price'):
        queryset = queryset.filter(base_price__lte=params['max_price'])
    if params.get('airline'):
        queryset = queryset.filter(airline__icontains=params['airline'])
    sort = params.get('sort', 'time_asc')
    queryset = queryset.order_by(SORT_MAP.get(sort, 'departure_time'))
    return queryset


class FlightListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = FlightSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        qs = self.filter_queryset(self.get_queryset())
        rec = recommend_flights(qs, self.request.user if self.request.user.is_authenticated else None)
        ctx['recommend_labels'] = rec.get('labels', {})
        return ctx
    
    def get_queryset(self):
        params = {
            'departure_city': self.request.query_params.get('departure_city'),
            'arrival_city': self.request.query_params.get('arrival_city'),
            'departure_date': self.request.query_params.get('departure_date'),
            'min_price': self.request.query_params.get('min_price'),
            'max_price': self.request.query_params.get('max_price'),
            'airline': self.request.query_params.get('airline'),
            'sort': self.request.query_params.get('sort', 'time_asc'),
            'include_sold_out': self.request.query_params.get('include_sold_out'),
        }
        if not any([params['departure_city'], params['arrival_city'], params['departure_date']]):
            queryset = Flight.objects.all()
            sort = SORT_MAP.get(params['sort'], 'departure_time')
            return queryset.order_by(sort)
        return filter_flights(params)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        qs = self.filter_queryset(self.get_queryset())
        rec = recommend_flights(qs, request.user if request.user.is_authenticated else None)
        data = response.data
        if isinstance(data, dict) and 'results' in data:
            data['recommendations'] = rec
        elif isinstance(data, list):
            response.data = {'results': data, 'recommendations': rec}
        return response


class FlightDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    lookup_field = 'id'


class FlightSearchView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = FlightSearchSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            data['sort'] = request.data.get('sort', 'time_asc')
            queryset = filter_flights(data)
            flights = FlightSerializer(queryset, many=True).data
            return Response({'count': len(flights), 'flights': flights})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlightSeatMapView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, flight_id):
        try:
            flight = Flight.objects.get(pk=flight_id)
        except Flight.DoesNotExist:
            return Response({'error': '航班不存在'}, status=404)
        return Response({'flight_id': flight.id, 'seats': get_seat_map(flight)})


class PriceCalendarView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        departure_city = request.query_params.get('departure_city')
        arrival_city = request.query_params.get('arrival_city')
        days = int(request.query_params.get('days', 7))
        if not departure_city or not arrival_city:
            return Response({'error': '请提供出发和到达城市'}, status=400)

        start = timezone.now().date()
        calendar = []
        for i in range(days):
            date = start + timedelta(days=i)
            agg = Flight.objects.filter(
                departure_city__icontains=departure_city,
                arrival_city__icontains=arrival_city,
                departure_time__date=date,
                status='normal',
                available_seats__gt=0,
            ).aggregate(min_price=Min('base_price'))
            calendar.append({
                'date': str(date),
                'min_price': str(agg['min_price']) if agg['min_price'] else None,
            })
        return Response({'calendar': calendar})


class FlightStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, flight_id):
        try:
            flight = Flight.objects.get(id=flight_id)
            new_status = request.data.get('status')
            
            if flight.update_status(new_status):
                check_flight_alerts(flight)
                return Response({
                    'message': '航班状态更新成功',
                    'flight': FlightSerializer(flight).data
                })
            return Response({'error': '无效的状态'}, status=status.HTTP_400_BAD_REQUEST)
        except Flight.DoesNotExist:
            return Response({'error': '航班不存在'}, status=status.HTTP_404_NOT_FOUND)


class FlightReviewListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, flight_id):
        reviews = FlightReview.objects.filter(flight_id=flight_id).select_related('user', 'flight')[:20]
        avg = reviews.aggregate(avg=Avg('rating'))['avg'] if reviews.exists() else None
        return Response({
            'reviews': FlightReviewSerializer(reviews, many=True).data,
            'average_rating': round(avg, 1) if avg else None,
            'count': reviews.count(),
        })


class FlightReviewCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FlightReviewCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(FlightReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class TransferSearchView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        departure_city = request.data.get('departure_city')
        arrival_city = request.data.get('arrival_city')
        departure_date = request.data.get('departure_date')
        if not all([departure_city, arrival_city, departure_date]):
            return Response({'error': '请提供出发城市、到达城市和日期'}, status=400)
        min_layover = int(request.data.get('min_layover', 60))
        itineraries = search_transfer_itineraries(
            departure_city, arrival_city, departure_date, min_layover=min_layover
        )
        return Response({'count': len(itineraries), 'itineraries': itineraries})
