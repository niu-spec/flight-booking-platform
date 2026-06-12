from django.db import models
from django.utils import timezone


class Flight(models.Model):
    """
    航班类 - 对应详细设计报告3.2.2
    
    属性:
        flightNo: 航班号 (string, private)
        departureTime: 计划起飞时间 (DateTime, private)
        basePrice: 基准票价 (double, private)
        availableSeats: 剩余可售座位数 (int, private)
    """
    FLIGHT_STATUS_CHOICES = [
        ('normal', '正常'),
        ('delayed', '延误'),
        ('cancelled', '取消'),
        ('departed', '已起飞'),
        ('landed', '已降落'),
    ]
    
    flight_no = models.CharField('航班号', max_length=20, unique=True, db_index=True)
    airline = models.CharField('航空公司', max_length=50)
    departure_city = models.CharField('出发城市', max_length=50)
    arrival_city = models.CharField('到达城市', max_length=50)
    departure_time = models.DateTimeField('计划起飞时间')
    arrival_time = models.DateTimeField('计划到达时间')
    base_price = models.DecimalField('基准票价', max_digits=10, decimal_places=2)
    available_seats = models.IntegerField('剩余可售座位数', default=0)
    total_seats = models.IntegerField('总座位数', default=0)
    status = models.CharField('航班状态', max_length=20, choices=FLIGHT_STATUS_CHOICES, default='normal')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'flights'
        verbose_name = '航班'
        verbose_name_plural = verbose_name
        ordering = ['departure_time']
    
    def __str__(self):
        return f'{self.flight_no} {self.departure_city}->{self.arrival_city}'
    
    def get_available_seats(self):
        """
        查询剩余座位 - public方法
        对应详细设计报告中的 getAvailableSeats()
        """
        return self.available_seats
    
    @property
    def is_available(self):
        return self.status == 'normal' and self.available_seats > 0

    def update_status(self, new_status):
        valid = {c[0] for c in self.FLIGHT_STATUS_CHOICES}
        if new_status not in valid:
            return False
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])
        return True

    def book_seats(self, count=1):
        """
        预订座位 - public方法
        对应详细设计报告中的 bookSeats()
        """
        if self.available_seats >= count:
            self.available_seats -= count
            self.save(update_fields=['available_seats'])
            return True
        return False
    
    def release_seats(self, count=1):
        """释放座位"""
        self.available_seats = min(self.available_seats + count, self.total_seats)
        self.save(update_fields=['available_seats'])


class FlightReview(models.Model):
    """航班评价"""
    user = models.ForeignKey(
        'user.CustomUser', on_delete=models.CASCADE, related_name='flight_reviews'
    )
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(
        'order.Order', on_delete=models.CASCADE, related_name='review', null=True, blank=True
    )
    rating = models.IntegerField('评分', default=5)
    content = models.TextField('评价内容', blank=True, default='')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'flight_reviews'
        ordering = ['-created_at']
        unique_together = ['user', 'order']

    def __str__(self):
        return f'{self.user.username} 评价 {self.flight.flight_no}'
