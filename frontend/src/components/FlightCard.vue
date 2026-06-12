<template>
  <div class="flight-card" :class="{ unavailable: !flight.is_available }">
    <div class="card-left">
      <div class="airline-info">
        <div class="airline-logo" :style="{ background: airlineColor }">
          {{ (flight.airline || '航')[0] }}
        </div>
        <div>
          <div class="airline-name">{{ flight.airline }}</div>
          <div class="flight-no">{{ flight.flight_no }}</div>
        </div>
      </div>
    </div>

    <div class="card-center">
      <div class="route">
        <div class="time-block">
          <div class="time">{{ formatTime(flight.departure_time) }}</div>
          <div class="city">{{ flight.departure_city }}</div>
        </div>
        <div class="route-line">
          <div class="duration">{{ duration }}</div>
          <div class="line">
            <span class="dot start"></span>
            <span class="dash"></span>
            <span class="plane">✈</span>
            <span class="dash"></span>
            <span class="dot end"></span>
          </div>
          <div class="direct">{{ directLabel }}</div>
        </div>
        <div class="time-block arrive">
          <div class="time">{{ formatTime(flight.arrival_time) }}</div>
          <div class="city">{{ flight.arrival_city }}</div>
        </div>
      </div>
      <div class="meta">
        <span>{{ formatDateTime(flight.departure_time) }} 出发</span>
        <span class="sep">|</span>
        <span>余票 {{ flight.available_seats }} 张</span>
        <span class="sep">|</span>
        <span class="carbon">🌱 {{ flight.carbon_kg }}kg 碳排放</span>
        <el-tag v-if="flight.recommend_tag" size="small" type="success" style="margin-left: 8px">
          {{ flight.recommend_tag }}
        </el-tag>
        <el-tag v-if="flight.status !== 'normal'" size="small" type="warning" style="margin-left: 8px">
          {{ statusText }}
        </el-tag>
      </div>
    </div>

    <div class="card-actions-extra">
      <el-checkbox
        :model-value="compareSelected"
        @change="v => $emit('compare-change', flight, v)"
        size="small"
      >对比</el-checkbox>
      <el-button
        v-if="showAlert"
        link
        size="small"
        :type="alertSubscribed ? 'warning' : 'primary'"
        @click.stop="$emit('subscribe-alert', flight)"
      >
        {{ alertSubscribed ? '已订阅' : '🔔 订阅' }}
      </el-button>
    </div>

    <div class="card-right">
      <div class="price-block">
        <div class="price-text">
          <span class="currency">¥</span>
          <span class="amount">{{ flight.base_price }}</span>
          <span class="suffix">起</span>
        </div>
        <div class="cabin-hint">经济舱含税价</div>
        <div v-if="avgRating" class="rating-hint">★ {{ avgRating }} ({{ reviewCount }}评)</div>
      </div>
      <el-button
        v-if="selectMode"
        class="btn-accent book-btn"
        :type="selected ? 'primary' : 'default'"
        :disabled="!flight.is_available"
        @click="$emit('select', flight)"
      >
        {{ selected ? '已选' : '选择' }}
      </el-button>
      <el-button
        v-else-if="waitlistMode && !flight.is_available && flight.status === 'normal'"
        class="btn-accent book-btn"
        type="warning"
        @click="$emit('waitlist', flight)"
      >
        候补购票
      </el-button>
      <el-button
        v-else
        class="btn-accent book-btn"
        :disabled="!flight.is_available"
        @click="$emit('book', flight)"
      >
        {{ flight.is_available ? '预订' : '售罄' }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatTime, formatDateTime, calcDuration, getAirlineColor } from '@/utils/travel'

const props = defineProps({
  flight: { type: Object, required: true },
  compareSelected: { type: Boolean, default: false },
  selectMode: { type: Boolean, default: false },
  selected: { type: Boolean, default: false },
  showAlert: { type: Boolean, default: false },
  alertSubscribed: { type: Boolean, default: false },
  avgRating: { type: [Number, String], default: null },
  reviewCount: { type: Number, default: 0 },
  waitlistMode: { type: Boolean, default: false },
  directLabel: { type: String, default: '直飞' },
})

defineEmits(['book', 'compare-change', 'select', 'subscribe-alert', 'waitlist'])

const airlineColor = computed(() => getAirlineColor(props.flight.airline))
const duration = computed(() => calcDuration(props.flight.departure_time, props.flight.arrival_time))

const statusText = computed(() => {
  const map = { normal: '正常', delayed: '延误', cancelled: '取消', departed: '已起飞', landed: '已降落' }
  return map[props.flight.status] || props.flight.status
})
</script>

<style scoped>
.flight-card {
  display: flex;
  align-items: center;
  gap: 24px;
  background: #fff;
  border-radius: var(--radius);
  padding: 20px 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid transparent;
  transition: all 0.25s;
}

.flight-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--primary-light);
}

.flight-card.unavailable {
  opacity: 0.65;
}

.card-left {
  width: 130px;
  flex-shrink: 0;
}

.airline-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.airline-logo {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.airline-name {
  font-size: 13px;
  color: var(--text-secondary);
}

.flight-no {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-center {
  flex: 1;
  min-width: 0;
}

.route {
  display: flex;
  align-items: center;
  gap: 16px;
}

.time-block {
  text-align: center;
  min-width: 72px;
}

.time-block.arrive {
  text-align: center;
}

.time {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.city {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.route-line {
  flex: 1;
  text-align: center;
  min-width: 120px;
}

.duration {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  flex-shrink: 0;
}

.dash {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, var(--primary), #b3d9ff);
  max-width: 60px;
}

.plane {
  font-size: 14px;
  color: var(--primary);
  margin: 0 4px;
}

.direct {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 4px;
}

.meta {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-muted);
}

.sep {
  margin: 0 8px;
}

.carbon { color: var(--success); font-size: 12px; }
.card-actions-extra { flex-shrink: 0; display: flex; flex-direction: column; gap: 4px; align-items: flex-start; }
.rating-hint { font-size: 11px; color: #fa8c16; margin-top: 2px; }
.card-right {
  width: 140px;
  text-align: center;
  flex-shrink: 0;
}

.price-block {
  margin-bottom: 10px;
}

.price-text .suffix {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 400;
  margin-left: 2px;
}

.cabin-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.book-btn {
  width: 100%;
}

@media (max-width: 900px) {
  .flight-card {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }

  .card-left, .card-right {
    width: 100%;
  }

  .card-right {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top: 1px dashed var(--border);
    padding-top: 16px;
  }

  .price-block {
    margin-bottom: 0;
    text-align: left;
  }

  .book-btn {
    width: auto;
    min-width: 100px;
  }
}
</style>
