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
export function getOrderStats(params) {
  return request.get('/orders/stats', { params })
}

// 订单发货
export function shipOrder(id, data) {
  return request.post(`/orders/${id}/ship`, data)
}

// 取消订单
export function cancelOrder(id, reason) {
  return request.post(`/orders/${id}/cancel`, { reason })
}

// 更新订单备注
export function updateOrderRemark(id, remark) {
  return request.patch(`/orders/${id}/remark`, { seller_remark: remark })
}

// 同意退款
export function approveRefund(id) {
  return request.post(`/orders/${id}/refund/approve`)
}

// 拒绝退款
export function rejectRefund(id, reason) {
  return request.post(`/orders/${id}/refund/reject`, { reason })
}

// 导出订单
export function exportOrders(params) {
  return request.get('/orders/export', { params, responseType: 'blob' })
}

// 获取物流信息
export function getLogistics(trackingNo, company) {
  return request.get('/logistics/track', { params: { tracking_no: trackingNo, company } })
}

// 批量发货
export function batchShip(orders) {
  return request.post('/orders/batch-ship', { orders })
}

export default {
  getOrderList,
  getOrderDetail,
  getOrderStats,
  shipOrder,
  cancelOrder,
  updateOrderRemark,
  approveRefund,
  rejectRefund,
  exportOrders,
  getLogistics,
  batchShip
}
