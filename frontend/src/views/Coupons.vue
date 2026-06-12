<template>
  <div class="page-container">
    <h1 class="page-title">优惠券</h1>
    <div class="page-card claim-box">
      <el-input v-model="claimCode" placeholder="输入优惠码领取" style="max-width: 240px" />
      <el-button type="primary" @click="handleClaim" :loading="claiming">领取</el-button>
    </div>
    <h2 style="font-size:18px;margin:24px 0 12px">我的优惠券</h2>
    <div class="coupon-grid" v-loading="loading">
      <div v-for="item in myCoupons" :key="item.id" class="coupon-card">
        <div class="coupon-value">
          <template v-if="item.coupon.discount_type === 'fixed'">¥{{ item.coupon.discount_value }}</template>
          <template v-else>{{ item.coupon.discount_value }}折</template>
        </div>
        <div class="coupon-info">
          <h3>{{ item.coupon.name }}</h3>
          <p>满 ¥{{ item.coupon.min_amount }} 可用 · 码：{{ item.coupon.code }}</p>
        </div>
      </div>
      <div v-if="!loading && !myCoupons.length" class="empty-state page-card" style="grid-column:1/-1">暂无优惠券，输入优惠码领取吧</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { couponApi } from '@/api/coupon'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const claiming = ref(false)
const claimCode = ref('')
const myCoupons = ref([])

const fetchList = async () => {
  loading.value = true
  try {
    const res = await couponApi.getMyCoupons()
    myCoupons.value = res.results || res
  } finally {
    loading.value = false
  }
}

const handleClaim = async () => {
  if (!claimCode.value) return
  claiming.value = true
  try {
    await couponApi.claim(claimCode.value)
    ElMessage.success('领取成功')
    claimCode.value = ''
    fetchList()
  } finally {
    claiming.value = false
  }
}

onMounted(fetchList)
</script>

<style scoped>
.claim-box { display: flex; gap: 12px; align-items: center; }
.coupon-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.coupon-card {
  background: linear-gradient(135deg, #fff5eb, #fff);
  border: 1px dashed var(--accent);
  border-radius: var(--radius);
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
}
.coupon-value { font-size: 28px; font-weight: 700; color: var(--accent); min-width: 70px; }
.coupon-info h3 { margin: 0 0 4px; font-size: 15px; }
.coupon-info p { margin: 0; font-size: 12px; color: var(--text-muted); }
</style>
