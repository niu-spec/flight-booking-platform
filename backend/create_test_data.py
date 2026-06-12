import os
import sys
import django

sys.path.insert(0, 'D:/大学/专业课/软件系统分析与设计/机票预约平台/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.flight.models import Flight
from datetime import datetime, timedelta

flights_data = [
    {
        'flight_no': 'CA1234',
        'airline': '中国国航',
        'departure_city': '北京',
        'arrival_city': '上海',
        'departure_time': datetime.now() + timedelta(days=1),
        'arrival_time': datetime.now() + timedelta(days=1, hours=2),
        'base_price': 800,
        'available_seats': 50,
        'total_seats': 50,
        'status': 'normal'
    },
    {
        'flight_no': 'MU5678',
        'airline': '东方航空',
        'departure_city': '北京',
        'arrival_city': '广州',
        'departure_time': datetime.now() + timedelta(days=2),
        'arrival_time': datetime.now() + timedelta(days=2, hours=3),
        'base_price': 1000,
        'available_seats': 30,
        'total_seats': 30,
        'status': 'normal'
    },
    {
        'flight_no': 'CZ9012',
        'airline': '南方航空',
        'departure_city': '上海',
        'arrival_city': '深圳',
        'departure_time': datetime.now() + timedelta(days=3),
        'arrival_time': datetime.now() + timedelta(days=3, hours=2),
        'base_price': 900,
        'available_seats': 40,
        'total_seats': 40,
        'status': 'normal'
    }
]

for flight_data in flights_data:
    flight, created = Flight.objects.get_or_create(
        flight_no=flight_data['flight_no'],
        defaults=flight_data
    )
    if created:
        print(f'创建航班: {flight.flight_no}')
    else:
        print(f'航班已存在: {flight.flight_no}')

print(f'总共 {Flight.objects.count()} 个航班')
