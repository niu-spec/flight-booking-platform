<template>
  <div class="share-card" ref="cardRef">
    <div class="share-header">
      <span class="share-logo">✈ 行程分享</span>
      <span class="share-route">{{ data.title }}</span>
    </div>
    <div class="share-body">
      <div class="share-subtitle">{{ data.subtitle }}</div>
      <div class="share-times" v-if="data.departure_time">
        <span>{{ formatTime(data.departure_time) }} 出发</span>
        <span class="arrow">→</span>
        <span>{{ formatTime(data.arrival_time) }} 到达</span>
      </div>
      <div class="share-weather" v-if="data.weather">
        <span>{{ data.weather.icon }} {{ data.weather.city }} {{ data.weather.condition }} {{ data.weather.temperature }}°C</span>
        <span class="weather-tip">{{ data.weather.tip }}</span>
      </div>
      <canvas ref="qrCanvas" class="share-qr" width="120" height="120"></canvas>
    </div>
    <div class="share-actions">
      <el-button type="primary" plain size="small" @click="copyText">复制分享文案</el-button>
      <el-button type="primary" size="small" @click="nativeShare" v-if="canShare">分享</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import QRCode from 'qrcode'
import { ElMessage } from 'element-plus'
import { formatTime } from '@/utils/travel'

const props = defineProps({
  data: { type: Object, required: true }
})

const qrCanvas = ref(null)
const canShare = computed(() => typeof navigator.share === 'function')

const drawQr = async () => {
  if (!qrCanvas.value || !props.data.qr_payload) return
  await QRCode.toCanvas(qrCanvas.value, props.data.qr_payload, {
    width: 120,
    margin: 1,
    color: { dark: '#1677ff' },
  })
}

const copyText = async () => {
  const text = props.data.share_text || props.data.title
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('分享文案已复制')
  } catch {
    ElMessage.warning('复制失败，请手动复制')
  }
}

const nativeShare = async () => {
  try {
    await navigator.share({
      title: props.data.title,
      text: props.data.share_text,
    })
  } catch {
    copyText()
  }
}

onMounted(drawQr)
</script>

<style scoped>
.share-card {
  background: linear-gradient(135deg, #e8f4ff 0%, #fff 60%);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border);
}
.share-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.share-logo { font-weight: 700; color: var(--primary); }
.share-route { font-size: 16px; font-weight: 600; }
.share-subtitle { color: var(--text-secondary); font-size: 14px; margin-bottom: 8px; }
.share-times { font-size: 13px; color: var(--text-muted); margin-bottom: 10px; }
.share-times .arrow { margin: 0 8px; color: var(--primary); }
.share-weather {
  background: #fff;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 13px;
  margin-bottom: 12px;
}
.weather-tip { display: block; font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.share-qr { display: block; margin: 0 auto 12px; border-radius: 8px; }
.share-actions { display: flex; gap: 8px; justify-content: center; }
</style>
