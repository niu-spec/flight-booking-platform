import api from './index'

export const orderApi = {
  getList: () => api.get('/orders/'),
  getDetail: (id) => api.get(`/orders/${id}/`),
  create: (data) => api.post('/orders/create/', data),
  createRoundTrip: (data) => api.post('/orders/create-roundtrip/', data),
  cancel: (id) => api.post(`/orders/${id}/cancel/`),
  change: (id, data) => api.post(`/orders/${id}/change/`, data),
  refund: (id, data) => api.post(`/orders/${id}/refund/`, data),
  getTicket: (id) => api.get(`/orders/${id}/ticket/`),
  getShare: (id) => api.get(`/orders/${id}/share/`),
  createMultiLeg: (data) => api.post('/orders/create-multileg/', data),
}
