from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    用户类 - 对应详细设计报告3.2.1
    
    属性:
        phone: 手机号 (string, private)
        passwordHash继承自AbstractUser
    """
    phone = models.CharField('手机号', max_length=11, unique=True, db_index=True)
    points = models.IntegerField('积分', default=0)
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f'{self.username}({self.phone})'
    
    def register(self):
        """
        注册账号 - public方法
        实际注册逻辑在序列化器和视图中处理
        """
        self.is_active = True
        self.save()
        return self
    
    def login(self):
        """
        登录 - public方法
        登录验证逻辑在认证层处理
        """
        return {
            'user_id': self.id,
            'username': self.username,
            'phone': self.phone
        }
    
    def logout(self):
        """
        退出登录 - public方法
        实际登出逻辑在视图中处理(Token黑名单等)
        """
        return True

    def add_points(self, amount):
        from apps.core.innovation import calc_member_level
        self.points += int(amount)
        self.save(update_fields=['points'])
        level, label = calc_member_level(self.points)
        return level, label

    @property
    def member_level(self):
        from apps.core.innovation import calc_member_level
        return calc_member_level(self.points)[0]

    @property
    def member_label(self):
        from apps.core.innovation import calc_member_level
        return calc_member_level(self.points)[1]


class FrequentPassenger(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='passengers', verbose_name='用户'
    )
    name = models.CharField('姓名', max_length=50)
    id_card = models.CharField('身份证号', max_length=18)
    phone = models.CharField('手机号', max_length=11, blank=True, default='')
    is_default = models.BooleanField('默认', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        db_table = 'frequent_passengers'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f'{self.name}({self.user.username})'
