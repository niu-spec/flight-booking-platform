import api from './index'

export const itineraryApi = {
  getList: () => api.get('/itineraries/'),
  
  getDetail: (id) => api.get(`/itineraries/${id}/`),
  
  refresh: (id) => api.post(`/itineraries/${id}/refresh/`)
}
