<template>
  <div class="page-container orders-page">
    <div class="page-header">
      <h1 class="page-title">我的订单</h1>
      <p class="page-subtitle">查看和管理您的所有机票订单</p>
    </div>

    <div class="filter-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="filter-tab"
        :class="{ active: activeTab === tab.value }"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
        <span v-if="tab.count" class="tab-count">{{ tab.count }}</span>
      </button>
    </div>

    <div v-loading="loading" class="order-list">
      <template v-if="filteredOrders.length">
        <div v-for="order in filteredOrders" :key="order.id" class="order-card">
          <div class="order-card-header">
            <span class="order-id">订单号：{{ order.order_id }}</span>
            <el-tag :type="getStatusType(order.status)" size="small">
              {{ getStatusText(order.status) }}
            </el-tag>
          </div>

          <div class="order-route" v-if="order.flight">
            <div class="route-main">
              <span class="city">{{ order.flight.departure_city }}</span>
              <span class="arrow">→</span>
              <span class="city">{{ order.flight.arrival_city }}</span>
            </div>
            <div class="route-detail">
              {{ order.flight.airline }} {{ order.flight.flight_no }}
              · {{ getCabinClass(order.cabin_class) }}
              · {{ order.passenger_name }}
            </div>
          </div>

          <div class="order-card-footer">
            <div class="order-meta">
              <span class="order-time">{{ formatDateTime(order.created_at) }}</span>
              <span class="order-price">¥{{ order.total_amount }}</span>
            </div>
            <div class="order-actions">
              <el-button size="small" @click="$router.push(`/orders/${order.id}`)">
                查看详情
              </el-button>
              <el-button
                v-if="order.status === 'pending'"
                type="primary"
                size="small"
                @click="$router.push(`/orders/${order.id}`)"
              >
                去支付
              </el-button>
              <el-button
                v-if="order.status === 'pending'"
                type="danger"
                size="small"
                plain
                @click="handleCancel(order)"
              >
                取消
              </el-button>
            </div>
          </div>
        </div>
      </template>
      <div v-else-if="!loading" class="empty-state page-card">
        <div class="empty-icon">📋</div>
        <p>暂无{{ activeTabLabel }}订单</p>
        <el-button type="primary" style="margin-top: 16px" @click="$router.push('/flights')">
          去预订机票
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { orderApi } from '@/api/order'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CABIN_MAP, ORDER_STATUS_MAP, formatDateTime } from '@/utils/travel'

const loading = ref(false)
const orders = ref([])
const activeTab = ref('all')

const tabs = computed(() => [
  { label: '全部', value: 'all', count: orders.value.length },
  { label: '待支付', value: 'pending', count: orders.value.filter(o => o.status === 'pending').length },
  { label: '已出票', value: 'ticketed', count: orders.value.filter(o => o.status === 'ticketed').length },
  { label: '已取消', value: 'cancelled', count: orders.value.filter(o => o.status === 'cancelled').length }
])

const activeTabLabel = computed(() => {
  const tab = tabs.value.find(t => t.value === activeTab.value)
  return tab?.value === 'all' ? '' : tab?.label
})

const filteredOrders = computed(() => {
  if (activeTab.value === 'all') return orders.value
  return orders.value.filter(o => o.status === activeTab.value)
})

const getCabinClass = (cabin) => CABIN_MAP[cabin] || cabin
const getStatusText = (status) => ORDER_STATUS_MAP[status]?.text || status
const getStatusType = (status) => ORDER_STATUS_MAP[status]?.type || 'info'

const handleCancel = async (order) => {
  await ElMessageBox.confirm('确定取消订单吗？', '提示', { type: 'warning' })
  await orderApi.cancel(order.id)
  ElMessage.success('订单已取消')
  fetchOrders()
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const response = await orderApi.getList()
    orders.value = response.results || response
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.orders-page {
  padding-top: 32px;
}

.page-header {
  margin-bottom: 24px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-tab {
  border: 1px solid var(--border);
  background: #fff;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-tab:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.filter-tab.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
}

.tab-count {
  background: rgba(255, 255, 255, 0.25);
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.filter-tab:not(.active) .tab-count {
  background: var(--primary-light);
  color: var(--primary);
}

.order-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
}

.order-card {
  background: #fff;
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.order-card:hover {
  box-shadow: var(--shadow-md);
}

.order-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  background: #fafbfc;
  border-bottom: 1px solid var(--border);
}

.order-id {
  font-size: 13px;
  color: var(--text-secondary);
}

.order-route {
  padding: 20px;
}

.route-main {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 6px;
}

.route-main .arrow {
  margin: 0 12px;
  color: var(--primary);
}

.route-detail {
  font-size: 13px;
  color: var(--text-muted);
}

.order-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-top: 1px solid var(--border);
}

.order-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.order-time {
  font-size: 13px;
  color: var(--text-muted);
}

.order-price {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent);
}

.order-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 600px) {
  .order-card-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
