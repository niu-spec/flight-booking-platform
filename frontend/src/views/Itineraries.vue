<template>
  <div class="page-container itineraries-page">
    <div class="page-header">
      <h1 class="page-title">我的行程</h1>
      <p class="page-subtitle">管理您的出行计划，实时掌握航班动态</p>
    </div>

    <div v-loading="loading" class="itinerary-list">
      <template v-if="itineraries.length">
        <div v-for="item in itineraries" :key="item.id" class="itinerary-card">
          <div class="itin-status" :class="item.status">
            <el-tag :type="getStatusType(item.status)" size="small">
              {{ getStatusText(item.status) }}
            </el-tag>
          </div>

          <div class="itin-main">
            <div class="itin-route">
              <div class="itin-city-block">
                <div class="itin-time">{{ formatTime(item.departure_time) }}</div>
                <div class="itin-city">{{ item.departure_city }}</div>
              </div>
              <div class="itin-arrow">
                <div class="itin-flight-no">{{ item.flight_no }}</div>
                <div class="arrow-line">——— ✈ ———</div>
                <div class="itin-airline">{{ item.airline }}</div>
              </div>
              <div class="itin-city-block arrive">
                <div class="itin-time">{{ formatTime(item.arrival_time) }}</div>
                <div class="itin-city">{{ item.arrival_city }}</div>
              </div>
            </div>

            <RouteMap
              :cities="[item.departure_city, item.arrival_city]"
              compact
              style="margin: 10px 0"
            />

            <div class="itin-meta">
              <span>行程号 {{ item.itinerary_id }}</span>
              <span class="sep">|</span>
              <span>{{ formatDate(item.departure_time) }} 出发</span>
              <span class="sep">|</span>
              <span>{{ getCabinClass(item.cabin_class) }}</span>
            </div>
            <div class="itin-weather" v-if="weatherMap[item.arrival_city]">
              <span>{{ weatherMap[item.arrival_city].icon }} {{ item.arrival_city }}</span>
              <span>{{ weatherMap[item.arrival_city].condition }} {{ weatherMap[item.arrival_city].temperature }}°C</span>
              <span class="weather-tip">{{ weatherMap[item.arrival_city].tip }}</span>
            </div>
          </div>

          <div class="itin-actions">
            <el-button type="primary" plain size="small" @click="handleRefresh(item)">
              刷新状态
            </el-button>
            <el-button plain size="small" @click="handleShare(item)">分享</el-button>
          </div>
        </div>
      </template>
      <div v-else-if="!loading" class="empty-state page-card">
        <div class="empty-icon">🗺️</div>
        <p>暂无行程安排</p>
        <p style="font-size: 13px; margin-top: 8px">完成机票预订并支付后，行程将自动出现在这里</p>
        <el-button type="primary" style="margin-top: 16px" @click="$router.push('/flights')">
          预订机票
        </el-button>
      </div>
    </div>

    <el-dialog v-model="shareVisible" title="分享行程" width="440px">
      <TripShareCard v-if="shareData.title" :data="shareData" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { itineraryApi } from '@/api/itinerary'
import { orderApi } from '@/api/order'
import { coreApi } from '@/api/core'
import { ElMessage } from 'element-plus'
import TripShareCard from '@/components/TripShareCard.vue'
import RouteMap from '@/components/RouteMap.vue'
import { CABIN_MAP, ITINERARY_STATUS_MAP, formatTime, formatDate } from '@/utils/travel'

const loading = ref(false)
const itineraries = ref([])
const weatherMap = ref({})
const shareVisible = ref(false)
const shareData = ref({})

const getCabinClass = (cabin) => CABIN_MAP[cabin] || cabin
const getStatusText = (status) => ITINERARY_STATUS_MAP[status]?.text || status
const getStatusType = (status) => ITINERARY_STATUS_MAP[status]?.type || 'info'

const handleRefresh = async (itinerary) => {
  await itineraryApi.refresh(itinerary.id)
  ElMessage.success('行程状态已刷新')
  fetchItineraries()
}

const loadWeather = async (list) => {
  const cities = [...new Set(list.map(i => i.arrival_city).filter(Boolean))]
  const map = {}
  await Promise.all(cities.map(async (city) => {
    try {
      map[city] = await coreApi.getWeather(city)
    } catch { /* ignore */ }
  }))
  weatherMap.value = map
}

const handleShare = async (item) => {
  if (!item.order) {
    ElMessage.warning('无法分享该行程')
    return
  }
  shareData.value = await orderApi.getShare(item.order)
  shareVisible.value = true
}

const fetchItineraries = async () => {
  loading.value = true
  try {
    const response = await itineraryApi.getList()
    itineraries.value = response.results || response
    await loadWeather(itineraries.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchItineraries()
})
</script>

<style scoped>
.itineraries-page {
  padding-top: 32px;
}

.page-header {
  margin-bottom: 24px;
}

.itinerary-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
}

.itinerary-card {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: box-shadow 0.2s;
  border-left: 4px solid var(--primary);
}

.itinerary-card:hover {
  box-shadow: var(--shadow-md);
}

.itin-status {
  flex-shrink: 0;
}

.itin-main {
  flex: 1;
  min-width: 0;
}

.itin-route {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
}

.itin-city-block {
  min-width: 80px;
}

.itin-time {
  font-size: 24px;
  font-weight: 700;
}

.itin-city {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.itin-arrow {
  flex: 1;
  text-align: center;
  min-width: 120px;
}

.itin-flight-no {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
}

.arrow-line {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 2px;
  margin: 4px 0;
}

.itin-airline {
  font-size: 12px;
  color: var(--text-muted);
}

.itin-meta {
  font-size: 12px;
  color: var(--text-muted);
}

.itin-meta .sep {
  margin: 0 8px;
}

.itin-weather {
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.itin-weather .weather-tip {
  font-size: 12px;
  color: var(--text-muted);
}

.itin-actions {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

@media (max-width: 768px) {
  .itinerary-card {
    flex-direction: column;
    align-items: stretch;
  }

  .itin-route {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
