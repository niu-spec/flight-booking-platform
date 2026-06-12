<template>
  <div class="search-box" :class="{ compact }">
    <div class="search-tabs">
      <button
        type="button"
        class="tab"
        :class="{ active: form.trip_type === 'one_way' }"
        @click="form.trip_type = 'one_way'"
      >单程</button>
      <button
        type="button"
        class="tab"
        :class="{ active: form.trip_type === 'round_trip' }"
        @click="form.trip_type = 'round_trip'"
      >往返</button>
      <button
        type="button"
        class="tab"
        :class="{ active: form.trip_type === 'transfer' }"
        @click="form.trip_type = 'transfer'"
      >中转</button>
      <button
        type="button"
        class="tab"
        :class="{ active: form.trip_type === 'multi_city' }"
        @click="form.trip_type = 'multi_city'"
      >多程</button>
    </div>
    <el-form :model="form" class="search-form" @submit.prevent="handleSearch">
      <div class="search-row">
        <div class="field-group city-field">
          <label>出发城市</label>
          <el-input
            v-model="form.departure_city"
            placeholder="城市名"
            size="large"
            clearable
          />
        </div>
        <button type="button" class="swap-btn" @click="swapCities" title="互换城市">
          ⇄
        </button>
        <div class="field-group city-field">
          <label>到达城市</label>
          <el-input
            v-model="form.arrival_city"
            placeholder="城市名"
            size="large"
            clearable
          />
        </div>
        <div class="field-group date-field">
          <label>{{ form.trip_type === 'round_trip' ? '去程日期' : '出发日期' }}</label>
          <el-date-picker
            v-model="form.departure_date"
            type="date"
            placeholder="选择日期"
            size="large"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </div>
        <div class="field-group date-field" v-if="form.trip_type === 'round_trip'">
          <label>返程日期</label>
          <el-date-picker
            v-model="form.return_date"
            type="date"
            placeholder="选择日期"
            size="large"
            style="width: 100%"
            :disabled-date="disabledReturnDate"
          />
        </div>
        <template v-if="form.trip_type === 'multi_city'">
          <div class="field-group city-field">
            <label>第二程到达</label>
            <el-input v-model="form.leg2_arrival_city" placeholder="城市名" size="large" clearable />
          </div>
          <div class="field-group date-field">
            <label>第二程日期</label>
            <el-date-picker
              v-model="form.leg2_departure_date"
              type="date"
              placeholder="选择日期"
              size="large"
              style="width: 100%"
              :disabled-date="disabledLeg2Date"
            />
          </div>
        </template>
        <button
          type="button"
          class="voice-btn"
          :class="{ listening }"
          @click="startVoice"
          title="语音搜索"
        >
          🎤
        </button>
        <el-button
          class="search-btn"
          type="primary"
          size="large"
          :loading="loading"
          @click="handleSearch"
        >
          搜索航班
        </el-button>
      </div>
      <div class="hot-cities">
        <span class="hot-label">热门：</span>
        <button
          v-for="city in HOT_CITIES"
          :key="city"
          type="button"
          class="hot-city"
          @click="pickCity(city)"
        >
          {{ city }}
        </button>
      </div>
      <p v-if="voiceHint" class="voice-hint">{{ voiceHint }}</p>
    </el-form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { HOT_CITIES } from '@/utils/travel'

