from django.db import models
from django.utils import timezone
from apps.user.models import CustomUser
from apps.order.models import Order


class Itinerary(models.Model):
    """
    行程类 - 对应详细设计报告3.2.5
    
    属性:
        itineraryId: 行程记录标识 (string, private)
        flightNo: 展示用航班号 (string, private)
        departureTime: 出发时间 (DateTime, private)
    """
    ITINERARY_STATUS_CHOICES = [
        ('upcoming', '即将出行'),
        ('in_progress', '行程中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    itinerary_id = models.CharField('行程ID', max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='itineraries', verbose_name='用户')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='itineraries', verbose_name='订单')
    
    flight_no = models.CharField('航班号', max_length=20)
    airline = models.CharField('航空公司', max_length=50)
    departure_city = models.CharField('出发城市', max_length=50)
    arrival_city = models.CharField('到达城市', max_length=50)
    departure_time = models.DateTimeField('出发时间')
    arrival_time = models.DateTimeField('到达时间')
    cabin_class = models.CharField('舱位等级', max_length=20)
    seat_number = models.CharField('座位号', max_length=10, blank=True, null=True)
    
    status = models.CharField('行程状态', max_length=20, choices=ITINERARY_STATUS_CHOICES, default='upcoming')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'itineraries'
        verbose_name = '行程'
        verbose_name_plural = verbose_name
        ordering = ['-departure_time']
    
    def __str__(self):
        return f'行程{self.itinerary_id} - {self.flight_no}'
    
    def sync_from_order(self):
        """
        根据订单/出票结果同步行程 - public方法
        对应详细设计报告中的 syncFromOrder()
        """
        order = self.order
        flight = order.flight
        
        self.flight_no = flight.flight_no
        self.airline = flight.airline
        self.departure_city = flight.departure_city
        self.arrival_city = flight.arrival_city
        self.departure_time = flight.departure_time
        self.arrival_time = flight.arrival_time
        self.cabin_class = order.cabin_class
        self.seat_number = order.seat_number
        self.save()
        
        return self
    
    def refresh_status(self):
        """
        刷新航班动态信息 - public方法
        对应详细设计报告中的 refreshStatus()
        """
        flight = self.order.flight
        
        if flight.status == 'cancelled':
            self.status = 'cancelled'
        elif flight.status in ['departed', 'landed']:
            self.status = 'completed'
        elif timezone.now() > self.departure_time:
            self.status = 'in_progress'
        else:
            self.status = 'upcoming'
        
        self.save()
        return self
    
    @classmethod
    def create_from_order(cls, order):
        """
        从订单创建行程
        """
        existing = cls.objects.filter(order=order).first()
        if existing:
            return existing

        import uuid
        itinerary_id = f'ITI{timezone.now().strftime("%Y%m%d")}{uuid.uuid4().hex[:8].upper()}'
        
        itinerary = cls.objects.create(
            itinerary_id=itinerary_id,
            user=order.user,
            order=order,
            flight_no=order.flight.flight_no,
            airline=order.flight.airline,
            departure_city=order.flight.departure_city,
            arrival_city=order.flight.arrival_city,
            departure_time=order.flight.departure_time,
            arrival_time=order.flight.arrival_time,
            cabin_class=order.cabin_class,
            seat_number=order.seat_number
        )
        
        return itinerary
