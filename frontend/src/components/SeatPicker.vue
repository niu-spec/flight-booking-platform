<template>
  <div class="seat-picker" v-loading="loading">
    <div class="seat-legend">
      <span><i class="dot available"></i>可选</span>
      <span><i class="dot occupied"></i>已售</span>
      <span><i class="dot locked"></i>锁定</span>
      <span><i class="dot selected"></i>已选</span>
    </div>
    <div class="seat-grid">
      <button
        v-for="seat in seats"
        :key="seat.seat_number"
        type="button"
        class="seat"
        :class="[seat.status, { active: modelValue === seat.seat_number }]"
        :disabled="seat.status !== 'available'"
        @click="$emit('update:modelValue', seat.seat_number)"
      >
        {{ seat.seat_number }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  seats: { type: Array, default: () => [] },
  modelValue: String,
  loading: Boolean
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.seat-legend {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 12px;
  color: var(--text-muted);
}
.dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 3px;
  margin-right: 4px;
  vertical-align: middle;
}
.dot.available { background: #e8f4ff; border: 1px solid var(--primary); }
.dot.occupied { background: #eee; }
.dot.locked { background: #fff3e0; }
.dot.selected { background: var(--primary); }

.seat-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 6px;
  max-height: 200px;
  overflow-y: auto;
}
.seat {
  border: 1px solid var(--border);
  background: #e8f4ff;
  border-radius: 4px;
  padding: 6px 2px;
  font-size: 11px;
  cursor: pointer;
}
.seat.occupied, .seat.locked {
  background: #f5f5f5;
  color: #ccc;
  cursor: not-allowed;
}
.seat.active {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
}
</style>
