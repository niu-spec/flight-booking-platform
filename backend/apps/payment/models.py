from django.db import models
from django.utils import timezone
from apps.order.models import Order


class Payment(models.Model):
    """
    支付类 - 对应详细设计报告3.2.4
    
    属性:
        paymentId: 支付流水号 (string, private)
        amount: 支付金额 (double, private)
        status: 支付成功/失败等 (string, private)
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', '待支付'),
        ('processing', '处理中'),
        ('success', '支付成功'),
        ('failed', '支付失败'),
        ('refunded', '已退款'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('wechat', '微信支付'),
        ('alipay', '支付宝'),
        ('bank_card', '银行卡'),
    ]
    
    payment_id = models.CharField('支付流水号', max_length=50, unique=True, db_index=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name='订单')
    
    amount = models.DecimalField('支付金额', max_digits=10, decimal_places=2)
    status = models.CharField('支付状态', max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField('支付方式', max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    transaction_id = models.CharField('第三方交易号', max_length=100, blank=True, null=True)
    callback_time = models.DateTimeField('回调时间', null=True, blank=True)
    callback_data = models.JSONField('回调数据', default=dict, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = '支付'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f'支付{self.payment_id} - {self.get_status_display()}'
    
    def execute_pay(self):
        """
        发起支付 - public方法
        对应详细设计报告中的 executePay()
        实际调用第三方支付网关
        """
        if self.status == 'pending':
            self.status = 'processing'
            self.save()
            return {
                'payment_id': self.payment_id,
                'amount': str(self.amount),
                'method': self.payment_method,
                'status': 'processing'
            }
        return None
    
    def handle_callback(self, callback_data):
        """
        处理支付渠道异步回调 - public方法
        对应详细设计报告中的 handleCallback()
        """
        success = callback_data.get('success', False)
        transaction_id = callback_data.get('transaction_id')
        
        if success:
            self.status = 'success'
            self.transaction_id = transaction_id
            self.callback_time = timezone.now()
            self.callback_data = callback_data
            self.save()
            
            self.order.confirm_paid()
            self.order.issue_ticket()
            
            return True
        else:
            self.status = 'failed'
            self.callback_time = timezone.now()
            self.callback_data = callback_data
            self.save()
            return False
    
    @classmethod
    def generate_payment_id(cls):
        """
        生成支付流水号
        """
        import uuid
        return f'PAY{timezone.now().strftime("%Y%m%d%H%M%S")}{uuid.uuid4().hex[:6].upper()}'


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', '待开具'),
        ('issued', '已开具'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    title = models.CharField('发票抬头', max_length=100)
    tax_number = models.CharField('税号', max_length=30, blank=True, default='')
    amount = models.DecimalField('金额', max_digits=10, decimal_places=2)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('申请时间', auto_now_add=True)

    class Meta:
        db_table = 'invoices'
