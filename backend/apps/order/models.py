from datetime import timedelta

from django.db import models
from django.utils import timezone
from apps.user.models import CustomUser
from apps.flight.models import Flight


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('fixed', '固定金额'),
        ('percent', '百分比'),
    ]

    code = models.CharField('优惠码', max_length=30, unique=True)
    name = models.CharField('名称', max_length=50)
    discount_type = models.CharField('类型', max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField('优惠值', max_digits=10, decimal_places=2)
    min_amount = models.DecimalField('最低消费', max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField('生效时间')
    valid_until = models.DateTimeField('失效时间')
    total_quota = models.IntegerField('总配额', default=1000)
    used_count = models.IntegerField('已使用', default=0)
    is_active = models.BooleanField('启用', default=True)

    class Meta:
        db_table = 'coupons'

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active
            and self.valid_from <= now <= self.valid_until
            and self.used_count < self.total_quota
        )

    def calc_discount(self, amount):
        from decimal import Decimal
        if not self.is_valid() or amount < self.min_amount:
            return Decimal('0')
        if self.discount_type == 'fixed':
            return min(self.discount_value, amount)
        return (amount * self.discount_value / Decimal('100')).quantize(Decimal('0.01'))


class UserCoupon(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='user_coupons')
    is_used = models.BooleanField('已使用', default=False)
    used_at = models.DateTimeField('使用时间', null=True, blank=True)
    claimed_at = models.DateTimeField('领取时间', auto_now_add=True)

    class Meta:
        db_table = 'user_coupons'
        unique_together = ['user', 'coupon']


class BookingGroup(models.Model):
    TRIP_TYPE_CHOICES = [
        ('one_way', '单程'),
        ('round_trip', '往返'),
        ('transfer', '中转'),
        ('multi_city', '多程'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='booking_groups')
    trip_type = models.CharField('行程类型', max_length=20, choices=TRIP_TYPE_CHOICES, default='one_way')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'booking_groups'


class Order(models.Model):
    """
    订单类 - 对应详细设计报告3.2.3
    
    属性:
        orderId: 订单号 (string, private)
        totalAmount: 订单总金额 (double, private)
        status: 待支付/已支付/已出票/已取消等 (string, private)
    """
    ORDER_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('ticketed', '已出票'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]
    
    CABIN_CLASS_CHOICES = [
        ('economy', '经济舱'),
        ('business', '商务舱'),
        ('first', '头等舱'),
    ]
    
    order_id = models.CharField('订单号', max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders', verbose_name='用户')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='orders', verbose_name='航班')
    
    cabin_class = models.CharField('舱位等级', max_length=20, choices=CABIN_CLASS_CHOICES, default='economy')
    seat_number = models.CharField('座位号', max_length=10, blank=True, null=True)
    passenger_name = models.CharField('乘客姓名', max_length=50)
    passenger_id_card = models.CharField('乘客身份证号', max_length=18)
    
    total_amount = models.DecimalField('订单总金额', max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField('优惠金额', max_digits=10, decimal_places=2, default=0)
    insurance_amount = models.DecimalField('延误险金额', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('订单状态', max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    booking_group = models.ForeignKey(
        BookingGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders'
    )
    trip_leg = models.CharField('航段', max_length=20, default='outbound')
    expires_at = models.DateTimeField('支付截止时间', null=True, blank=True)

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    paid_at = models.DateTimeField('支付时间', null=True, blank=True)
    ticketed_at = models.DateTimeField('出票时间', null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f'订单{self.order_id} - {self.get_status_display()}'
    
    def create(self):
        """
        创建订单 - public方法
        对应详细设计报告中的 create()
        """
        if self.flight.is_available:
            if self.flight.book_seats(1):
                self.status = 'pending'
                self.save()
                return True
        return False
    
    def is_expired(self):
        return self.status == 'pending' and self.expires_at and timezone.now() > self.expires_at

    def cancel(self):
        """
        取消订单 - public方法
        对应详细设计报告中的 cancel()
        """
        if self.status in ['pending', 'paid']:
            self.flight.release_seats(1)
            self.status = 'cancelled'
            self.save()
            if self.seat_number:
                from apps.core.services import release_seat_lock
                release_seat_lock(self.flight_id, self.seat_number)
            self._try_fulfill_waitlist()
            return True
        return False

    def refund(self, amount=None):
        if self.status in ['paid', 'ticketed']:
            self.flight.release_seats(1)
            self.status = 'refunded'
            self.save()
            if self.seat_number:
                from apps.core.services import release_seat_lock
                release_seat_lock(self.flight_id, self.seat_number)
            self._try_fulfill_waitlist()
            return True
        return False

    def _try_fulfill_waitlist(self):
        from apps.core.services import try_fulfill_waitlist
        flight = Flight.objects.get(pk=self.flight_id)
        try_fulfill_waitlist(flight)

    def set_expiry(self, minutes=30):
        self.expires_at = timezone.now() + timedelta(minutes=minutes)
    
    def confirm_paid(self):
        """
        支付成功后更新订单状态 - public方法
        对应详细设计报告中的 confirmPaid()
        """
        if self.status == 'pending':
            self.status = 'paid'
            self.paid_at = timezone.now()
            self.save()
            return True
        return False
    
    def issue_ticket(self):
        """
        出票
        """
        if self.status == 'paid':
            self.status = 'ticketed'
            self.ticketed_at = timezone.now()
            self.save()
            return True
        return False
    
    @classmethod
    def generate_order_id(cls):
        """
        生成订单号
        """
        import uuid
        return f'ORD{timezone.now().strftime("%Y%m%d")}{uuid.uuid4().hex[:8].upper()}'


class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refund_requests')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='refund_requests')
    reason = models.TextField('退款原因')
    amount = models.DecimalField('退款金额', max_digits=10, decimal_places=2)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('申请时间', auto_now_add=True)
    processed_at = models.DateTimeField('处理时间', null=True, blank=True)

    class Meta:
        db_table = 'refund_requests'
        ordering = ['-created_at']
