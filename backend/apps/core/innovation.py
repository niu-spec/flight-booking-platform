"""创新功能：碳排放估算、会员等级、智能推荐算法"""
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg
from django.utils import timezone

# 每公里人均碳排放约 0.09 kg（短途航班估算）
CO2_PER_KM = Decimal('0.09')
CITY_DISTANCE_KM = {
    ('北京', '上海'): 1100, ('上海', '北京'): 1100,
    ('北京', '广州'): 1900, ('广州', '北京'): 1900,
    ('北京', '深圳'): 1950, ('深圳', '北京'): 1950,
    ('上海', '广州'): 1300, ('广州', '上海'): 1300,
    ('广州', '成都'): 1500, ('成都', '广州'): 1500,
    ('深圳', '杭州'): 1100, ('杭州', '深圳'): 1100,
    ('杭州', '厦门'): 700, ('厦门', '杭州'): 700,
    ('上海', '西安'): 1300, ('西安', '上海'): 1300,
    ('成都', '重庆'): 300, ('重庆', '成都'): 300,
}


def estimate_distance_km(departure_city, arrival_city):
    key = (departure_city, arrival_city)
    if key in CITY_DISTANCE_KM:
        return CITY_DISTANCE_KM[key]
    return Decimal('1200')


def calc_carbon_kg(flight):
    distance = estimate_distance_km(flight.departure_city, flight.arrival_city)
    return float((distance * CO2_PER_KM).quantize(Decimal('0.1')))


def calc_member_level(points):
    if points >= 5000:
        return 'gold', '金卡会员'
    if points >= 2000:
        return 'silver', '银卡会员'
    return 'normal', '普通会员'


def points_for_order(amount):
    return int(amount)


def recommend_flights(queryset, user=None):
    flights = list(queryset)
    if not flights:
        return {}

    cheapest = min(flights, key=lambda f: float(f.base_price))
    fastest = min(
        flights,
        key=lambda f: (f.arrival_time - f.departure_time).total_seconds()
    )
    greenest = min(flights, key=lambda f: calc_carbon_kg(f))

    result = {
        'cheapest': cheapest.id,
        'fastest': fastest.id,
        'greenest': greenest.id,
        'labels': {
            str(cheapest.id): '💰 最低价',
            str(fastest.id): '⚡ 最快捷',
            str(greenest.id): '🌱 低碳推荐',
        },
    }

    if user and user.is_authenticated:
        history_cities = set()
        from apps.order.models import Order
        for o in Order.objects.filter(user=user, status='ticketed').select_related('flight')[:10]:
            history_cities.add(o.flight.arrival_city)
        for f in flights:
            if f.arrival_city in history_cities:
                result['labels'][str(f.id)] = (
                    (result['labels'].get(str(f.id), '') + ' 🔁 常飞').strip()
                )
                result['frequent'] = f.id
                break

    return result


def generate_checklist(itinerary):
    """根据行程生成出行准备清单"""
    items = [
        {'id': 1, 'text': '确认身份证件原件', 'category': '必备', 'done': False},
        {'id': 2, 'text': '提前2小时到达机场', 'category': '必备', 'done': False},
        {'id': 3, 'text': '查询航班动态与登机口', 'category': '必备', 'done': False},
        {'id': 4, 'text': '线上值机选座', 'category': '建议', 'done': False},
        {'id': 5, 'text': '准备充电宝（符合航空规定）', 'category': '建议', 'done': False},
    ]
    if itinerary.cabin_class == 'economy':
        items.append({'id': 6, 'text': '随身行李不超过5kg', 'category': '行李', 'done': False})
    else:
        items.append({'id': 6, 'text': '商务舱可携带2件行李', 'category': '行李', 'done': False})

    city = itinerary.arrival_city
    weather_tips = {
        '北京': '北方干燥，注意保湿防晒',
        '上海': '江南多雨，建议携带雨具',
        '广州': '南方湿热，穿着轻薄透气衣物',
        '成都': '盆地气候，昼夜温差较大',
        '杭州': '西湖景区步行多，穿舒适鞋子',
        '西安': '历史文化游，备一双舒适运动鞋',
    }
    tip = weather_tips.get(city, f'提前了解{city}当地天气')
    items.append({'id': 7, 'text': tip, 'category': '目的地', 'done': False})
    return items


CHAT_RULES = [
    (['退票', '退款'], '已出票订单可在「订单详情」申请退款，款项将原路返回。'),
    (['改签', '换航班'], '待支付订单支持改签，在订单详情点击「改签航班」输入新航班ID即可。'),
    (['优惠券', '优惠'], '在「优惠券」页面输入 WELCOME50 或 SAVE10 领取，预订时填入优惠码。'),
    (['积分', '会员'], '支付成功后自动获得等额积分，2000分升银卡、5000分升金卡。'),
    (['选座', '座位'], '预订时可在线选座，绿色座位为可选。'),
    (['碳', '环保', '低碳'], '每个航班展示预估碳排放量，标有🌱的为低碳推荐航班。'),
    (['超时', '取消'], '订单创建后30分钟内未支付将自动取消并释放座位。'),
    (['发票'], '出票后在订单详情点击「申请发票」即可开具电子发票。'),
    (['准备', '清单'], '在「出行助手」页面查看您的个性化出行准备清单。'),
    (['降价', '提醒'], '在航班搜索结果点击「降价提醒」订阅航线，票价下降时收到通知。'),
]


def chat_reply(message):
    msg = message.lower()
    for keywords, reply in CHAT_RULES:
        if any(k in message for k in keywords):
            return reply
    if '你好' in message or 'hi' in msg:
        return '您好！我是机票预约智能助手，可以解答退票、改签、优惠券、积分等问题。'
    return '抱歉，我暂时无法理解您的问题。您可以尝试问：如何退票？积分怎么用？如何选座？'
