<template>
  <div class="auth-page">
    <div class="auth-visual">
      <div class="visual-content">
        <div class="visual-icon">✈</div>
        <h1>加入机票预约</h1>
        <p>注册即享便捷预订体验</p>
        <div class="visual-stats">
          <div class="stat">
            <div class="stat-num">100+</div>
            <div class="stat-label">覆盖航线</div>
          </div>
          <div class="stat">
            <div class="stat-num">24h</div>
            <div class="stat-label">全天服务</div>
          </div>
          <div class="stat">
            <div class="stat-num">0元</div>
            <div class="stat-label">预订手续费</div>
          </div>
        </div>
      </div>
    </div>

    <div class="auth-form-side">
      <div class="auth-form-card">
        <h2>创建账号</h2>
        <p class="auth-hint">填写以下信息完成注册</p>
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large">
          <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" placeholder="设置用户名" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="11位手机号" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" placeholder="至少6位" show-password />
          </el-form-item>
          <el-form-item label="确认密码" prop="password_confirm">
            <el-input v-model="form.password_confirm" type="password" placeholder="再次输入密码" show-password />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleRegister" :loading="loading" class="submit-btn">
              注 册
            </el-button>
          </el-form-item>
        </el-form>
        <p class="auth-switch">
          已有账号？<router-link to="/login">立即登录</router-link>
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

const form = ref({
  username: '',
  phone: '',
  password: '',
  password_confirm: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.value.password) {
          callback(new Error('两次密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleRegister = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    await userStore.register(form.value)
    ElMessage.success('注册成功')
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
}

.visual-content {
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

.visual-stats {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.stat {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 16px 20px;
  min-width: 90px;
}

.stat-num {
  font-size: 22px;
  font-weight: 700;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
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

  .visual-stats {
    display: none;
  }
}
</style>
