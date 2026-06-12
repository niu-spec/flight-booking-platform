import api from './index'

export const innovationApi = {
  chat: (message, history = []) => api.post('/chat/', { message, history }),
  compareFlights: (flightIds) => api.post('/flights/compare/', { flight_ids: flightIds }),
  getPriceWatches: () => api.get('/price-watches/'),
  createPriceWatch: (data) => api.post('/price-watches/', data),
  deletePriceWatch: (id) => api.delete(`/price-watches/${id}/`),
  checkPriceWatches: () => api.post('/price-watches/check/'),
  getChecklists: () => api.get('/checklists/'),
  getChecklist: (itineraryId) => api.get(`/checklists/${itineraryId}/`),
  updateChecklist: (itineraryId, items) => api.patch(`/checklists/${itineraryId}/`, { items })
}