const props = defineProps({
  loading: Boolean,
  compact: Boolean,
  initial: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['search'])

const form = ref({
  trip_type: props.initial.trip_type || 'one_way',
  departure_city: props.initial.departure_city || '',
  arrival_city: props.initial.arrival_city || '',
  departure_date: props.initial.departure_date || null,
  return_date: props.initial.return_date || null,
  leg2_arrival_city: props.initial.leg2_arrival_city || '',
  leg2_departure_date: props.initial.leg2_departure_date || null,
})

const listening = ref(false)
const voiceHint = ref('')

watch(() => props.initial, (val) => {
  if (val) {
    form.value = { ...form.value, ...val }
  }
}, { deep: true })

const disabledDate = (date) => date.getTime() < Date.now() - 86400000

const disabledReturnDate = (date) => {
  if (date.getTime() < Date.now() - 86400000) return true
  if (form.value.departure_date) {
    const dep = new Date(form.value.departure_date)
    dep.setHours(0, 0, 0, 0)
    return date.getTime() < dep.getTime()
  }
  return false
}

const disabledLeg2Date = disabledReturnDate

const swapCities = () => {
  const temp = form.value.departure_city
  form.value.departure_city = form.value.arrival_city
  form.value.arrival_city = temp
}

const pickCity = (city) => {
  if (!form.value.departure_city) {
    form.value.departure_city = city
  } else if (!form.value.arrival_city) {
    form.value.arrival_city = city
  } else {
    form.value.arrival_city = city
  }
}

const parseVoiceText = (text) => {
  const cleaned = text.replace(/[，。！？\s]/g, '')
  const match = cleaned.match(/(.+?)(?:到|去|飞)(.+)/)
  if (match) {
    form.value.departure_city = match[1].replace(/从/g, '')
    form.value.arrival_city = match[2]
    voiceHint.value = `语音识别：${form.value.departure_city} → ${form.value.arrival_city}`
    return true
  }
  voiceHint.value = `识别到：${text}，未能解析城市，请手动确认`
  return false
}

const startVoice = () => {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SR) {
    ElMessage.warning('当前浏览器不支持语音搜索，请使用 Chrome')
    return
  }
  const rec = new SR()
  rec.lang = 'zh-CN'
  rec.interimResults = false
  listening.value = true
  voiceHint.value = '正在聆听…'
  rec.onresult = (e) => {
    const text = e.results[0][0].transcript
    parseVoiceText(text)
    listening.value = false
  }
  rec.onerror = () => {
    listening.value = false
    voiceHint.value = ''
    ElMessage.warning('语音识别失败，请重试')
  }
  rec.onend = () => { listening.value = false }
  rec.start()
}

const handleSearch = () => {
  if (form.value.trip_type === 'round_trip' && !form.value.return_date) {
    ElMessage.warning('请选择返程日期')
    return
  }
  if (form.value.trip_type === 'multi_city') {
    if (!form.value.leg2_arrival_city || !form.value.leg2_departure_date) {
      ElMessage.warning('请填写第二程到达城市和日期')
      return
    }
  }
  const params = { trip_type: form.value.trip_type }
  if (form.value.departure_city) params.departure_city = form.value.departure_city
  if (form.value.arrival_city) params.arrival_city = form.value.arrival_city
  if (form.value.departure_date) {
    params.departure_date = new Date(form.value.departure_date).toISOString().split('T')[0]
  }
  if (form.value.trip_type === 'round_trip' && form.value.return_date) {
    params.return_date = new Date(form.value.return_date).toISOString().split('T')[0]
  }
  if (form.value.trip_type === 'multi_city') {
    params.leg2_arrival_city = form.value.leg2_arrival_city
    params.leg2_departure_date = new Date(form.value.leg2_departure_date).toISOString().split('T')[0]
  }
  emit('search', params)
}

defineExpose({ form })
</script>

<style scoped>
.search-box {
  background: #fff;
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  padding: 24px 28px 20px;
}

.search-box.compact {
  box-shadow: var(--shadow-sm);
  padding: 20px 24px 16px;
}

.search-tabs {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 12px;
}

.tab {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-muted);
  padding-bottom: 10px;
  margin-bottom: -13px;
  cursor: pointer;
  border: none;
  background: none;
}

.tab.active {
  color: var(--primary);
  border-bottom: 3px solid var(--primary);
  font-weight: 600;
}

.tab.disabled {
  opacity: 0.45;
  cursor: default;
}

.search-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.field-group {
  flex: 1;
  min-width: 140px;
}

.field-group label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.city-field {
  flex: 1.2;
  min-width: 160px;
}

.date-field {
  flex: 1;
  min-width: 180px;
}

.swap-btn, .voice-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: #fff;
  color: var(--primary);
  font-size: 16px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.voice-btn.listening {
  background: #fff1f0;
  border-color: #ff4d4f;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  50% { transform: scale(1.08); }
}

.swap-btn:hover, .voice-btn:hover {
  border-color: var(--primary);
  background: var(--primary-light);
}

.search-btn {
  height: 40px !important;
  padding: 0 32px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  border-radius: 8px !important;
  flex-shrink: 0;
}

.hot-cities {
  margin-top: 14px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.hot-label {
  font-size: 12px;
  color: var(--text-muted);
}

.hot-city {
  border: none;
  background: var(--primary-light);
  color: var(--primary);
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.hot-city:hover {
  background: var(--primary);
  color: #fff;
}

.voice-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--primary);
}

@media (max-width: 768px) {
  .search-row {
    flex-direction: column;
    align-items: stretch;
  }

  .swap-btn {
    align-self: center;
    transform: rotate(90deg);
    margin: 0;
  }

  .search-btn {
    width: 100%;
  }
}
</style>
