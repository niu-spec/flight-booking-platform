<template>
  <div class="flight-search">
    <div class="search-header">
      <div class="page-container">
        <FlightSearchBox
          compact
          :loading="loading"
          :initial="initialSearch"
          @search="handleSearch"
        />
      </div>
    </div>

    <div class="page-container results-area">
      <div class="results-toolbar page-card" v-if="lastParams.departure_city && lastParams.arrival_city && isOneWay">
        <div class="price-calendar">
          <button
            v-for="day in priceCalendar"
            :key="day.date"
            type="button"
            class="cal-day"
            :class="{ active: lastParams.departure_date === day.date }"
            @click="pickDate(day.date)"
          >
            <span class="cal-date">{{ day.date.slice(5) }}</span>
            <span class="cal-price">{{ day.min_price ? `¥${day.min_price}` : '-' }}</span>
          </button>
        </div>
      </div>

      <div class="results-header" v-if="hasResults">
        <div>
          <h2 class="page-title">{{ searchSummary }}</h2>
          <p class="page-subtitle">
            <template v-if="isRoundTrip">去程 {{ flights.length }} 个 · 返程 {{ returnFlights.length }} 个</template>
            <template v-else-if="isTransfer">共 {{ transferItineraries.length }} 条中转联程</template>
            <template v-else-if="isMultiCity">第一程 {{ flights.length }} 个 · 第二程 {{ leg2Flights.length }} 个</template>
            <template v-else>共找到 {{ flights.length }} 个航班</template>
          </p>
        </div>
        <div class="toolbar-actions">
          <el-checkbox v-if="isOneWay" v-model="showSoldOut" @change="handleSearch(lastParams)">显示售罄可候补</el-checkbox>
          <el-button v-if="userStore.isLoggedIn" plain @click="watchDialogVisible = true">🔔 降价提醒</el-button>
          <el-button v-if="compareIds.length >= 2" type="primary" plain @click="showCompare">对比航班 ({{ compareIds.length }})</el-button>
          <el-select v-model="sortBy" placeholder="排序" style="width: 140px" @change="handleSearch(lastParams)">
            <el-option label="时间从早到晚" value="time_asc" />
            <el-option label="时间从晚到早" value="time_desc" />
            <el-option label="价格从低到高" value="price_asc" />
            <el-option label="价格从高到低" value="price_desc" />
          </el-select>
        </div>
      </div>

      <div v-if="mapLegs.length" class="page-card map-panel">
        <h3 class="leg-title">航线地图</h3>
        <RouteMap :legs="mapLegs" />
      </div>

      <div v-if="isTransfer && selectedTransfer" class="roundtrip-bar page-card">
        <div class="bar-info">
          已选联程 ¥{{ selectedTransfer.total_price }} · {{ selectedTransfer.hub_city }} 中转
        </div>
        <el-button class="btn-accent" @click="openTransferBook">预订联程</el-button>
      </div>

      <div v-if="isMultiCity && (selectedLeg1 || selectedLeg2)" class="roundtrip-bar page-card">
        <div class="bar-info">
          <span v-if="selectedLeg1">第1程 {{ selectedLeg1.flight_no }}</span>
          <span v-if="selectedLeg1 && selectedLeg2"> + </span>
          <span v-if="selectedLeg2">第2程 {{ selectedLeg2.flight_no }}</span>
        </div>
        <el-button class="btn-accent" :disabled="!selectedLeg1 || !selectedLeg2" @click="openMultiCityBook">预订多程</el-button>
      </div>

      <div v-if="isRoundTrip && (selectedOutbound || selectedReturn)" class="roundtrip-bar page-card">
        <div class="bar-info">
          <span v-if="selectedOutbound">去程：{{ selectedOutbound.flight_no }} ¥{{ selectedOutbound.base_price }}</span>
          <span v-if="selectedOutbound && selectedReturn"> + </span>
          <span v-if="selectedReturn">返程：{{ selectedReturn.flight_no }} ¥{{ selectedReturn.base_price }}</span>
        </div>
        <el-button
          class="btn-accent"
          :disabled="!selectedOutbound || !selectedReturn"
          @click="openRoundTripBook"
        >
          预订往返
        </el-button>
      </div>

      <div v-loading="loading">
        <template v-if="isTransfer">
          <div class="transfer-list">
            <TransferItineraryCard
              v-for="(itin, idx) in transferItineraries"
              :key="idx"
              :itinerary="itin"
              :selected="selectedTransfer === itin"
              @select="selectedTransfer = $event"
            />
          </div>
        </template>
        <template v-else-if="isMultiCity">
          <h3 class="leg-title">第一程 {{ lastParams.departure_city }} → {{ lastParams.arrival_city }}</h3>
          <div class="flight-list">
            <FlightCard
              v-for="flight in flights"
              :key="'l1-' + flight.id"
              :flight="flight"
              select-mode
              :selected="selectedLeg1?.id === flight.id"
              @select="selectedLeg1 = $event"
            />
          </div>
          <h3 class="leg-title">第二程 {{ lastParams.arrival_city }} → {{ lastParams.leg2_arrival_city }}</h3>
          <div class="flight-list">
            <FlightCard
              v-for="flight in leg2Flights"
              :key="'l2-' + flight.id"
              :flight="flight"
              select-mode
              :selected="selectedLeg2?.id === flight.id"
              @select="selectedLeg2 = $event"
            />
          </div>
        </template>
        <template v-else-if="isRoundTrip">
          <h3 class="leg-title">选择去程航班</h3>
          <div class="flight-list">
            <FlightCard
              v-for="flight in flights"
              :key="'out-' + flight.id"
              :flight="flight"
              select-mode
              :selected="selectedOutbound?.id === flight.id"
              :compare-selected="compareIds.includes(flight.id)"
              :show-alert="userStore.isLoggedIn"
              :alert-subscribed="alertFlightIds.has(flight.id)"
              @select="selectOutbound"
              @compare-change="toggleCompare"
              @subscribe-alert="handleFlightAlert"
            />
          </div>
          <h3 class="leg-title">选择返程航班</h3>
          <div class="flight-list">
            <FlightCard
              v-for="flight in returnFlights"
              :key="'ret-' + flight.id"
              :flight="flight"
              select-mode
              :selected="selectedReturn?.id === flight.id"
              :compare-selected="compareIds.includes(flight.id)"
              :show-alert="userStore.isLoggedIn"
              :alert-subscribed="alertFlightIds.has(flight.id)"
              @select="selectReturn"
              @compare-change="toggleCompare"
              @subscribe-alert="handleFlightAlert"
            />
          </div>
        </template>
        <div v-else class="flight-list">
          <template v-if="flights.length">
            <FlightCard
              v-for="flight in flights"
              :key="flight.id"
              :flight="flight"
              :compare-selected="compareIds.includes(flight.id)"
              :show-alert="userStore.isLoggedIn"
              :alert-subscribed="alertFlightIds.has(flight.id)"
              :waitlist-mode="showSoldOut"
              @book="handleBook"
              @waitlist="handleWaitlist"
              @compare-change="toggleCompare"
              @subscribe-alert="handleFlightAlert"
            />
          </template>
        </div>
        <div v-if="!loading && !hasResults" class="empty-state page-card">
          <div class="empty-icon">✈</div>
          <p>暂无符合条件的航班</p>
          <p style="font-size: 13px; margin-top: 8px">试试调整搜索条件或选择其他日期</p>
        </div>
      </div>
    </div>

    <el-dialog v-model="waitlistDialogVisible" title="候补购票" width="440px">
      <p class="wl-hint">航班售罄后可加入候补，有余票时将自动为您生成订单</p>
      <div v-if="waitlistFlight" class="book-flight-summary">
        {{ waitlistFlight.airline }} {{ waitlistFlight.flight_no }}
        {{ waitlistFlight.departure_city }} → {{ waitlistFlight.arrival_city }}
      </div>
      <el-form :model="waitlistForm" label-position="top">
        <el-form-item label="乘客姓名">
          <el-input v-model="waitlistForm.passenger_name" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="waitlistForm.passenger_id_card" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="waitlistDialogVisible = false">取消</el-button>
        <el-button type="warning" :loading="submitting" @click="submitWaitlist">确认候补</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="dialogVisible"
      :title="bookDialogTitle"
      width="520px"
      class="book-dialog"
    >
      <div v-if="selectedFlight && !isRoundTripBook" class="book-flight-summary">
        <span class="summary-route">
          {{ selectedFlight.departure_city }} → {{ selectedFlight.arrival_city }}
        </span>
        <span class="summary-flight">{{ selectedFlight.airline }} {{ selectedFlight.flight_no }}</span>
      </div>
      <div v-if="isMultiLegBook && selectedTransfer" class="book-flight-summary round-summary">
        <div v-for="(leg, i) in selectedTransfer.legs" :key="leg.id">
          <span class="leg-tag">第{{ i + 1 }}程</span>
          {{ leg.departure_city }}→{{ leg.arrival_city }} {{ leg.flight_no }}
        </div>
      </div>
      <div v-if="isMultiLegBook && selectedLeg1 && selectedLeg2" class="book-flight-summary round-summary">
        <div><span class="leg-tag">第1程</span>{{ selectedLeg1.flight_no }} {{ selectedLeg1.departure_city }}→{{ selectedLeg1.arrival_city }}</div>
        <div><span class="leg-tag return">第2程</span>{{ selectedLeg2.flight_no }} {{ selectedLeg2.departure_city }}→{{ selectedLeg2.arrival_city }}</div>
      </div>
      <div v-if="isRoundTripBook" class="book-flight-summary round-summary">
        <div>
          <span class="leg-tag">去程</span>
          {{ selectedOutbound.departure_city }}→{{ selectedOutbound.arrival_city }}
          {{ selectedOutbound.flight_no }} ¥{{ selectedOutbound.base_price }}
        </div>
        <div>
          <span class="leg-tag return">返程</span>
          {{ selectedReturn.departure_city }}→{{ selectedReturn.arrival_city }}
          {{ selectedReturn.flight_no }} ¥{{ selectedReturn.base_price }}
        </div>
      </div>
      <el-form :model="bookForm" :rules="bookRules" ref="bookFormRef" label-position="top">
        <el-form-item label="舱位等级" prop="cabin_class">
          <el-radio-group v-model="bookForm.cabin_class" class="cabin-group">
            <el-radio-button label="economy">经济舱</el-radio-button>
            <el-radio-button label="business">商务舱 ×1.5</el-radio-button>
            <el-radio-button label="first">头等舱 ×2.5</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="isRoundTripBook" label="返程舱位">
          <el-radio-group v-model="bookForm.return_cabin_class" class="cabin-group">
            <el-radio-button label="economy">经济舱</el-radio-button>
            <el-radio-button label="business">商务舱</el-radio-button>
            <el-radio-button label="first">头等舱</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="常用乘机人" v-if="passengers.length">
          <el-select v-model="selectedPassenger" placeholder="快速选择" style="width:100%" @change="fillPassenger">
            <el-option v-for="p in passengers" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="乘客姓名" prop="passenger_name">
          <el-input v-model="bookForm.passenger_name" placeholder="与证件一致" size="large" />
        </el-form-item>
        <el-form-item label="身份证号" prop="passenger_id_card">
          <el-input v-model="bookForm.passenger_id_card" placeholder="18位身份证号码" size="large" />
        </el-form-item>
        <el-form-item v-if="!isRoundTripBook" label="选座">
          <SeatPicker v-model="bookForm.seat_number" :seats="seats" :loading="seatsLoading" />
        </el-form-item>
        <el-form-item v-if="isRoundTripBook" label="去程选座">
          <SeatPicker v-model="bookForm.seat_number" :seats="outboundSeats" :loading="seatsLoading" />
        </el-form-item>
        <el-form-item v-if="isRoundTripBook" label="返程选座">
          <SeatPicker v-model="bookForm.return_seat_number" :seats="returnSeats" :loading="seatsLoading" />
        </el-form-item>
        <el-form-item label="优惠券">
          <el-input v-model="bookForm.coupon_code" placeholder="输入优惠码，如 WELCOME50" />
        </el-form-item>
        <el-form-item label="增值服务">
          <el-checkbox v-model="bookForm.delay_insurance">延误险 ¥25/程（航班延误2小时以上赔付）</el-checkbox>
          <el-checkbox
            v-if="isRoundTripBook"
            v-model="bookForm.return_delay_insurance"
            style="display:block;margin-top:8px"
          >返程延误险 ¥25</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button class="btn-accent" @click="handleSubmitBook" :loading="submitting">
          确认预订
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="compareVisible" title="航班对比" width="90%" style="max-width:900px">
      <el-table :data="compareFlights" border>
        <el-table-column prop="flight_no" label="航班号" />
        <el-table-column prop="airline" label="航司" />
        <el-table-column label="航线">
          <template #default="{ row }">{{ row.departure_city }}→{{ row.arrival_city }}</template>
        </el-table-column>
        <el-table-column prop="base_price" label="价格">
          <template #default="{ row }">¥{{ row.base_price }}</template>
        </el-table-column>
        <el-table-column prop="carbon_kg" label="碳排放">
          <template #default="{ row }">{{ row.carbon_kg }}kg</template>
        </el-table-column>
        <el-table-column prop="available_seats" label="余票" />
        <el-table-column prop="recommend_tag" label="推荐标签" />
      </el-table>
    </el-dialog>

    <el-dialog v-model="watchDialogVisible" title="设置降价提醒" width="400px">
      <el-form label-width="80px">
        <el-form-item label="目标价">
          <el-input-number v-model="watchForm.target_price" :min="100" :step="50" />
        </el-form-item>
      </el-form>
      <p style="font-size:12px;color:#999">当 {{ lastParams.departure_city }}→{{ lastParams.arrival_city }} 航线最低价低于目标价时，将发送消息通知。</p>
      <template #footer>
        <el-button @click="watchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePriceWatch">订阅</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { flightApi } from '@/api/flight'
