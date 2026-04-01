import api from './index'

// 创建USDT支付订单
export const createUSDT Payment = (data) => {
  return api.post('/payments/usdt/create', data)
}

// 检查USDT支付状态
export const checkUSDTStatus = (paymentId) => {
  return api.get(`/payments/usdt/${paymentId}/status`)
}

// 获取支付历史
export const getPaymentHistory = (skip = 0, limit = 20) => {
  return api.get(`/payments/history?skip=${skip}&limit=${limit}`)
}

// 获取支付详情
export const getPaymentDetail = (paymentId) => {
  return api.get(`/payments/${paymentId}`)
}

// 创建普通支付订单
export const createPayment = (data) => {
  return api.post('/payments/create', data)
}
