export const CABIN_MAP = {
  economy: '经济舱',
  business: '商务舱',
  first: '头等舱'
}

export const ORDER_STATUS_MAP = {
  pending: { text: '待支付', type: 'warning' },
  paid: { text: '已支付', type: 'info' },
  ticketed: { text: '已出票', type: 'success' },
  cancelled: { text: '已取消', type: 'danger' },
  refunded: { text: '已退款', type: 'info' }
}

export const ITINERARY_STATUS_MAP = {
  upcoming: { text: '即将出行', type: 'info' },
  in_progress: { text: '行程中', type: 'warning' },
  completed: { text: '已完成', type: 'success' },
  cancelled: { text: '已取消', type: 'danger' }
}

export const HOT_CITIES = ['北京', '上海', '广州', '深圳', '成都', '杭州', '西安', '重庆']

/** 城市在中国地图简图上的坐标 (viewBox 0-100) */
export const CITY_COORDS = {
  北京: { x: 68, y: 32 },
  上海: { x: 82, y: 55 },
  广州: { x: 72, y: 78 },
  深圳: { x: 74, y: 82 },
  成都: { x: 42, y: 58 },
  杭州: { x: 80, y: 58 },
  西安: { x: 52, y: 48 },
  重庆: { x: 48, y: 62 },
}

export function extractRouteCities(legs) {
  if (!legs?.length) return []
  const cities = [legs[0].departure_city]
  legs.forEach(leg => cities.push(leg.arrival_city))
  return cities.filter((c, i, arr) => c && arr.indexOf(c) === i)
}

export function formatLayover(minutes) {
  if (!minutes) return ''
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h > 0 ? `中转 ${h}小时${m}分` : `中转 ${m}分钟`
}

export function formatDateTime(date) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function formatTime(date) {
  if (!date) return '--:--'
  return new Date(date).toLocaleString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function formatDate(date) {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short'
  })
}

export function calcDuration(departure, arrival) {
  if (!departure || !arrival) return ''
  const ms = new Date(arrival) - new Date(departure)
  const h = Math.floor(ms / 3600000)
  const m = Math.floor((ms % 3600000) / 60000)
  return h > 0 ? `${h}小时${m}分` : `${m}分钟`
}

export function getAirlineColor(airline) {
  const colors = ['#0086f6', '#00a870', '#7b61ff', '#ff7700', '#e74c3c', '#3498db']
  let hash = 0
  for (let i = 0; i < (airline || '').length; i++) {
    hash = airline.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}
