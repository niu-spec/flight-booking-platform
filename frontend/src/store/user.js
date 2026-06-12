import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isLoggedIn = computed(() => !!token.value)

  const login = async (credentials) => {
    const response = await authApi.login(credentials)
    user.value = response.user
    token.value = response.token
    localStorage.setItem('token', response.token)
    if (response.access) localStorage.setItem('access', response.access)
    if (response.refresh) localStorage.setItem('refresh', response.refresh)
    return response
  }

  const register = async (userData) => {
    const response = await authApi.register(userData)
    user.value = response.user
    token.value = response.token
    localStorage.setItem('token', response.token)
    if (response.access) localStorage.setItem('access', response.access)
    if (response.refresh) localStorage.setItem('refresh', response.refresh)
    return response
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      user.value = null
      token.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    }
  }

  const fetchProfile = async () => {
    if (!token.value) return null
    try {
      const response = await authApi.getProfile({ silent: true })
      user.value = response
      return response
    } catch {
      user.value = null
      token.value = null
      return null
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    login,
    register,
    logout,
    fetchProfile
  }
})
