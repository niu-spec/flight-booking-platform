import api from './index'

export const adminApi = {
  getStats: () => api.get('/admin/stats/'),
  expireOrders: () => api.post('/admin/expire-orders/')
}