import { orderApi } from '@/api/order'
import { passengerApi } from '@/api/passenger'
import { innovationApi } from '@/api/innovation'
import { coreApi } from '@/api/core'
import { ElMessage } from 'element-plus'
import FlightSearchBox from '@/components/FlightSearchBox.vue'
import FlightCard from '@/components/FlightCard.vue'
import SeatPicker from '@/components/SeatPicker.vue'
import TransferItineraryCard from '@/components/TransferItineraryCard.vue'
import RouteMap from '@/components/RouteMap.vue'
import { waitlistApi } from '@/api/waitlist'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const submitting = ref(false)
const flights = ref([])
const returnFlights = ref([])
const leg2Flights = ref([])
const transferItineraries = ref([])
const selectedTransfer = ref(null)
const selectedLeg1 = ref(null)
const selectedLeg2 = ref(null)
const showSoldOut = ref(false)
const waitlistDialogVisible = ref(false)
const waitlistFlight = ref(null)
const waitlistForm = ref({ passenger_name: '', passenger_id_card: '' })
const dialogVisible = ref(false)
const bookFormRef = ref()
const selectedFlight = ref(null)
const selectedOutbound = ref(null)
const selectedReturn = ref(null)
const isRoundTripBook = ref(false)
const isMultiLegBook = ref(false)
const multiLegTripType = ref('transfer')
const lastParams = ref({})
const sortBy = ref('time_asc')
const priceCalendar = ref([])
const passengers = ref([])
const selectedPassenger = ref(null)
const seats = ref([])
const outboundSeats = ref([])
const returnSeats = ref([])
const seatsLoading = ref(false)
const compareIds = ref([])
const compareFlights = ref([])
const compareVisible = ref(false)
const watchDialogVisible = ref(false)
const watchForm = ref({ target_price: 500 })
const alertFlightIds = ref(new Set())
const alertMap = ref({})

