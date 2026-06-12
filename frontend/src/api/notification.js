import api from './index'

export const notificationApi = {
  getList: () => api.get('/notifications/'),
  read: (id) => api.post(`/notifications/${id}/read/`),
  readAll: () => api.post('/notifications/read-all/')
}
