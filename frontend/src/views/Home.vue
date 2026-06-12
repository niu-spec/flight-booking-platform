<template>
  <div class="home">
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <h1 class="hero-title">发现低价机票，开启美好旅程</h1>
        <p class="hero-subtitle">覆盖全国热门航线，实时查询，一键预订</p>
        <div class="hero-search">
          <FlightSearchBox :loading="false" @search="goSearch" />
        </div>
      </div>
    </section>

    <section class="page-container features">
      <h2 class="section-title">为什么选择我们</h2>
      <div class="feature-grid">
        <div v-for="item in features" :key="item.title" class="feature-card">
          <div class="feature-icon">{{ item.icon }}</div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </div>
      </div>
    </section>

    <section class="page-container routes">
      <h2 class="section-title">热门航线推荐</h2>
      <div class="route-grid">
        <div
          v-for="route in hotRoutes"
          :key="route.label"
          class="route-card"
          @click="goRoute(route)"
        >
          <div class="route-cities">
            <span>{{ route.from }}</span>
            <span class="route-arrow">→</span>
            <span>{{ route.to }}</span>
          </div>
          <div class="route-price">低至 ¥{{ route.price }} 起</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import FlightSearchBox from '@/components/FlightSearchBox.vue'

const router = useRouter()

const features = [
  { icon: '🤖', title: '智能助手', desc: 'AI 客服即时解答，出行清单自动生成' },
  { icon: '🌱', title: '低碳飞行', desc: '碳排放可视化，推荐绿色出行航班' },
  { icon: '🔔', title: '降价提醒', desc: '订阅航线目标价，低价机票不错过' },
  { icon: '🥇', title: '积分会员', desc: '消费赚积分，银卡金卡享更多权益' },
  { icon: '⚖️', title: '航班对比', desc: '最多3个航班横向对比，决策更高效' },
  { icon: '🛡️', title: '安心保障', desc: '订单全程可追踪，出行更放心' }
]

const hotRoutes = [
  { from: '北京', to: '上海', price: 450, label: '北京-上海' },
  { from: '广州', to: '成都', price: 520, label: '广州-成都' },
  { from: '深圳', to: '杭州', price: 480, label: '深圳-杭州' },
  { from: '上海', to: '西安', price: 550, label: '上海-西安' },
  { from: '北京', to: '广州', price: 680, label: '北京-广州' },
  { from: '成都', to: '重庆', price: 280, label: '成都-重庆' }
]

const goSearch = (params) => {
  router.push({ path: '/flights', query: params })
}

const goRoute = (route) => {
  router.push({
    path: '/flights',
    query: { departure_city: route.from, arrival_city: route.to }
  })
}
</script>

<style scoped>
.home {
  padding-bottom: 0;
}

.hero {
  position: relative;
  padding: 48px 20px 80px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #006fd6 0%, #0086f6 40%, #00a8e8 100%);
}

.hero-bg::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 60px;
  background: var(--bg-page);
  border-radius: 50% 50% 0 0 / 100% 100% 0 0;
}

.hero-content {
  position: relative;
  max-width: var(--max-width);
  margin: 0 auto;
  z-index: 1;
}

.hero-title {
  margin: 0 0 12px;
  font-size: 36px;
  font-weight: 700;
  color: #fff;
  text-align: center;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.hero-subtitle {
  margin: 0 0 36px;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
  text-align: center;
}

.hero-search {
  max-width: 960px;
  margin: 0 auto;
}

.features {
  padding-top: 16px;
}

.section-title {
  text-align: center;
  font-size: 22px;
  font-weight: 600;
  margin: 0 0 28px;
  color: var(--text-primary);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.feature-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 28px 20px;
  text-align: center;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.feature-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.feature-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
  color: var(--text-primary);
}

.feature-card p {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
}

.routes {
  padding-bottom: 48px;
}

.route-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.route-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 20px 24px;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  border: 1px solid transparent;
  transition: all 0.2s;
}

.route-card:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow-md);
}

.route-cities {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.route-arrow {
  margin: 0 12px;
  color: var(--primary);
}

.route-price {
  font-size: 14px;
  color: var(--accent);
  font-weight: 500;
}

@media (max-width: 900px) {
  .hero-title {
    font-size: 26px;
  }

  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .route-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 500px) {
  .feature-grid, .route-grid {
    grid-template-columns: 1fr;
  }
}
</style>
