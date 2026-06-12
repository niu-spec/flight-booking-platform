<template>
  <div class="transfer-card" :class="{ selected }">
    <div class="transfer-header">
      <div>
        <span class="hub-tag">{{ itinerary.hub_city }} 中转</span>
        <span class="layover">{{ formatLayover(itinerary.layover_minutes) }}</span>
      </div>
      <div class="price">
        <span class="currency">¥</span>
        <span class="amount">{{ itinerary.total_price }}</span>
        <span class="suffix">起</span>
      </div>
    </div>

    <RouteMap :legs="itinerary.legs" compact />

    <div class="legs">
      <div v-for="(leg, i) in itinerary.legs" :key="leg.id" class="leg-row">
        <span class="leg-index">{{ i + 1 }}</span>
        <div class="leg-info">
          <div class="leg-route">
            {{ leg.departure_city }} {{ formatTime(leg.departure_time) }}
            → {{ leg.arrival_city }} {{ formatTime(leg.arrival_time) }}
          </div>
          <div class="leg-meta">{{ leg.airline }} {{ leg.flight_no }} · ¥{{ leg.base_price }}</div>
        </div>
      </div>
    </div>

    <el-button
      class="btn-accent select-btn"
      :type="selected ? 'primary' : 'default'"
      @click="$emit('select', itinerary)"
    >
      {{ selected ? '已选联程' : '选择此联程' }}
    </el-button>
  </div>
</template>

<script setup>
import RouteMap from '@/components/RouteMap.vue'
import { formatTime, formatLayover } from '@/utils/travel'

defineProps({
  itinerary: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})

defineEmits(['select'])
</script>

<style scoped>
.transfer-card {
  background: #fff;
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 2px solid transparent;
  transition: all 0.2s;
}
.transfer-card.selected {
  border-color: var(--primary);
  box-shadow: var(--shadow-md);
}
.transfer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.hub-tag {
  background: var(--primary-light);
  color: var(--primary);
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 600;
}
.layover {
  margin-left: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
.price .amount {
  font-size: 24px;
  font-weight: 700;
  color: var(--accent);
}
.legs { margin: 14px 0; }
.leg-row {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--border);
}
.leg-row:last-child { border-bottom: none; }
.leg-index {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.leg-route { font-size: 14px; font-weight: 500; }
.leg-meta { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.select-btn { width: 100%; }
</style>
