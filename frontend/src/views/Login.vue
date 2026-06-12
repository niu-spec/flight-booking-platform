<template>
  <div class="auth-page">
    <div class="auth-visual">
      <div class="visual-content">
        <div class="visual-icon">✈</div>
        <h1>机票预约平台</h1>
        <p>低价机票 · 安心出行 · 智慧旅程</p>
        <div class="visual-features">
          <div class="vf-item">🔍 实时航班查询</div>
          <div class="vf-item">💳 安全快捷支付</div>
          <div class="vf-item">📱 行程全程追踪</div>
        </div>
      </div>
    </div>

    <div class="auth-form-side">
      <div class="auth-form-card">
        <h2>欢迎回来</h2>
        <p class="auth-hint">登录您的账号，继续预订旅程</p>
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleLogin" :loading="loading" class="submit-btn">
              登 录
            </el-button>
          </el-form-item>
        </el-form>
        <p class="auth-switch">
          还没有账号？<router-link to="/register">免费注册</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const form = ref({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.login(form.value)
    ElMessage.success('登录成功')
    router.push('/')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  min-height: calc(100vh - var(--header-height) - 120px);
}

.auth-visual {
  flex: 1;
  background: linear-gradient(135deg, #006fd6, #0086f6, #00b4d8);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.auth-visual::before {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  top: -100px;
  right: -100px;
}

.visual-content {
  position: relative;
  color: #fff;
  text-align: center;
  max-width: 400px;
}

.visual-icon {
  font-size: 56px;
  margin-bottom: 16px;
}

.visual-content h1 {
  margin: 0 0 12px;
  font-size: 32px;
  font-weight: 700;
}

.visual-content > p {
  margin: 0 0 32px;
  font-size: 16px;
  opacity: 0.85;
}

.visual-features {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.vf-item {
  background: rgba(255, 255, 255, 0.12);
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  backdrop-filter: blur(4px);
}

.auth-form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: var(--bg-page);
}

.auth-form-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 40px 36px;
  box-shadow: var(--shadow-md);
}

.auth-form-card h2 {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 700;
}

.auth-hint {
  margin: 0 0 28px;
  font-size: 14px;
  color: var(--text-muted);
}

.submit-btn {
  width: 100%;
  height: 44px !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  border-radius: 8px !important;
}

.auth-switch {
  text-align: center;
  margin: 20px 0 0;
  font-size: 14px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .auth-page {
    flex-direction: column;
  }

  .auth-visual {
    padding: 32px 20px;
  }

  .visual-features {
    display: none;
  }
}
</style>
