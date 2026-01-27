/**
 * 客户管理 API
 */
import request from './request'

// 获取客户列表
export function getCustomerList(params) {
  return request.get('/customers', { params })
}

// 获取客户详情
export function getCustomerDetail(id) {
  return request.get(`/customers/${id}`)
}

// 获取客户统计
export function getCustomerStats() {
  return request.get('/customers/stats')
}

// 更新客户信息
export function updateCustomer(id, data) {
  return request.put(`/customers/${id}`, data)
}

// 更新客户等级
export function updateCustomerLevel(id, level) {
  return request.patch(`/customers/${id}/level`, { level })
}

// 添加客户备注
export function addCustomerRemark(id, remark) {
  return request.post(`/customers/${id}/remarks`, { remark })
}

// 获取客户订单历史
export function getCustomerOrders(id, params) {
  return request.get(`/customers/${id}/orders`, { params })
}

// 发送消息给客户
export function sendMessageToCustomer(id, message) {
  return request.post(`/customers/${id}/messages`, { message })
}

// 导出客户
export function exportCustomers(params) {
  return request.get('/customers/export', { params, responseType: 'blob' })
}

// 获取客户标签
export function getCustomerTags() {
  return request.get('/customers/tags')
}

// 给客户添加标签
export function addCustomerTag(id, tagId) {
  return request.post(`/customers/${id}/tags`, { tag_id: tagId })
}

export default {
  getCustomerList,
  getCustomerDetail,
  getCustomerStats,
  updateCustomer,
  updateCustomerLevel,
  addCustomerRemark,
  getCustomerOrders,
  sendMessageToCustomer,
  exportCustomers,
  getCustomerTags,
  addCustomerTag
}
