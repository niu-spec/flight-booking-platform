# 机票预约平台

软件系统分析与设计课程项目 —— 基于 **Django + Vue 3** 的全栈机票预订系统，支持航班搜索、在线预订、支付出票、行程管理等完整业务流程。

## 功能概览

| 模块 | 功能 |
|------|------|
| 航班搜索 | 单程 / 往返 / 中转 / 多程、价格日历、筛选排序、语音搜索 |
| 预订下单 | 选座、优惠券、延误险、往返/联程一键预订 |
| 候补购票 | 售罄航班排队，释放座位后自动兑现订单 |
| 订单支付 | 微信/支付宝模拟支付，30 分钟超时自动取消 |
| 电子客票 | 二维码登机牌、行程分享、目的地天气 |
| 个人中心 | 常用乘机人、消息中心、积分会员、航班评价 |
| 创新功能 | 碳排放估算、智能推荐、降价提醒、AI 出行助手 |
| 管理后台 | 订单统计、航班状态管理（`/admin`） |

## 技术栈

**后端**
- Python 3.9+ · Django 4.2 · Django REST Framework
- JWT + Token 双认证 · SQLite
- OpenAI 兼容大模型接口（DeepSeek 等，可选）

**前端**
- Vue 3 · Vue Router · Pinia · Element Plus · Vite
- Axios · QRCode · SVG 航线地图

**部署**
- Docker Compose 一键启动

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- npm 或 pnpm

### 1. 克隆项目

```bash
git clone https://github.com/niu-spec/flight-booking-platform.git
cd flight-booking-platform
```

### 2. 后端

```bash
cd backend
pip install -r requirements.txt
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver 0.0.0.0:8000
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：**http://localhost:8080**

### 4. Docker（可选）

```bash
docker-compose up --build
```

## 演示账号

| 用户名 | 密码 | 说明 |
|--------|------|------|
| `demo` | `123456` | 管理员，可访问 `/admin` 看板 |
| `test` | `123456` | 普通用户 |
| `alice` | `123456` | 普通用户（3200 积分，银卡） |

**演示优惠券：** `WELCOME50` · `SAVE10` · `SPRING100` · `VIP20` · `FLASH30`

## 局域网 / 手机访问

后端需监听所有网卡：

```bash
python manage.py runserver 0.0.0.0:8000
```

前端 `vite.config.js` 已配置 `host: 0.0.0.0`，手机与电脑同一 WiFi 下访问 `http://<电脑IP>:8080` 即可。

## 项目结构

```
机票预约平台/
├── backend/                 # Django 后端
│   ├── apps/
│   │   ├── user/            # 用户、乘机人
│   │   ├── flight/          # 航班、评价、中转搜索
│   │   ├── order/           # 订单、优惠券、退款改签
│   │   ├── payment/         # 支付、发票
│   │   ├── itinerary/       # 行程
│   │   └── core/            # 通知、候补、AI 助手、天气
│   ├── config/              # Django 配置
│   └── manage.py
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── views/           # 页面
│       ├── components/      # 组件
│       └── api/             # 接口封装
├── docs/                    # 需求/设计文档、用例图
└── docker-compose.yml
```

## 主要 API

| 路径 | 说明 |
|------|------|
| `POST /api/auth/login/` | 登录 |
| `GET /api/flights/` | 航班搜索 |
| `POST /api/flights/search-transfer/` | 中转联程搜索 |
| `POST /api/orders/create/` | 创建订单 |
| `POST /api/orders/create-roundtrip/` | 往返预订 |
| `POST /api/orders/create-multileg/` | 多程/联程预订 |
| `GET/POST /api/waitlist/` | 候补购票 |
| `POST /api/chat/` | AI 出行助手 |
| `GET /api/admin/stats/` | 管理统计 |

## 环境变量

复制 `backend/.env.example` 为 `backend/.env`，按需配置：

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,*

# AI 客服（可选）
LLM_ENABLED=true
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

> **注意：** `.env` 已加入 `.gitignore`，请勿将 API Key 提交到仓库。

## 常用命令

```bash
# 导入/更新演示数据（467+ 航班）
python manage.py seed_demo_data

# 取消超时未支付订单
python manage.py expire_orders

# 全局 API 测试
python scripts/global_api_test.py
```

## 文档

课设相关文档见 `docs/` 目录，包括需求分析报告、详细设计报告、用例图等。

## License

本项目为课程设计作品，仅供学习交流使用。
