from datetime import datetime, timedelta

from apps.flight.models import Flight
from apps.flight.serializers import FlightSerializer

HUB_CITIES = ['上海', '广州', '成都', '西安', '杭州', '深圳', '重庆']


def _parse_date(departure_date):
    if isinstance(departure_date, str):
        return datetime.strptime(departure_date, '%Y-%m-%d').date()
    return departure_date


def search_transfer_itineraries(departure_city, arrival_city, departure_date, min_layover=60, max_results=20):
    """搜索一次中转联程方案"""
    date = _parse_date(departure_date)
    min_layover_delta = timedelta(minutes=min_layover)
    itineraries = []

    leg1_base = Flight.objects.filter(
        departure_city__icontains=departure_city,
        departure_time__date=date,
        status='normal',
        available_seats__gt=0,
    )

    for hub in HUB_CITIES:
        if hub in (departure_city or '') or hub in (arrival_city or ''):
            continue
        for leg1 in leg1_base.filter(arrival_city__icontains=hub).order_by('departure_time')[:8]:
            min_depart = leg1.arrival_time + min_layover_delta
            leg2_qs = Flight.objects.filter(
                departure_city__icontains=hub,
                arrival_city__icontains=arrival_city,
                departure_time__gte=min_depart,
                departure_time__date=date,
                status='normal',
                available_seats__gt=0,
            ).order_by('departure_time')[:5]
            for leg2 in leg2_qs:
                layover_minutes = int((leg2.departure_time - leg1.arrival_time).total_seconds() / 60)
                total_price = leg1.base_price + leg2.base_price
                total_duration = int((leg2.arrival_time - leg1.departure_time).total_seconds() / 60)
                itineraries.append({
                    'hub_city': hub,
                    'layover_minutes': layover_minutes,
                    'total_price': str(total_price),
                    'total_duration_minutes': total_duration,
                    'legs': [
                        FlightSerializer(leg1).data,
                        FlightSerializer(leg2).data,
                    ],
                })

    itineraries.sort(key=lambda x: (float(x['total_price']), x['total_duration_minutes']))
    return itineraries[:max_results]
