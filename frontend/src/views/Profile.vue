<template>
  <div class="page-container">
    <h1 class="page-title">个人中心</h1>

    <div class="member-card" v-if="form.points !== undefined">
      <div class="member-badge" :class="form.member_level">
        {{ levelIcon }} {{ form.member_label }}
      </div>
      <div class="member-points">
        <span class="points-num">{{ form.points }}</span>
        <span class="points-label">积分</span>
      </div>
      <div class="member-progress">
        <el-progress :percentage="levelProgress" :format="() => nextLevelText" />
      </div>
    </div>

    <div class="page-card" v-loading="loading" style="margin-top:20px">
      <el-form :model="form" label-width="80px" style="max-width: 480px">
        <el-form-item label="用户名"><el-input v-model="form.username" disabled /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="姓名"><el-input v-model="form.first_name" placeholder="真实姓名" /></el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSave" :loading="saving">保存修改</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { authApi } from '@/api/auth'
import { useUserStore } from '@/store/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const form = ref({ username: '', phone: '', email: '', first_name: '', points: 0, member_level: 'normal', member_label: '' })

const levelIcon = computed(() => ({
  normal: '🌟', silver: '🥈', gold: '🥇'
})[form.value.member_level] || '🌟')

const levelProgress = computed(() => {
  const p = form.value.points || 0
  if (p >= 5000) return 100
  if (p >= 2000) return Math.round(((p - 2000) / 3000) * 100)
  return Math.round((p / 2000) * 100)
})

const nextLevelText = computed(() => {
  const p = form.value.points || 0
  if (p >= 5000) return '已满级'
  if (p >= 2000) return `距金卡 ${5000 - p} 分`
  return `距银卡 ${2000 - p} 分`
})

const fetchProfile = async () => {
  loading.value = true
  try {
    const data = userStore.user || await userStore.fetchProfile()
    if (data) form.value = { ...form.value, ...data }
    else router.push('/login')
  } finally {
    loading.value = false
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    const data = await authApi.updateProfile(form.value)
    userStore.user = data
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.member-card {
  background: linear-gradient(135deg, #006fd6, #0086f6);
  border-radius: 16px;
  padding: 28px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 32px;
  flex-wrap: wrap;
}
.member-badge {
  font-size: 18px;
  font-weight: 700;
  padding: 8px 16px;
  background: rgba(255,255,255,0.15);
  border-radius: 20px;
}
.member-badge.gold { background: linear-gradient(135deg, #ffd700, #ffb300); color: #333; }
.member-badge.silver { background: linear-gradient(135deg, #c0c0c0, #a8a8a8); color: #333; }
.member-points { text-align: center; }
.points-num { font-size: 36px; font-weight: 700; display: block; }
.points-label { font-size: 13px; opacity: 0.8; }
.member-progress { flex: 1; min-width: 200px; }
.member-progress :deep(.el-progress__text) { color: #fff !important; font-size: 12px !important; }
</style>
