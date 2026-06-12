from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.flight.models import Flight
from apps.order.models import Coupon, Order, UserCoupon
from apps.user.models import CustomUser


class OrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username='tester', phone='13900000001', password='123456'
        )
        self.client.force_authenticate(user=self.user)
        now = timezone.now()
        self.flight = Flight.objects.create(
            flight_no='TEST001',
            airline='测试航空',
            departure_city='北京',
            arrival_city='上海',
            departure_time=now,
            arrival_time=now,
            base_price=Decimal('500.00'),
            available_seats=10,
            total_seats=10,
        )
        coupon = Coupon.objects.create(
            code='TEST10',
            name='测试券',
            discount_type='fixed',
            discount_value=Decimal('10'),
            min_amount=Decimal('0'),
            valid_from=now,
            valid_until=now + timezone.timedelta(days=30),
        )
        UserCoupon.objects.create(user=self.user, coupon=coupon)

    def test_create_order(self):
        resp = self.client.post('/api/orders/create/', {
            'flight': self.flight.id,
            'cabin_class': 'economy',
            'passenger_name': '张三',
            'passenger_id_card': '110101199001011234',
            'coupon_code': 'TEST10',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Order.objects.filter(user=self.user).exists())

    def test_seat_map(self):
        resp = self.client.get(f'/api/flights/{self.flight.id}/seats/')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.json()['seats']) > 0)