const isRoundTrip = computed(() => lastParams.value.trip_type === 'round_trip')
const isTransfer = computed(() => lastParams.value.trip_type === 'transfer')
const isMultiCity = computed(() => lastParams.value.trip_type === 'multi_city')
const isOneWay = computed(() => !lastParams.value.trip_type || lastParams.value.trip_type === 'one_way')

const hasResults = computed(() => {
  if (isTransfer.value) return transferItineraries.value.length > 0
  if (isMultiCity.value) return flights.value.length > 0 || leg2Flights.value.length > 0
  if (isRoundTrip.value) return flights.value.length > 0 || returnFlights.value.length > 0
  return flights.value.length > 0
})

const mapLegs = computed(() => {
  if (selectedTransfer.value?.legs) return selectedTransfer.value.legs
  if (selectedLeg1.value && selectedLeg2.value) return [selectedLeg1.value, selectedLeg2.value]
  if (selectedOutbound.value && selectedReturn.value) return [selectedOutbound.value, selectedReturn.value]
  if (selectedFlight.value) return [selectedFlight.value]
  return []
})

const bookDialogTitle = computed(() => {
  if (isRoundTripBook.value) return '预订往返机票'
  if (isMultiLegBook.value) return isTransfer.value ? '预订中转联程' : '预订多程机票'
  return '填写乘客信息'
})

