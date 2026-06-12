from django.db import models
from django.utils import timezone


class Notification(models.Model):
    TYPE_CHOICES = [
        ('order', '订单'),
        ('payment', '支付'),
        ('flight', '航班'),
        ('refund', '退款'),
        ('system', '系统'),
    ]

    user = models.ForeignKey(
        'user.CustomUser', on_delete=models.CASCADE, related_name='notifications'
    )
    title = models.CharField('标题', max_length=100)
    content = models.TextField('内容')
    notification_type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='system')
    is_read = models.BooleanField('已读', default=False)
    related_id = models.CharField('关联ID', max_length=50, blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']


class FlightAlert(models.Model):
    user = models.ForeignKey(
        'user.CustomUser', on_delete=models.CASCADE, related_name='flight_alerts'
    )
    flight = models.ForeignKey(
        'flight.Flight', on_delete=models.CASCADE, related_name='alerts'
    )
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'flight_alerts'
        unique_together = ['user', 'flight']


class PriceWatch(models.Model):
    """降价提醒：订阅航线的目标价格"""
    user = models.ForeignKey(
        'user.CustomUser', on_delete=models.CASCADE, related_name='price_watches'
    )
    departure_city = models.CharField('出发城市', max_length=50)
    arrival_city = models.CharField('到达城市', max_length=50)
    target_price = models.DecimalField('目标价格', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'price_watches'


class WaitlistEntry(models.Model):
    """候补购票"""
    STATUS_CHOICES = [
        ('waiting', '候补中'),
        ('fulfilled', '已兑现'),
        ('cancelled', '已取消'),
    ]

    user = models.ForeignKey(
        'user.CustomUser', on_delete=models.CASCADE, related_name='waitlist_entries'
    )
    flight = models.ForeignKey(
        'flight.Flight', on_delete=models.CASCADE, related_name='waitlist_entries'
    )
    passenger_name = models.CharField('乘客姓名', max_length=50)
    passenger_id_card = models.CharField('乘客身份证号', max_length=18)
    cabin_class = models.CharField('舱位', max_length=20, default='economy')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='waiting')
    order = models.ForeignKey(
        'order.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='waitlist_entry'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'waitlist_entries'
        ordering = ['created_at']

    @property
    def position(self):
        if self.status != 'waiting':
            return None
        return WaitlistEntry.objects.filter(
            flight=self.flight, status='waiting', created_at__lte=self.created_at
        ).count()


class TravelChecklist(models.Model):
    """出行准备清单"""
    user = models.ForeignKey(
        'user.CustomUser', on_delete=models.CASCADE, related_name='checklists'
    )
    itinerary = models.ForeignKey(
        'itinerary.Itinerary', on_delete=models.CASCADE, related_name='checklists'
    )
    items = models.JSONField('清单项', default=list)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'travel_checklists'
        unique_together = ['user', 'itinerary']
