<template>
  <header class="navbar" :class="{ scrolled: isScrolled }">
    <div class="navbar-inner">
      <router-link to="/" class="logo">
        <span class="logo-icon">✈</span>
        <span class="logo-text">机票预约</span>
      </router-link>

      <nav class="nav-links">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
        >
          {{ item.label }}
        </router-link>
      </nav>

      <div class="user-area">
        <template v-if="userStore.isLoggedIn">
          <router-link to="/messages" class="nav-icon-link">消息</router-link>
          <router-link to="/coupons" class="nav-icon-link">优惠券</router-link>
          <el-dropdown>
            <div class="user-badge" style="cursor:pointer">
              <span class="avatar">{{ avatarLetter }}</span>
              <span class="username">{{ userStore.user?.username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">个人中心</el-dropdown-item>
                <el-dropdown-item @click="router.push('/passengers')">常用乘机人</el-dropdown-item>
                <el-dropdown-item v-if="userStore.user?.is_staff" @click="router.push('/admin')">管理看板</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <router-link to="/login" class="auth-link">登录</router-link>
          <router-link to="/register" class="auth-btn">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const isScrolled = ref(false)

const navItems = [
  { path: '/', label: '首页' },
  { path: '/flights', label: '机票' },
  { path: '/orders', label: '订单' },
  { path: '/waitlist', label: '候补' },
  { path: '/itineraries', label: '行程' },
  { path: '/assistant', label: '助手' }
]

const avatarLetter = computed(() => {
  const name = userStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const isActive = (path) => {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 10
}

const handleLogout = async () => {
  await userStore.logout()
  router.push('/login')
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  if (userStore.token && !userStore.user) {
    userStore.fetchProfile()
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid transparent;
  transition: all 0.3s;
}

.navbar.scrolled {
  border-bottom-color: var(--border);
  box-shadow: var(--shadow-sm);
}

.navbar-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  height: var(--header-height);
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  flex-shrink: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #0086f6, #006fd6);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #fff;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
  letter-spacing: -0.5px;
}

.nav-links {
  display: flex;
  gap: 4px;
  flex: 1;
}

.nav-item {
  padding: 8px 18px;
  border-radius: 20px;
  font-size: 15px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s;
  font-weight: 500;
}

.nav-item:hover {
  color: var(--primary);
  background: var(--primary-light);
}

.nav-item.active {
  color: var(--primary);
  background: var(--primary-light);
  font-weight: 600;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #7b61ff);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.username {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.nav-icon-link {
  font-size: 13px;
  color: var(--text-secondary);
  padding: 6px 10px;
}
.nav-icon-link:hover { color: var(--primary); }

.auth-link {
  color: var(--text-secondary);
  font-size: 14px;
  padding: 6px 12px;
}

.auth-link:hover {
  color: var(--primary);
}

.auth-btn {
  background: var(--primary);
  color: #fff !important;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.auth-btn:hover {
  background: var(--primary-dark);
}

@media (max-width: 768px) {
  .nav-links {
    display: none;
  }

  .username {
    display: none;
  }
}
</style>
