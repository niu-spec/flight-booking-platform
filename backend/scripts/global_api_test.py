"""全局 API 集成测试脚本"""
import json
import sys
import uuid
import urllib.error
import urllib.request

BASE = 'http://127.0.0.1:8000/api'
PASS = 0
FAIL = 0
BUGS = []


def req(method, path, data=None, token=None, expect=None):
    global PASS, FAIL
    url = f'{BASE}{path}'
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Token {token}'
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as resp:
            status = resp.status
            raw = resp.read().decode()
            payload = json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        status = e.code
        raw = e.read().decode()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = raw
    name = f'{method} {path}'
    if expect is not None and status != expect:
        FAIL += 1
        BUGS.append(f'[{name}] 期望 HTTP {expect}，实际 {status}，响应: {payload}')
        return status, payload
    PASS += 1
    return status, payload


def check(name, condition, detail=''):
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        BUGS.append(f'[{name}] {detail}')


def main():
    suffix = uuid.uuid4().hex[:8]
    username = f'test_{suffix}'
    phone = f'138{suffix[:8]}'
    password = '123456'

    print('=== 1. 用户注册 ===')
    status, reg = req('POST', '/auth/register/', {
        'username': username,
        'phone': phone,
        'password': password,
        'password_confirm': password,
        'email': f'{username}@test.com',
    }, expect=201)
    token = reg.get('token')
    check('注册返回 token', bool(token), reg)

    print('=== 2. 用户登录 ===')
    status, login = req('POST', '/auth/login/', {
        'username': username,
        'password': password,
    }, expect=200)
    token = login.get('token') or token

    print('=== 3. 用户信息 ===')
    status, profile = req('GET', '/auth/profile/', token=token, expect=200)
    check('profile 用户名', profile.get('username') == username, profile)

    print('=== 4. 航班列表 ===')
    status, flights_resp = req('GET', '/flights/', expect=200)
    flights = flights_resp.get('results', flights_resp)
    check('航班列表非空', len(flights) > 0, flights_resp)
    flight = flights[0]
    check('航班含 is_available', 'is_available' in flight, flight)

    print('=== 5. 航班搜索 ===')
    status, search = req('POST', '/flights/search/', {
        'departure_city': flight['departure_city'],
    }, expect=200)
    check('搜索返回 flights', 'flights' in search and len(search['flights']) > 0, search)

    print('=== 6. 航班详情 ===')
    status, detail = req('GET', f'/flights/{flight["id"]}/', expect=200)
    check('详情航班号', detail.get('flight_no') == flight['flight_no'], detail)

    print('=== 7. 创建订单 ===')
    status, order_create = req('POST', '/orders/create/', {
        'flight': flight['id'],
        'cabin_class': 'economy',
        'passenger_name': '测试乘客',
        'passenger_id_card': '110101199001011234',
    }, token=token, expect=201)
    check('创建订单返回 id', 'id' in order_create, order_create)
    check('创建订单返回 order_id', 'order_id' in order_create, order_create)
    order_id = order_create.get('id')

    print('=== 8. 订单列表 ===')
    status, orders_resp = req('GET', '/orders/', token=token, expect=200)
    orders = orders_resp.get('results', orders_resp)
    check('订单列表有数据', isinstance(orders, list) and len(orders) > 0, orders_resp)
    if not isinstance(orders, list) or not orders:
        print('\n无法继续：订单列表为空')
        return 1
    first_order = orders[0]
    check('订单列表含 flight 对象',
          isinstance(first_order.get('flight'), dict) and first_order['flight'].get('flight_no'),
          first_order)

    print('=== 9. 订单详情 ===')
    status, order_detail = req('GET', f'/orders/{order_id}/', token=token, expect=200)
    check('订单详情含 order_id', bool(order_detail.get('order_id')), order_detail)
    check('订单详情含 flight 信息',
          isinstance(order_detail.get('flight'), dict) and order_detail['flight'].get('flight_no'),
          order_detail)

    print('=== 10. 发起支付（DEBUG 模式自动出票）===')
    status, pay_create = req('POST', f'/payments/create/{order_id}/', {
        'payment_method': 'wechat',
    }, token=token, expect=201)
    payment = pay_create.get('payment', {})
    payment_id = payment.get('payment_id')
    check('支付返回 payment_id', bool(payment_id), pay_create)
    check('DEBUG 自动支付成功', payment.get('status') == 'success', payment)

    print('=== 11. 支付后订单状态 ===')
    status, order_after_pay = req('GET', f'/orders/{order_id}/', token=token, expect=200)
    check('支付后订单已出票', order_after_pay.get('status') == 'ticketed', order_after_pay)

    print('=== 12. 行程列表 ===')
    status, itin_resp = req('GET', '/itineraries/', token=token, expect=200)
    itineraries = itin_resp.get('results', itin_resp)
    check('支付后有行程', len(itineraries) > 0, itin_resp)
    itinerary_id = itineraries[0]['id'] if itineraries else None

    if itinerary_id:
        print('=== 13. 刷新行程 ===')
        status, refresh = req('POST', f'/itineraries/{itinerary_id}/refresh/', token=token, expect=200)
        check('刷新行程成功', 'itinerary' in refresh, refresh)

    print('=== 14. 重复支付（应失败）===')
    status, dup_pay = req('POST', f'/payments/create/{order_id}/', {
        'payment_method': 'alipay',
    }, token=token, expect=404)

    print('=== 15. 创建待取消订单 ===')
    status, cancel_order = req('POST', '/orders/create/', {
        'flight': flight['id'],
        'cabin_class': 'economy',
        'passenger_name': '取消测试',
        'passenger_id_card': '110101199001011235',
    }, token=token, expect=201)
    cancel_id = cancel_order.get('id')

    print('=== 16. 取消订单 ===')
    status, cancel_resp = req('POST', f'/orders/{cancel_id}/cancel/', token=token, expect=200)
    check('取消订单成功', '成功' in cancel_resp.get('message', ''), cancel_resp)

    print('=== 17. 退出登录 ===')
    status, logout = req('POST', '/auth/logout/', token=token, expect=200)

    print('\n' + '=' * 50)
    print(f'通过: {PASS}  失败: {FAIL}')
    if BUGS:
        print('\n发现的问题:')
        for i, bug in enumerate(BUGS, 1):
            print(f'  {i}. {bug}')
        return 1
    print('\n全部测试通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())
