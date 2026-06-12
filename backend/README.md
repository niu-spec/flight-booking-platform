# Django项目配置说明

## 环境要求
- Python 3.9+
- Django 4.2.7
- djangorestframework 3.14.1

## 安装步骤

1. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 数据库迁移
```bash
python manage.py makemigrations user flight order payment itinerary
python manage.py migrate
```

4. 创建超级用户
```bash
python manage.py createsuperuser
```

5. 运行开发服务器
```bash
python manage.py runserver
```

## API接口说明

### 用户认证
- POST /api/auth/register/ - 用户注册
- POST /api/auth/login/ - 用户登录
- POST /api/auth/logout/ - 用户登出
- GET /api/auth/profile/ - 获取用户信息

### 航班管理
- GET /api/flights/ - 获取航班列表
- GET /api/flights/{id}/ - 获取航班详情
- POST /api/flights/search/ - 搜索航班
- POST /api/flights/{id}/update-status/ - 更新航班状态

### 订单管理
- GET /api/orders/ - 获取订单列表
- POST /api/orders/create/ - 创建订单
- GET /api/orders/{id}/ - 获取订单详情
- POST /api/orders/{id}/cancel/ - 取消订单

### 支付管理
- POST /api/payments/create/{order_id}/ - 创建支付
- GET /api/payments/{id}/ - 获取支付详情
- POST /api/payments/callback/{payment_id}/ - 支付回调

### 行程管理
- GET /api/itineraries/ - 获取行程列表
- GET /api/itineraries/{id}/ - 获取行程详情
- POST /api/itineraries/{id}/refresh/ - 刷新行程状态
