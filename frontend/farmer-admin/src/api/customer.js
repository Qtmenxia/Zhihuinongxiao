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
  return request.get('/customers/statistics/summary')
}

// 创建客户
export function createCustomer(data) {
  return request.post('/customers', data)
}

// 更新客户信息
export function updateCustomer(id, data) {
  return request.put(`/customers/${id}`, data)
}

// 删除客户
export function deleteCustomer(id) {
  return request.delete(`/customers/${id}`)
}

// 导出客户PDF
export function exportCustomersPDF(params) {
  return request.get('/customers/export/pdf', { 
    params, 
    responseType: 'blob' 
  })
}

export default {
  getCustomerList,
  getCustomerDetail,
  getCustomerStats,
  createCustomer,
  updateCustomer,
  deleteCustomer,
  exportCustomersPDF
}