const initialSearch = computed(() => ({
  trip_type: route.query.trip_type || 'one_way',
  departure_city: route.query.departure_city || '',
  arrival_city: route.query.arrival_city || '',
  departure_date: route.query.departure_date || null,
  return_date: route.query.return_date || null,
  leg2_arrival_city: route.query.leg2_arrival_city || '',
  leg2_departure_date: route.query.leg2_departure_date || null,
}))

const searchSummary = computed(() => {
  const { departure_city, arrival_city, trip_type, leg2_arrival_city } = lastParams.value
  if (departure_city && arrival_city) {
    if (trip_type === 'round_trip') return `${departure_city} ⇄ ${arrival_city}（往返）`
    if (trip_type === 'transfer') return `${departure_city} → ${arrival_city}（中转）`
    if (trip_type === 'multi_city' && leg2_arrival_city) {
      return `${departure_city} → ${arrival_city} → ${leg2_arrival_city}（多程）`
    }
    return `${departure_city} → ${arrival_city}`
  }
  return '全部航班'
})

const bookForm = ref({
  cabin_class: 'economy',
  return_cabin_class: 'economy',
  passenger_name: '',
  passenger_id_card: '',
  seat_number: '',
  return_seat_number: '',
  coupon_code: '',
  delay_insurance: false,
  return_delay_insurance: false,
})

