/**
 * 订单管理 API
 */
import request from './request'

// 获取订单列表
export function getOrderList(params) {
  return request.get('/orders', { params })
}

// 获取订单详情
export function getOrderDetail(id) {
  return request.get(`/orders/${id}`)
}

// 获取订单统计
export function getOrderStats() {
  return request.get('/orders/statistics/summary')
}

// 订单发货
export function shipOrder(id, data) {
  return request.post(`/orders/${id}/ship`, null, { params: data })
}

// 取消订单
export function cancelOrder(id, reason) {
  return request.post(`/orders/${id}/cancel`, null, { params: { reason } })
}

// 更新订单状态
export function updateOrderStatus(id, data) {
  return request.put(`/orders/${id}/status`, data)
}

// 导出订单PDF
export function exportOrdersPDF(params) {
  return request.get('/orders/export/pdf', { 
    params, 
    responseType: 'blob' 
  })
}

export default {
  getOrderList,
  getOrderDetail,
  getOrderStats,
  shipOrder,
  cancelOrder,
  updateOrderStatus,
  exportOrdersPDF
}
