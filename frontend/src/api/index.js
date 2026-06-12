import axios from 'axios'
import { ElMessage } from 'element-plus'

function resolveBaseURL() {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  const { hostname } = window.location
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return '/api'
  }
  return `http://${hostname}:8000/api`
}

const api = axios.create({
  baseURL: resolveBaseURL(),
  timeout: 15000
})

let lastErrorToast = 0

function showError(message) {
  const now = Date.now()
  if (now - lastErrorToast < 2000) return
  lastErrorToast = now
  ElMessage.error(message)
}

function formatError(error) {
  const status = error.response?.status
  const data = error.response?.data

  if (!error.response) {
    return '无法连接后端，请确认已启动：python manage.py runserver 0.0.0.0:8000'
  }
  if (status === 401 || status === 403) {
    return '登录已过期，请重新登录'
  }
  if (status === 500 && (!data || typeof data !== 'object' || !Object.keys(data).length)) {
    return '后端服务异常或未启动，请检查 8000 端口'
  }

  const message = data?.message
    || data?.error
    || data?.detail
    || (typeof data === 'object' ? Object.values(data)[0]?.[0] : null)

  return Array.isArray(message) ? message[0] : (message || error.message || '请求失败')
}

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    const access = localStorage.getItem('access')
    if (access) {
      config.headers.Authorization = `Bearer ${access}`
    } else if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => response.data,
  error => {
    if (!error.config?.silent) {
      showError(formatError(error))
    }

    if (error.response?.status === 401 || error.response?.status === 403) {
      localStorage.removeItem('token')
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    }

    return Promise.reject(error)
  }
)

export default api
