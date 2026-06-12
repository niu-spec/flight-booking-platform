<template>
  <div class="page-container ticket-page" v-loading="loading">
    <div class="ticket-card" v-if="ticket.ticket_no">
      <div class="ticket-header">
        <span class="ticket-logo">✈ 电子客票</span>
        <span class="ticket-no">{{ ticket.ticket_no }}</span>
      </div>
      <div class="ticket-route">
        <div>
          <div class="city">{{ ticket.departure_city }}</div>
          <div class="time">{{ formatTime(ticket.departure_time) }}</div>
        </div>
        <div class="arrow">→ {{ ticket.flight_no }} →</div>
        <div>
          <div class="city">{{ ticket.arrival_city }}</div>
          <div class="time">{{ formatTime(ticket.arrival_time) }}</div>
        </div>
      </div>
      <div class="ticket-info">
        <div><label>乘客</label>{{ ticket.passenger_name }}</div>
        <div><label>身份证</label>{{ ticket.passenger_id_card }}</div>
        <div><label>舱位</label>{{ CABIN_MAP[ticket.cabin_class] }}</div>
        <div><label>座位</label>{{ ticket.seat_number }}</div>
        <div><label>航司</label>{{ ticket.airline }}</div>
        <div><label>订单号</label>{{ ticket.order_id }}</div>
      </div>
      <div class="ticket-qr-wrap">
        <canvas ref="qrCanvas" class="ticket-qr"></canvas>
        <p class="qr-label">扫码登机</p>
      </div>
      <div class="ticket-actions">
        <el-button type="primary" plain @click="shareVisible = true">分享行程</el-button>
        <el-button type="primary" @click="$router.push(`/orders/${route.params.id}`)">返回订单</el-button>
      </div>
      <p class="ticket-tip">请凭此电子客票和有效证件办理登机手续</p>
    </div>

    <el-dialog v-model="shareVisible" title="分享行程" width="440px">
      <TripShareCard v-if="shareData.title" :data="shareData" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import QRCode from 'qrcode'
import { orderApi } from '@/api/order'
import { formatTime, CABIN_MAP } from '@/utils/travel'
import TripShareCard from '@/components/TripShareCard.vue'

const route = useRoute()
const loading = ref(false)
const ticket = ref({})
const qrCanvas = ref(null)
const shareVisible = ref(false)
const shareData = ref({})

const drawQr = async () => {
  if (!qrCanvas.value || !ticket.value.qr_payload) return
  await QRCode.toCanvas(qrCanvas.value, ticket.value.qr_payload, {
    width: 160,
    margin: 2,
    color: { dark: '#1677ff' },
  })
}

onMounted(async () => {
  loading.value = true
  try {
    ticket.value = await orderApi.getTicket(route.params.id)
    await drawQr()
    shareData.value = await orderApi.getShare(route.params.id)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.ticket-page { display: flex; justify-content: center; padding-top: 32px; }
.ticket-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  padding: 32px;
  max-width: 520px;
  width: 100%;
  border-top: 6px solid var(--primary);
}
.ticket-header { display: flex; justify-content: space-between; margin-bottom: 24px; }
.ticket-logo { font-size: 18px; font-weight: 700; color: var(--primary); }
.ticket-no { font-size: 13px; color: var(--text-muted); }
.ticket-route { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; text-align: center; }
.city { font-size: 22px; font-weight: 700; }
.time { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
.arrow { color: var(--primary); font-size: 14px; }
.ticket-info { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; font-size: 14px; }
.ticket-info label { color: var(--text-muted); margin-right: 8px; }
.ticket-qr-wrap {
  text-align: center;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 16px;
}
.ticket-qr { display: inline-block; border-radius: 8px; }
.qr-label { font-size: 12px; color: var(--text-muted); margin-top: 8px; }
.ticket-actions { display: flex; gap: 10px; justify-content: center; margin-bottom: 12px; }
.ticket-tip { text-align: center; font-size: 12px; color: var(--text-muted); }
</style>
