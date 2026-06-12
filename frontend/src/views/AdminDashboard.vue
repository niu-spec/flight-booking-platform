<template>
  <div class="page-container">
    <h1 class="page-title">管理看板</h1>
    <div class="stats-grid" v-loading="loading">
      <div class="stat-card" v-for="item in statCards" :key="item.label">
        <div class="stat-value">{{ item.value }}</div>
        <div class="stat-label">{{ item.label }}</div>
      </div>
    </div>
    <div class="page-card" style="margin-top:20px">
      <h3>订单状态分布</h3>
      <div class="status-bars">
        <div v-for="(count, status) in stats.orders_by_status" :key="status" class="status-row">
          <span>{{ statusMap[status] || status }}</span>
          <el-progress :percentage="calcPercent(count)" :format="() => String(count)" />
        </div>
      </div>
    </div>
    <div class="page-card" style="margin-top:20px">
      <h3>热门航线</h3>
      <el-table :data="stats.hot_routes">
        <el-table-column label="航线">
          <template #default="{ row }">{{ row.departure_city }} → {{ row.arrival_city }}</template>
        </el-table-column>
        <el-table-column prop="count" label="订单数" />
      </el-table>
      <el-button style="margin-top:16px" @click="handleExpire">清理超时订单</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const stats = ref({ orders_by_status: {}, hot_routes: [] })
const statusMap = { pending: '待支付', ticketed: '已出票', cancelled: '已取消', refunded: '已退款' }

const statCards = computed(() => [
  { label: '注册用户', value: stats.value.users || 0 },
  { label: '航班数量', value: stats.value.flights || 0 },
  { label: '总订单', value: stats.value.orders_total || 0 },
  { label: '今日订单', value: stats.value.orders_today || 0 },
  { label: '总收入', value: `¥${stats.value.revenue_total || 0}` }
])

const totalOrders = computed(() => stats.value.orders_total || 1)
const calcPercent = (count) => Math.round((count / totalOrders.value) * 100)

const fetchStats = async () => {
  loading.value = true
  try {
    stats.value = await adminApi.getStats()
  } finally {
    loading.value = false
  }
}

const handleExpire = async () => {
  const res = await adminApi.expireOrders()
  ElMessage.success(res.message)
  fetchStats()
}

onMounted(fetchStats)
</script>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; }
.stat-card { background: #fff; border-radius: var(--radius); padding: 24px; text-align: center; box-shadow: var(--shadow-sm); }
.stat-value { font-size: 28px; font-weight: 700; color: var(--primary); }
.stat-label { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
.status-row { display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }
.status-row span { width: 80px; font-size: 13px; }
.status-row .el-progress { flex: 1; }
@media (max-width: 900px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
</style>
