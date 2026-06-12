<template>
  <div class="route-map" :class="{ compact }">
    <svg viewBox="0 0 100 90" class="map-svg">
      <rect x="8" y="10" width="84" height="70" rx="6" fill="#e8f4ff" stroke="#b3d9ff" stroke-width="0.5" />
      <path
        v-for="(seg, i) in segments"
        :key="i"
        :d="seg.path"
        fill="none"
        :stroke="seg.active ? '#1677ff' : '#91caff'"
        :stroke-width="seg.active ? 1.2 : 0.8"
        stroke-dasharray="2 1"
        marker-end="url(#arrow)"
      />
      <g v-for="city in displayCities" :key="city.name">
        <circle
          :cx="city.x"
          :cy="city.y"
          r="2.8"
          :fill="city.isEndpoint ? '#1677ff' : '#52c41a'"
          stroke="#fff"
          stroke-width="0.6"
        />
        <text :x="city.x" :y="city.y - 4.5" text-anchor="middle" class="city-label">{{ city.name }}</text>
      </g>
      <defs>
        <marker id="arrow" markerWidth="4" markerHeight="4" refX="3" refY="2" orient="auto">
          <path d="M0,0 L4,2 L0,4 Z" fill="#1677ff" />
        </marker>
      </defs>
    </svg>
    <div v-if="routeText" class="route-text">{{ routeText }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CITY_COORDS } from '@/utils/travel'

const props = defineProps({
  cities: { type: Array, default: () => [] },
  legs: { type: Array, default: () => [] },
  compact: { type: Boolean, default: false },
})

const routeCities = computed(() => {
  if (props.cities.length) return props.cities
  if (!props.legs.length) return []
  const list = [props.legs[0].departure_city]
  props.legs.forEach(l => list.push(l.arrival_city))
  return list.filter((c, i, arr) => c && arr.indexOf(c) === i)
})

const displayCities = computed(() => {
  const names = routeCities.value
  return names.map((name, i) => {
    const coord = CITY_COORDS[name] || { x: 50 + i * 8, y: 45 }
    return {
      name,
      x: coord.x,
      y: coord.y,
      isEndpoint: i === 0 || i === names.length - 1,
    }
  })
})

const segments = computed(() => {
  const names = routeCities.value
  const segs = []
  for (let i = 0; i < names.length - 1; i++) {
    const a = CITY_COORDS[names[i]] || { x: 40, y: 40 }
    const b = CITY_COORDS[names[i + 1]] || { x: 60, y: 50 }
    const mx = (a.x + b.x) / 2
    const my = Math.min(a.y, b.y) - 8
    segs.push({
      active: true,
      path: `M ${a.x} ${a.y} Q ${mx} ${my} ${b.x} ${b.y}`,
    })
  }
  return segs
})

const routeText = computed(() => routeCities.value.join(' → '))
</script>

<style scoped>
.route-map {
  background: #fff;
  border-radius: 12px;
  padding: 12px;
  border: 1px solid var(--border);
}
.route-map.compact {
  padding: 8px;
}
.map-svg {
  width: 100%;
  height: auto;
  display: block;
}
.city-label {
  font-size: 3.2px;
  fill: #333;
  font-weight: 600;
}
.route-text {
  text-align: center;
  font-size: 13px;
  color: var(--primary);
  font-weight: 500;
  margin-top: 8px;
}
</style>
