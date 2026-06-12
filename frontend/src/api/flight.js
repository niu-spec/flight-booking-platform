import api from './index'

export const flightApi = {
  getList: (params) => api.get('/flights/', { params }),
  
  getDetail: (id) => api.get(`/flights/${id}/`),
  
  search: (data) => api.post('/flights/search/', data),
  getSeats: (id) => api.get(`/flights/${id}/seats/`),
  getPriceCalendar: (params) => api.get('/flights/price-calendar/', { params }),
  updateStatus: (id, status) => api.post(`/flights/${id}/update-status/`, { status }),
  getReviews: (flightId) => api.get(`/flights/${flightId}/reviews/`),
  createReview: (data) => api.post('/flights/reviews/', data),
  searchTransfer: (data) => api.post('/flights/search-transfer/', data),
}
