<template>
  <div class="page-container order-detail-page" v-loading="loading">
    <div class="breadcrumb">
      <router-link to="/orders">我的订单</router-link>
      <span class="sep">/</span>
      <span>订单详情</span>
    </div>

    <div class="detail-layout" v-if="order.id">
      <div class="detail-main">
        <div class="status-banner" :class="order.status">
          <div class="status-icon">{{ statusIcon }}</div>
          <div>
            <h2>{{ getStatusText(order.status) }}</h2>
            <p v-if="order.status === 'pending'">
              请在 30 分钟内完成支付{{ order.expires_at ? `（截止 ${formatDateTime(order.expires_at)}）` : '' }}
            </p>
            <p v-else-if="order.status === 'ticketed'">出票成功，祝您旅途愉快！</p>
          </div>
        </div>

        <div class="page-card weather-card" v-if="destinationWeather">
          <h3 class="card-heading">目的地天气 · {{ destinationWeather.city }}</h3>
          <div class="weather-row">
            <span class="weather-icon">{{ destinationWeather.icon }}</span>
            <span>{{ destinationWeather.condition }} {{ destinationWeather.temperature }}°C</span>
            <span class="weather-meta">{{ destinationWeather.low }}~{{ destinationWeather.high }}°C · {{ destinationWeather.wind }}</span>
          </div>
          <p class="weather-tip">{{ destinationWeather.tip }}</p>
        </div>

        <div class="page-card map-card" v-if="order.flight">
          <h3 class="card-heading">航线地图</h3>
          <RouteMap :legs="[order.flight]" />
        </div>

        <div class="page-card flight-ticket" v-if="order.flight">
          <div class="ticket-header">
            <span class="ticket-label">航班信息</span>
            <span>{{ order.flight.airline }} {{ order.flight.flight_no }}</span>
          </div>
          <div class="ticket-route">
            <div class="ticket-city">
              <div class="ticket-time">{{ formatTime(order.flight.departure_time) }}</div>
              <div class="ticket-name">{{ order.flight.departure_city }}</div>
              <div class="ticket-date">{{ formatDate(order.flight.departure_time) }}</div>
            </div>
            <div class="ticket-line">
              <div class="ticket-duration">
                {{ calcDuration(order.flight.departure_time, order.flight.arrival_time) }}
              </div>
              <div class="line-visual">
                <span class="dot"></span>
                <span class="dash"></span>
                <span class="plane">✈</span>
                <span class="dash"></span>
                <span class="dot"></span>
              </div>
            </div>
            <div class="ticket-city arrive">
              <div class="ticket-time">{{ formatTime(order.flight.arrival_time) }}</div>
              <div class="ticket-name">{{ order.flight.arrival_city }}</div>
              <div class="ticket-date">{{ formatDate(order.flight.arrival_time) }}</div>
            </div>
          </div>
        </div>

        <div class="page-card review-card" v-if="order.status === 'ticketed' && !hasReviewed">
          <h3 class="card-heading">航班评价</h3>
          <el-rate v-model="reviewForm.rating" />
          <el-input
            v-model="reviewForm.content"
            type="textarea"
            placeholder="分享您的乘机体验（选填）"
            :rows="3"
            style="margin-top: 12px"
          />
          <el-button type="primary" style="margin-top: 12px" :loading="reviewSubmitting" @click="submitReview">
            提交评价
          </el-button>
        </div>

        <div class="page-card passenger-info">
          <h3 class="card-heading">乘客信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">乘客姓名</span>
              <span class="info-value">{{ order.passenger_name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">身份证号</span>
              <span class="info-value">{{ order.passenger_id_card }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">舱位等级</span>
              <span class="info-value">{{ getCabinClass(order.cabin_class) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">座位号</span>
              <span class="info-value">{{ order.seat_number || '未选座' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="detail-sidebar">
        <div class="page-card price-card">
          <h3 class="card-heading">费用明细</h3>
          <div class="price-row" v-if="order.discount_amount > 0">
            <span>优惠金额</span>
            <span>-¥{{ order.discount_amount }}</span>
          </div>
          <div class="price-row" v-if="order.insurance_amount > 0">
            <span>延误险</span>
            <span>¥{{ order.insurance_amount }}</span>
          </div>
          <div class="price-total">
            <span>订单总额</span>
            <span class="total-amount">¥{{ order.total_amount }}</span>
          </div>
          <div class="price-actions">
            <el-button
              v-if="order.status === 'pending'"
              class="btn-accent"
              style="width: 100%"
              size="large"
              @click="handlePay"
            >
              立即支付 ¥{{ order.total_amount }}
            </el-button>
            <el-button
              v-if="order.status === 'pending'"
              type="danger"
              plain
              style="width: 100%; margin-top: 10px; margin-left: 0"
              @click="handleCancel"
            >
              取消订单
            </el-button>
            <el-button
              v-if="order.status === 'ticketed'"
              type="primary"
              plain
              style="width: 100%; margin-left: 0"
              @click="$router.push(`/orders/${order.id}/ticket`)"
            >
              查看电子客票
            </el-button>
            <el-button
              v-if="order.status === 'ticketed'"
              plain
              style="width: 100%; margin-top: 10px; margin-left: 0"
              @click="openShare"
            >
              分享行程
            </el-button>
            <el-button
              v-if="order.status === 'ticketed'"
              plain
              style="width: 100%; margin-top: 10px; margin-left: 0"
              @click="handleInvoice"
            >
              申请发票
            </el-button>
            <el-button
              v-if="order.status === 'ticketed'"
              type="danger"
              plain
              style="width: 100%; margin-top: 10px; margin-left: 0"
              @click="handleRefund"
            >
              申请退款
            </el-button>
            <el-button
              v-if="order.status === 'pending'"
              plain
              style="width: 100%; margin-top: 10px; margin-left: 0"
              @click="changeDialogVisible = true"
            >
              改签航班
            </el-button>
          </div>
        </div>

        <div class="page-card order-meta-card">
          <div class="meta-row">
            <span class="meta-label">订单号</span>
            <span class="meta-value">{{ order.order_id }}</span>
          </div>
          <div class="meta-row">
            <span class="meta-label">创建时间</span>
            <span class="meta-value">{{ formatDateTime(order.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <el-dialog v-model="payDialogVisible" title="选择支付方式" width="420px">
      <div class="pay-amount">
        支付金额：<span class="price-text"><span class="currency">¥</span><span class="amount">{{ order.total_amount }}</span></span>
      </div>
      <div class="pay-methods">
        <div
          class="pay-method"
          :class="{ active: payForm.payment_method === 'wechat' }"
          @click="payForm.payment_method = 'wechat'"
        >
          <span class="pay-icon wechat">微</span>
          <span>微信支付</span>
        </div>
        <div
          class="pay-method"
          :class="{ active: payForm.payment_method === 'alipay' }"
          @click="payForm.payment_method = 'alipay'"
        >
          <span class="pay-icon alipay">支</span>
          <span>支付宝</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="payDialogVisible = false">取消</el-button>
        <el-button class="btn-accent" @click="handleSubmitPay" :loading="paying">
          确认支付
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="changeDialogVisible" title="改签航班" width="400px">
      <el-input v-model="newFlightId" placeholder="输入新航班 ID" />
      <template #footer>
        <el-button @click="changeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChange">确认改签</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="shareVisible" title="分享行程" width="440px">
      <TripShareCard v-if="shareData.title" :data="shareData" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { orderApi } from '@/api/order'
import { paymentApi } from '@/api/payment'
import { flightApi } from '@/api/flight'
import { coreApi } from '@/api/core'
import { ElMessage, ElMessageBox } from 'element-plus'
import TripShareCard from '@/components/TripShareCard.vue'
import RouteMap from '@/components/RouteMap.vue'
import {
  CABIN_MAP,
  ORDER_STATUS_MAP,
  formatDateTime,
  formatTime,
  formatDate,
  calcDuration
} from '@/utils/travel'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const paying = ref(false)
const order = ref({})
const payDialogVisible = ref(false)
const changeDialogVisible = ref(false)
const newFlightId = ref('')
const payForm = ref({ payment_method: 'wechat' })
const shareVisible = ref(false)
const shareData = ref({})
const hasReviewed = ref(false)
const reviewSubmitting = ref(false)
const reviewForm = ref({ rating: 5, content: '' })
const destinationWeather = ref(null)

const statusIcon = computed(() => {
  const map = { pending: '⏳', paid: '💳', ticketed: '✅', cancelled: '❌' }
  return map[order.value.status] || '📋'
})

const getCabinClass = (cabin) => CABIN_MAP[cabin] || cabin
const getStatusText = (status) => ORDER_STATUS_MAP[status]?.text || status

const handlePay = () => {
  payDialogVisible.value = true
}

const handleSubmitPay = async () => {
  paying.value = true
  try {
    await paymentApi.create(order.value.id, payForm.value)
    ElMessage.success('支付成功，已出票')
    payDialogVisible.value = false
    fetchOrder()
  } finally {
    paying.value = false
  }
}

const handleCancel = async () => {
  await ElMessageBox.confirm('确定取消订单吗？', '提示', { type: 'warning' })
  await orderApi.cancel(order.value.id)
  ElMessage.success('订单已取消')
  fetchOrder()
}

const handleRefund = async () => {
  const { value } = await ElMessageBox.prompt('请填写退款原因', '申请退款')
  await orderApi.refund(order.value.id, { reason: value })
  ElMessage.success('退款已处理')
  fetchOrder()
}

const handleInvoice = async () => {
  const { value } = await ElMessageBox.prompt('请输入发票抬头', '申请发票')
  await paymentApi.createInvoice(order.value.id, { title: value })
  ElMessage.success('发票已开具')
}

const handleChange = async () => {
  if (!newFlightId.value) return
  const res = await orderApi.change(order.value.id, { new_flight: Number(newFlightId.value) })
  ElMessage.success('改签成功')
  changeDialogVisible.value = false
  router.push(`/orders/${res.order.id}`)
}

const openShare = async () => {
  shareData.value = await orderApi.getShare(order.value.id)
  shareVisible.value = true
}

const submitReview = async () => {
  reviewSubmitting.value = true
  try {
    await flightApi.createReview({
      order_id: order.value.id,
      rating: reviewForm.value.rating,
      content: reviewForm.value.content,
    })
    ElMessage.success('评价已提交，感谢您的反馈')
    hasReviewed.value = true
  } finally {
    reviewSubmitting.value = false
  }
}

const loadExtras = async () => {
  if (order.value.status !== 'ticketed' || !order.value.flight) return
  try {
    const reviews = await flightApi.getReviews(order.value.flight.id)
    hasReviewed.value = (reviews.reviews || []).some(
      r => r.order === order.value.id
    )
    if (order.value.flight.arrival_city) {
      destinationWeather.value = await coreApi.getWeather(order.value.flight.arrival_city)
    }
  } catch { /* ignore */ }
}

const fetchOrder = async () => {
  loading.value = true
  try {
    order.value = await orderApi.getDetail(route.params.id)
    await loadExtras()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchOrder()
})
</script>

<style scoped>
.order-detail-page {
  padding-top: 24px;
}

.breadcrumb {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 20px;
}

.breadcrumb a {
  color: var(--primary);
}

.breadcrumb .sep {
  margin: 0 8px;
}

.detail-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 20px;
  align-items: start;
}

.status-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-radius: var(--radius);
  margin-bottom: 16px;
  background: #fff;
  box-shadow: var(--shadow-sm);
}

.status-banner.pending {
  border-left: 4px solid var(--warning);
}

.status-banner.ticketed {
  border-left: 4px solid var(--success);
}

.status-banner.cancelled {
  border-left: 4px solid var(--danger);
}

.status-icon {
  font-size: 32px;
}

.status-banner h2 {
  margin: 0 0 4px;
  font-size: 18px;
}

.status-banner p {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
}

.weather-card, .review-card {
  margin-bottom: 16px;
}

.weather-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
}

.weather-icon { font-size: 28px; }
.weather-meta { font-size: 13px; color: var(--text-muted); }
.weather-tip { margin: 8px 0 0; font-size: 13px; color: var(--text-secondary); }

.flight-ticket {
  margin-bottom: 16px;
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  font-size: 14px;
  color: var(--text-secondary);
}

.ticket-label {
  font-weight: 600;
  color: var(--text-primary);
}

.ticket-route {
  display: flex;
  align-items: center;
  gap: 20px;
}

.ticket-city {
  text-align: center;
  min-width: 100px;
}

.ticket-time {
  font-size: 32px;
  font-weight: 700;
}

.ticket-name {
  font-size: 16px;
  font-weight: 500;
  margin-top: 4px;
}

.ticket-date {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
}

.ticket-line {
  flex: 1;
  text-align: center;
}

.ticket-duration {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.line-visual {
  display: flex;
  align-items: center;
  justify-content: center;
}

.line-visual .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
}

.line-visual .dash {
  width: 40px;
  height: 2px;
  background: var(--primary-light);
}

.line-visual .plane {
  margin: 0 6px;
  color: var(--primary);
}

.card-heading {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--text-muted);
}

.info-value {
  font-size: 15px;
  font-weight: 500;
}

.price-card {
  margin-bottom: 16px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.price-total {
  display: flex;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px dashed var(--border);
  font-weight: 600;
}

.total-amount {
  font-size: 22px;
  color: var(--accent);
}

.price-actions {
  margin-top: 20px;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 8px 0;
}

.meta-label {
  color: var(--text-muted);
}

.meta-value {
  color: var(--text-primary);
  font-weight: 500;
}

.pay-amount {
  text-align: center;
  font-size: 15px;
  margin-bottom: 20px;
}

.pay-methods {
  display: flex;
  gap: 12px;
}

.pay-method {
  flex: 1;
  border: 2px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.pay-method.active {
  border-color: var(--primary);
  background: var(--primary-light);
}

.pay-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 16px;
}

.pay-icon.wechat {
  background: #07c160;
}

.pay-icon.alipay {
  background: #1677ff;
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .ticket-route {
    flex-direction: column;
  }
}
</style>
