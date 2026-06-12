from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.user'
    verbose_name = '用户管理'


class FlightConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.flight'
    verbose_name = '航班管理'


class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.order'
    verbose_name = '订单管理'


class PaymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payment'
    verbose_name = '支付管理'


class ItineraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.itinerary'
    verbose_name = '行程管理'
