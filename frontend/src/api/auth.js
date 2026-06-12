import api from './index'

export const authApi = {
  login: (data) => api.post('/auth/login/', data),

  register: (data) => api.post('/auth/register/', data),

  logout: () => api.post('/auth/logout/', { silent: true }),

  getProfile: (config = {}) => api.get('/auth/profile/', config),

  updateProfile: (data) => {
    const { id, date_joined, is_staff, points, member_level, member_label, ...payload } = data
    return api.put('/auth/profile/', payload)
  },
}
