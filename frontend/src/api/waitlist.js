import api from './index'

export const waitlistApi = {
  getList: () => api.get('/waitlist/'),
  create: (data) => api.post('/waitlist/', data),
  cancel: (id) => api.delete(`/waitlist/${id}/`),
}
