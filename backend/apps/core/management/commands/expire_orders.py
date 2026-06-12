from django.core.management.base import BaseCommand

from apps.core.services import expire_pending_orders


class Command(BaseCommand):
    help = '取消超时未支付订单'

    def handle(self, *args, **options):
        count = expire_pending_orders()
        self.stdout.write(self.style.SUCCESS(f'已取消 {count} 笔超时订单'))