const bookRules = {
  cabin_class: [{ required: true, message: '请选择舱位', trigger: 'change' }],
  passenger_name: [{ required: true, message: '请输入乘客姓名', trigger: 'blur' }],
  passenger_id_card: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /^\d{17}[\dXx]$/, message: '身份证号格式不正确', trigger: 'blur' }
  ]
}

const loadAlerts = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await coreApi.getFlightAlerts()
    const list = res.results || res
    alertMap.value = {}
    const ids = new Set()
    list.forEach(a => {
      ids.add(a.flight)
      alertMap.value[a.flight] = a.id
    })
    alertFlightIds.value = ids
  } catch { /* ignore */ }
}

const handleFlightAlert = async (flight) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  if (alertFlightIds.value.has(flight.id)) {
    const alertId = alertMap.value[flight.id]
    await coreApi.deleteFlightAlert(alertId)
    alertFlightIds.value.delete(flight.id)
    delete alertMap.value[flight.id]
    ElMessage.success('已取消航班订阅')
    return
  }
  const res = await coreApi.createFlightAlert(flight.id)
  alertFlightIds.value.add(flight.id)
  alertMap.value[flight.id] = res.id
  ElMessage.success(`已订阅 ${flight.flight_no} 的延误/取消提醒`)
}

const loadCalendar = async (params) => {
  if (!params.departure_city || !params.arrival_city) return
  const res = await flightApi.getPriceCalendar({
    departure_city: params.departure_city,
    arrival_city: params.arrival_city,
    days: 7
  })
  priceCalendar.value = res.calendar || []
}

