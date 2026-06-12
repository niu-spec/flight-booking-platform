"""目的地天气（演示数据，按城市名生成稳定模拟结果）"""

WEATHER_POOL = [
    {'condition': '晴', 'icon': '☀️', 'temp_range': (18, 28)},
    {'condition': '多云', 'icon': '⛅', 'temp_range': (15, 24)},
    {'condition': '小雨', 'icon': '🌧️', 'temp_range': (12, 20)},
    {'condition': '阴', 'icon': '☁️', 'temp_range': (14, 22)},
]


def get_weather(city):
    if not city:
        return None
    idx = sum(ord(c) for c in city) % len(WEATHER_POOL)
    pool = WEATHER_POOL[idx]
    low, high = pool['temp_range']
    offset = (sum(ord(c) for c in city) % 5) - 2
    return {
        'city': city,
        'condition': pool['condition'],
        'icon': pool['icon'],
        'temperature': high + offset,
        'low': low + offset,
        'high': high + offset,
        'humidity': 45 + (sum(ord(c) for c in city) % 40),
        'wind': f'{"东" if idx % 2 else "西"}风 {2 + idx % 4}级',
        'tip': _travel_tip(pool['condition']),
    }


def _travel_tip(condition):
    tips = {
        '晴': '天气晴好，适合出行，注意防晒。',
        '多云': '天气舒适，建议携带薄外套。',
        '小雨': '可能有雨，请携带雨具。',
        '阴': '体感偏凉，注意保暖。',
    }
    return tips.get(condition, '出行前请关注天气变化。')
