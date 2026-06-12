import api from './index'

export const paymentApi = {
  create: (orderId, data) => api.post(`/payments/create/${orderId}/`, data),
  getDetail: (id) => api.get(`/payments/${id}/`),
  getStatus: (id) => api.get(`/payments/${id}/status/`),
  createInvoice: (orderId, data) => api.post(`/payments/invoice/${orderId}/`, data),
  getInvoices: () => api.get('/payments/invoices/')
}