const pickDate = (date) => {
  handleSearch({ ...lastParams.value, departure_date: date })
}

const handleSearch = async (params) => {
  lastParams.value = { ...params, sort: sortBy.value }
  loading.value = true
  selectedOutbound.value = null
  selectedReturn.value = null
  selectedTransfer.value = null
  selectedLeg1.value = null
  selectedLeg2.value = null
  try {
    if (params.trip_type === 'transfer') {
      const res = await flightApi.searchTransfer({
        departure_city: params.departure_city,
        arrival_city: params.arrival_city,
        departure_date: params.departure_date,
      })
      transferItineraries.value = res.itineraries || []
      flights.value = []
      returnFlights.value = []
      leg2Flights.value = []
    } else if (params.trip_type === 'multi_city') {
      const [leg1Res, leg2Res] = await Promise.all([
        flightApi.getList({ ...lastParams.value }),
        flightApi.getList({
          departure_city: params.arrival_city,
          arrival_city: params.leg2_arrival_city,
          departure_date: params.leg2_departure_date,
          sort: sortBy.value,
        }),
      ])
      flights.value = leg1Res.results || leg1Res
      leg2Flights.value = leg2Res.results || leg2Res
      returnFlights.value = []
      transferItineraries.value = []
    } else {
      const query = { ...lastParams.value }
      if (showSoldOut.value && params.trip_type !== 'round_trip') {
        query.include_sold_out = true
      }
      const outboundRes = await flightApi.getList(query)
      flights.value = outboundRes.results || outboundRes
      transferItineraries.value = []
      leg2Flights.value = []
      if (params.trip_type === 'round_trip' && params.return_date) {
        const returnRes = await flightApi.getList({
          departure_city: params.arrival_city,
          arrival_city: params.departure_city,
          departure_date: params.return_date,
          sort: sortBy.value,
        })
        returnFlights.value = returnRes.results || returnRes
      } else {
        returnFlights.value = []
      }
      if (isOneWay.value) loadCalendar(params)
    }
    router.replace({ query: params })
  } finally {
    loading.value = false
  }
}

const selectOutbound = (flight) => { selectedOutbound.value = flight }
const selectReturn = (flight) => { selectedReturn.value = flight }

const fillPassenger = (id) => {
  const p = passengers.value.find(x => x.id === id)
  if (p) {
    bookForm.value.passenger_name = p.name
    bookForm.value.passenger_id_card = p.id_card
  }
}

const toggleCompare = (flight, selected) => {
  if (selected) {
    if (compareIds.value.length >= 3) {
      ElMessage.warning('最多对比3个航班')
      return
    }
    compareIds.value.push(flight.id)
  } else {
    compareIds.value = compareIds.value.filter(id => id !== flight.id)
  }
}

const showCompare = async () => {
  const res = await innovationApi.compareFlights(compareIds.value)
  compareFlights.value = res.flights || []
  compareVisible.value = true
}

const handlePriceWatch = async () => {
  if (!lastParams.value.departure_city || !lastParams.value.arrival_city) {
    ElMessage.warning('请先搜索航线')
    return
  }
  await innovationApi.createPriceWatch({
    departure_city: lastParams.value.departure_city,
    arrival_city: lastParams.value.arrival_city,
    target_price: watchForm.value.target_price
  })
  ElMessage.success('降价提醒已设置')
  watchDialogVisible.value = false
  await innovationApi.checkPriceWatches()
}

const resetBookForm = () => ({
  cabin_class: 'economy',
  return_cabin_class: 'economy',
  passenger_name: '',
  passenger_id_card: '',
  seat_number: '',
  return_seat_number: '',
  coupon_code: '',
  delay_insurance: false,
  return_delay_insurance: false,
})

