from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.flight.models import Flight, FlightReview
from apps.order.models import Coupon, UserCoupon
from apps.user.models import CustomUser, FrequentPassenger


AIRLINES = [
    ('CA', '中国国际航空'),
    ('MU', '中国东方航空'),
    ('CZ', '中国南方航空'),
    ('HU', '海南航空'),
    ('ZH', '深圳航空'),
    ('MF', '厦门航空'),
    ('3U', '四川航空'),
    ('SC', '山东航空'),
]

# 热门航线及参考票价
ROUTES = [
    ('北京', '上海', 680, 150),
    ('上海', '北京', 720, 150),
    ('北京', '广州', 980, 180),
    ('广州', '北京', 1020, 180),
    ('北京', '深圳', 890, 170),
    ('深圳', '北京', 920, 170),
    ('北京', '成都', 1180, 200),
    ('成都', '北京', 1150, 200),
    ('上海', '广州', 520, 160),
    ('广州', '上海', 550, 160),
    ('上海', '成都', 880, 180),
    ('成都', '上海', 860, 180),
    ('上海', '西安', 620, 150),
    ('西安', '上海', 640, 150),
    ('上海', '杭州', 380, 120),
    ('杭州', '上海', 400, 120),
    ('广州', '成都', 750, 160),
    ('成都', '广州', 780, 160),
    ('深圳', '杭州', 420, 130),
    ('杭州', '深圳', 450, 130),
    ('杭州', '厦门', 380, 110),
    ('厦门', '杭州', 390, 110),
    ('成都', '重庆', 280, 100),
    ('重庆', '成都', 290, 100),
    ('北京', '西安', 720, 160),
    ('西安', '北京', 740, 160),
    ('广州', '深圳', 320, 100),
    ('深圳', '广州', 310, 100),
    ('北京', '杭州', 780, 160),
    ('杭州', '北京', 800, 160),
    ('上海', '重庆', 920, 170),
    ('重庆', '上海', 940, 170),
]


def _flight_no(prefix, seq):
    return f'{prefix}{seq:04d}'


def _build_flights(now):
    """生成未来 10 天内多班次航班"""
    flights = []
    seq = 1000

    for day in range(1, 8):
        base_day = now + timedelta(days=day)
        for dep, arr, price, duration_min in ROUTES:
            for slot, hour in enumerate([8, 14], start=1):
                prefix = AIRLINES[(seq + day + slot) % len(AIRLINES)][0]
                airline = AIRLINES[(seq + day + slot) % len(AIRLINES)][1]
                dep_time = base_day.replace(hour=hour, minute=(slot * 15) % 60, second=0, microsecond=0)
                arr_time = dep_time + timedelta(minutes=duration_min)
                price_var = price + (day % 3) * 30 + slot * 20
                seats = 80 - (seq % 40)
                flights.append({
                    'flight_no': _flight_no(prefix, seq),
                    'airline': airline,
                    'departure_city': dep,
                    'arrival_city': arr,
                    'departure_time': dep_time,
                    'arrival_time': arr_time,
                    'base_price': Decimal(str(price_var)),
                    'available_seats': max(seats, 5),
                    'total_seats': 180,
                })
                seq += 1

    # 中转联程专用：同一天衔接班次（北京→上海→成都）
    transfer_day = now + timedelta(days=2)
    transfer_legs = [
        ('CA2101', '中国国际航空', '北京', '上海', 8, 0, 150, 680),
        ('MU2102', '中国东方航空', '上海', '成都', 12, 30, 180, 820),
        ('CA2103', '中国国际航空', '北京', '上海', 9, 30, 150, 720),
        ('3U2104', '四川航空', '上海', '成都', 14, 0, 180, 850),
        ('MU2105', '中国东方航空', '北京', '广州', 7, 30, 165, 950),
        ('CZ2106', '中国南方航空', '广州', '成都', 12, 0, 150, 680),
        ('HU2107', '海南航空', '北京', '西安', 8, 30, 120, 620),
        ('SC2108', '山东航空', '西安', '成都', 11, 30, 90, 480),
    ]
    for fn, al, dep, arr, h, m, dur, price in transfer_legs:
        dep_time = transfer_day.replace(hour=h, minute=m, second=0, microsecond=0)
        flights.append({
            'flight_no': fn,
            'airline': al,
            'departure_city': dep,
            'arrival_city': arr,
            'departure_time': dep_time,
            'arrival_time': dep_time + timedelta(minutes=dur),
            'base_price': Decimal(str(price)),
            'available_seats': 35,
            'total_seats': 160,
        })

    # 售罄航班（候补购票演示）
    sold_out = [
        ('CA8801', '中国国际航空', '北京', '上海', 1, 10, 0, 150, 599),
        ('MU8802', '中国东方航空', '上海', '广州', 1, 14, 0, 165, 488),
        ('CZ8803', '中国南方航空', '广州', '深圳', 1, 16, 0, 80, 320),
        ('3U8804', '四川航空', '成都', '重庆', 3, 9, 0, 60, 268),
    ]
    for fn, al, dep, arr, d, h, m, dur, price in sold_out:
        dep_time = (now + timedelta(days=d)).replace(hour=h, minute=m, second=0, microsecond=0)
        flights.append({
            'flight_no': fn,
            'airline': al,
            'departure_city': dep,
            'arrival_city': arr,
            'departure_time': dep_time,
            'arrival_time': dep_time + timedelta(minutes=dur),
            'base_price': Decimal(str(price)),
            'available_seats': 0,
            'total_seats': 160,
        })

    # 特殊状态航班
    flights.append({
        'flight_no': 'MF2468',
        'airline': '厦门航空',
        'departure_city': '杭州',
        'arrival_city': '厦门',
        'departure_time': now + timedelta(days=5, hours=16),
        'arrival_time': now + timedelta(days=5, hours=17, minutes=20),
        'base_price': Decimal('380'),
        'available_seats': 50,
        'total_seats': 100,
        'status': 'delayed',
    })
    flights.append({
        'flight_no': 'HU5501',
        'airline': '海南航空',
        'departure_city': '深圳',
        'arrival_city': '北京',
        'departure_time': now + timedelta(days=4, hours=20),
        'arrival_time': now + timedelta(days=4, hours=23, minutes=10),
        'base_price': Decimal('920'),
        'available_seats': 22,
        'total_seats': 140,
        'status': 'normal',
    })

    return flights


