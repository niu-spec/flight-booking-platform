import api from './index'

export const coreApi = {
  getWeather: (city) => api.get('/weather/', { params: { city } }),
  getFlightAlerts: () => api.get('/flight-alerts/'),
  createFlightAlert: (flightId) => api.post('/flight-alerts/', { flight: flightId }),
  deleteFlightAlert: (id) => api.delete(`/flight-alerts/${id}/`),
}