const loadSeatsForBook = async () => {
  seatsLoading.value = true
  try {
    if (isRoundTripBook.value) {
      const [out, ret] = await Promise.all([
        flightApi.getSeats(selectedOutbound.value.id),
        flightApi.getSeats(selectedReturn.value.id),
      ])
      outboundSeats.value = out.seats || []
      returnSeats.value = ret.seats || []
    } else if (selectedFlight.value) {
      const res = await flightApi.getSeats(selectedFlight.value.id)
      seats.value = res.seats || []
    }
  } finally {
    seatsLoading.value = false
  }
}

const handleWaitlist = (flight) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  waitlistFlight.value = flight
  waitlistForm.value = { passenger_name: '', passenger_id_card: '' }
  waitlistDialogVisible.value = true
  passengerApi.getList().then(res => {
    const list = res.results || res
    if (list.length) {
      waitlistForm.value.passenger_name = list[0].name
      waitlistForm.value.passenger_id_card = list[0].id_card
    }
  })
}

const submitWaitlist = async () => {
  if (!waitlistForm.value.passenger_name || !waitlistForm.value.passenger_id_card) {
    ElMessage.warning('请填写乘客信息')
    return
  }
  submitting.value = true
  try {
    await waitlistApi.create({
      flight: waitlistFlight.value.id,
      passenger_name: waitlistForm.value.passenger_name,
      passenger_id_card: waitlistForm.value.passenger_id_card,
      cabin_class: 'economy',
    })
    ElMessage.success('候补登记成功，可在「候补」页面查看排队情况')
    waitlistDialogVisible.value = false
  } finally {
    submitting.value = false
  }
}

const openTransferBook = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再预订')
    router.push('/login')
    return
  }
  isRoundTripBook.value = false
  isMultiLegBook.value = true
  multiLegTripType.value = 'transfer'
  bookForm.value = resetBookForm()
  dialogVisible.value = true
  passengerApi.getList().then(res => { passengers.value = res.results || res })
}

const openMultiCityBook = () => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }
  isRoundTripBook.value = false
  isMultiLegBook.value = true
  multiLegTripType.value = 'multi_city'
  bookForm.value = resetBookForm()
  dialogVisible.value = true
  passengerApi.getList().then(res => { passengers.value = res.results || res })
}

const handleBook = (flight) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再预订')
    router.push('/login')
    return
  }
  isRoundTripBook.value = false
  isMultiLegBook.value = false
  selectedFlight.value = flight
  bookForm.value = resetBookForm()
  selectedPassenger.value = null
  dialogVisible.value = true
  loadSeatsForBook()
  passengerApi.getList().then(res => { passengers.value = res.results || res })
}

const openRoundTripBook = () => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录后再预订')
    router.push('/login')
    return
  }
  isRoundTripBook.value = true
  isMultiLegBook.value = false
  selectedFlight.value = null
  bookForm.value = resetBookForm()
  selectedPassenger.value = null
  dialogVisible.value = true
  loadSeatsForBook()
  passengerApi.getList().then(res => { passengers.value = res.results || res })
}