class Command(BaseCommand):
    help = '导入演示用用户、航班、优惠券等数据'

    def handle(self, *args, **options):
        now = timezone.now()

        # ── 演示账号 ──
        users_data = [
            {'username': 'demo', 'phone': '13800000001', 'email': 'demo@example.com', 'is_staff': True, 'points': 1500},
            {'username': 'test', 'phone': '13800000002', 'email': 'test@example.com', 'is_staff': False, 'points': 800},
            {'username': 'alice', 'phone': '13800000003', 'email': 'alice@example.com', 'is_staff': False, 'points': 3200},
        ]
        demo_user = None
        for u in users_data:
            user, created = CustomUser.objects.get_or_create(
                username=u['username'],
                defaults={'phone': u['phone'], 'email': u['email'], 'is_staff': u['is_staff'], 'points': u['points']},
            )
            user.is_staff = u['is_staff']
            user.points = u['points']
            user.set_password('123456')
            user.save()
            if u['username'] == 'demo':
                demo_user = user
            action = '创建' if created else '更新'
            self.stdout.write(f'  {action}用户 {u["username"]} / 123456')

        # ── 常用乘机人 ──
        passengers_data = [
            {'name': '张三', 'id_card': '110101199001011234', 'phone': '13811112222', 'is_default': True},
            {'name': '李四', 'id_card': '310101199205051234', 'phone': '13833334444', 'is_default': False},
            {'name': '王五', 'id_card': '440101198808081234', 'phone': '13855556666', 'is_default': False},
        ]
        for p in passengers_data:
            FrequentPassenger.objects.update_or_create(
                user=demo_user,
                id_card=p['id_card'],
                defaults={**p},
            )
        self.stdout.write(self.style.SUCCESS(f'  常用乘机人 {len(passengers_data)} 条'))

        # ── 航班 ──
        flights_data = _build_flights(now)
        created_count = 0
        updated_count = 0
        for data in flights_data:
            status = data.pop('status', 'normal')
            flight, created = Flight.objects.update_or_create(
                flight_no=data['flight_no'],
                defaults={**data, 'status': status},
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        total = Flight.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'  航班：新增 {created_count}，更新 {updated_count}，库中共 {total} 条'
            )
        )

        # ── 优惠券 ──
        coupons = [
            {'code': 'WELCOME50', 'name': '新用户立减50', 'discount_type': 'fixed', 'discount_value': 50, 'min_amount': 300},
            {'code': 'SAVE10', 'name': '全场9折', 'discount_type': 'percent', 'discount_value': 10, 'min_amount': 500},
            {'code': 'SPRING100', 'name': '春季满减100', 'discount_type': 'fixed', 'discount_value': 100, 'min_amount': 800},
            {'code': 'VIP20', 'name': 'VIP专享8折', 'discount_type': 'percent', 'discount_value': 20, 'min_amount': 1000},
            {'code': 'FLASH30', 'name': '限时立减30', 'discount_type': 'fixed', 'discount_value': 30, 'min_amount': 200},
        ]
        for c in coupons:
            coupon, _ = Coupon.objects.update_or_create(
                code=c['code'],
                defaults={
                    **c,
                    'valid_from': now - timedelta(days=1),
                    'valid_until': now + timedelta(days=365),
                    'is_active': True,
                    'total_quota': 5000,
                },
            )
            UserCoupon.objects.get_or_create(user=demo_user, coupon=coupon)
            UserCoupon.objects.get_or_create(
                user=CustomUser.objects.get(username='test'), coupon=coupon
            )
        self.stdout.write(self.style.SUCCESS(f'  优惠券 {len(coupons)} 张（demo/test 已领取）'))

        # ── 示例航班评价 ──
        sample_flight = Flight.objects.filter(flight_no='CA2101').first()
        if sample_flight and not FlightReview.objects.filter(flight=sample_flight, user=demo_user).exists():
            FlightReview.objects.create(
                user=demo_user,
                flight=sample_flight,
                rating=5,
                content='准点起飞，服务很好，餐食也不错！',
            )
        alice = CustomUser.objects.filter(username='alice').first()
        if sample_flight and alice and not FlightReview.objects.filter(flight=sample_flight, user=alice).exists():
            FlightReview.objects.create(
                user=alice,
                flight=sample_flight,
                rating=4,
                content='整体满意，登机流程顺畅。',
            )
        review_count = FlightReview.objects.count()
        self.stdout.write(self.style.SUCCESS(f'  航班评价 {review_count} 条'))

        self.stdout.write(self.style.SUCCESS('\n演示数据导入完成！'))
        self.stdout.write('  账号: demo / test / alice  密码均为 123456')
        self.stdout.write('  优惠券: WELCOME50  SAVE10  SPRING100  VIP20  FLASH30')
