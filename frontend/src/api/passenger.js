import api from './index'

export const passengerApi = {
  getList: () => api.get('/auth/passengers/'),
  create: (data) => api.post('/auth/passengers/', data),
  update: (id, data) => api.put(`/auth/passengers/${id}/`, data),
  remove: (id) => api.delete(`/auth/passengers/${id}/`)
}
