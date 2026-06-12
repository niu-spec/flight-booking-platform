<template>
  <div class="page-container waitlist-page">
    <div class="page-header">
      <h1 class="page-title">我的候补</h1>
      <p class="page-subtitle">航班有余票释放时将自动为您生成订单，请在 30 分钟内支付</p>
    </div>

    <div v-loading="loading" class="waitlist-list">
      <template v-if="entries.length">
        <div v-for="item in entries" :key="item.id" class="waitlist-card page-card">
          <div class="wl-main">
            <div class="wl-route">{{ item.departure_city }} → {{ item.arrival_city }}</div>
            <div class="wl-meta">
              {{ item.flight_no }} · {{ formatDateTime(item.departure_time) }}
            </div>
            <div class="wl-passenger">乘客 {{ item.passenger_name }}</div>
          </div>
          <div class="wl-status">
            <el-tag :type="statusType(item.status)">{{ statusText(item.status) }}</el-tag>
            <div v-if="item.status === 'waiting'" class="wl-position">排队第 {{ item.position }} 位</div>
            <el-button
              v-if="item.status === 'waiting'"
              type="danger"
              plain
              size="small"
              @click="handleCancel(item)"
            >取消候补</el-button>
            <el-button
              v-if="item.status === 'fulfilled' && item.order"
              type="primary"
              size="small"
              @click="$router.push(`/orders/${item.order}`)"
            >去支付</el-button>
          </div>
        </div>
      </template>
      <div v-else-if="!loading" class="empty-state page-card">
        <div class="empty-icon">🎫</div>
        <p>暂无候补记录</p>
        <el-button type="primary" style="margin-top: 16px" @click="$router.push('/flights')">
          去搜索航班
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { waitlistApi } from '@/api/waitlist'
import { formatDateTime } from '@/utils/travel'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const entries = ref([])

const statusText = (s) => ({ waiting: '候补中', fulfilled: '已兑现', cancelled: '已取消' }[s] || s)
const statusType = (s) => ({ waiting: 'warning', fulfilled: 'success', cancelled: 'info' }[s] || 'info')

const fetchList = async () => {
  loading.value = true
  try {
    const res = await waitlistApi.getList()
    entries.value = (res.results || res).filter(e => e.status !== 'cancelled')
  } finally {
    loading.value = false
  }
}

const handleCancel = async (item) => {
  await ElMessageBox.confirm('确定取消候补吗？', '提示', { type: 'warning' })
  await waitlistApi.cancel(item.id)
  ElMessage.success('已取消候补')
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.waitlist-page { padding-top: 32px; }
.waitlist-list { display: flex; flex-direction: column; gap: 12px; min-height: 200px; }
.waitlist-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 20px 24px;
}
.wl-route { font-size: 18px; font-weight: 600; color: var(--primary); }
.wl-meta, .wl-passenger { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
.wl-status { text-align: right; display: flex; flex-direction: column; gap: 8px; align-items: flex-end; }
.wl-position { font-size: 12px; color: var(--warning); }
</style>