const handleSubmitBook = async () => {
  await bookFormRef.value.validate()
  submitting.value = true
  try {
    if (isMultiLegBook.value && selectedTransfer.value) {
      const response = await orderApi.createMultiLeg({
        flight_ids: selectedTransfer.value.legs.map(l => l.id),
        trip_type: 'transfer',
        passenger_name: bookForm.value.passenger_name,
        passenger_id_card: bookForm.value.passenger_id_card,
        cabin_class: bookForm.value.cabin_class,
        coupon_code: bookForm.value.coupon_code,
        delay_insurance_legs: [bookForm.value.delay_insurance, bookForm.value.return_delay_insurance],
      })
      ElMessage.success('联程订单创建成功')
      dialogVisible.value = false
      router.push(`/orders/${response.orders[0].id}`)
    } else if (isMultiLegBook.value && selectedLeg1.value && selectedLeg2.value) {
      const response = await orderApi.createMultiLeg({
        flight_ids: [selectedLeg1.value.id, selectedLeg2.value.id],
        trip_type: 'multi_city',
        passenger_name: bookForm.value.passenger_name,
        passenger_id_card: bookForm.value.passenger_id_card,
        cabin_class: bookForm.value.cabin_class,
        coupon_code: bookForm.value.coupon_code,
        delay_insurance_legs: [bookForm.value.delay_insurance, bookForm.value.return_delay_insurance],
      })
      ElMessage.success('多程订单创建成功')
      dialogVisible.value = false
      router.push(`/orders/${response.orders[0].id}`)
    } else if (isRoundTripBook.value) {
      const response = await orderApi.createRoundTrip({
        outbound_flight: selectedOutbound.value.id,
        return_flight: selectedReturn.value.id,
        cabin_class: bookForm.value.cabin_class,
        return_cabin_class: bookForm.value.return_cabin_class,
        seat_number: bookForm.value.seat_number,
        return_seat_number: bookForm.value.return_seat_number,
        passenger_name: bookForm.value.passenger_name,
        passenger_id_card: bookForm.value.passenger_id_card,
        coupon_code: bookForm.value.coupon_code,
        delay_insurance: bookForm.value.delay_insurance,
        return_delay_insurance: bookForm.value.return_delay_insurance,
      })
      ElMessage.success('往返订单创建成功')
      dialogVisible.value = false
      router.push(`/orders/${response.outbound.id}`)
    } else {
      const response = await orderApi.create({
        flight: selectedFlight.value.id,
        ...bookForm.value,
      })
      ElMessage.success('订单创建成功')
      dialogVisible.value = false
      router.push(`/orders/${response.id}`)
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  const params = {}
  if (route.query.trip_type) params.trip_type = route.query.trip_type
  if (route.query.departure_city) params.departure_city = route.query.departure_city
  if (route.query.arrival_city) params.arrival_city = route.query.arrival_city
  if (route.query.departure_date) params.departure_date = route.query.departure_date
  if (route.query.return_date) params.return_date = route.query.return_date
  if (route.query.leg2_arrival_city) params.leg2_arrival_city = route.query.leg2_arrival_city
  if (route.query.leg2_departure_date) params.leg2_departure_date = route.query.leg2_departure_date
  handleSearch(params)
  loadAlerts()
})
</script>

<style scoped>
.flight-search {
  min-height: calc(100vh - var(--header-height) - 120px);
}

.search-header {
  background: linear-gradient(180deg, #e8f4ff 0%, var(--bg-page) 100%);
  padding: 24px 0 8px;
}

.results-area {
  padding-top: 16px;
}

.results-toolbar { margin-bottom: 16px; padding: 16px; }
.price-calendar { display: flex; gap: 8px; overflow-x: auto; }
.cal-day {
  border: 1px solid var(--border); background: #fff; border-radius: 8px;
  padding: 8px 14px; cursor: pointer; text-align: center; min-width: 72px;
}
.cal-day.active { border-color: var(--primary); background: var(--primary-light); }
.cal-date { display: block; font-size: 13px; font-weight: 600; }
.cal-price { display: block; font-size: 12px; color: var(--accent); margin-top: 2px; }
.results-header {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}
.toolbar-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }

.leg-title {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 0 12px;
  color: var(--text-primary);
}

.map-panel { margin-bottom: 16px; padding: 16px 20px; }
.transfer-list { display: flex; flex-direction: column; gap: 16px; }
.wl-hint { font-size: 13px; color: var(--text-muted); margin-bottom: 12px; }

.roundtrip-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 14px 20px;
  background: var(--primary-light);
}

.bar-info { font-size: 14px; font-weight: 500; }

.flight-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 80px;
  margin-bottom: 24px;
}

.book-flight-summary {
  background: var(--primary-light);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.round-summary {
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.leg-tag {
  display: inline-block;
  background: var(--primary);
  color: #fff;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 6px;
}

.leg-tag.return { background: #52c41a; }

.summary-route {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary);
}

.summary-flight {
  font-size: 13px;
  color: var(--text-secondary);
}

.cabin-group {
  width: 100%;
}

.cabin-group :deep(.el-radio-button) {
  flex: 1;
}

.cabin-group :deep(.el-radio-button__inner) {
  width: 100%;
}
</style>
