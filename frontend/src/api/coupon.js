import api from './index'

export const couponApi = {
  getList: () => api.get('/orders/coupons/'),
  getMyCoupons: () => api.get('/orders/my-coupons/'),
  claim: (code) => api.post('/orders/claim-coupon/', { code })
}
