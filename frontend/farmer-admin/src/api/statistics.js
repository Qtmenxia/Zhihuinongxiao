/**
 * 数据统计 API
 */
import request from './request'

// 获取概览数据
export function getOverviewStats(params) {
  return request.get('/statistics/overview', { params })
}

// 获取销售趋势
export function getSalesTrend(params) {
  return request.get('/statistics/sales-trend', { params })
}

// 获取产品销量排行
export function getProductRanking(params) {
  return request.get('/statistics/product-ranking', { params })
}

// 获取订单来源分布
export function getOrderSourceDistribution(params) {
  return request.get('/statistics/order-source', { params })
}

// 获取客户统计
export function getCustomerStats(params) {
  return request.get('/statistics/customers', { params })
}

// 获取AI服务成本统计
export function getAICostStats(params) {
  return request.get('/statistics/ai-cost', { params })
}

// 获取AI服务成本明细
export function getAICostDetails(params) {
  return request.get('/statistics/ai-cost/details', { params })
}

// 获取模型使用分布
export function getModelUsageDistribution(params) {
  return request.get('/statistics/model-usage', { params })
}

// 导出统计报表
export function exportStatistics(type, params) {
  return request.get(`/statistics/export/${type}`, { params, responseType: 'blob' })
}

// 获取仪表盘数据
export function getDashboardData() {
  return request.get('/statistics/dashboard')
}

// 获取实时数据
export function getRealtimeData() {
  return request.get('/statistics/realtime')
}

export default {
  getOverviewStats,
  getSalesTrend,
  getProductRanking,
  getOrderSourceDistribution,
  getCustomerStats,
  getAICostStats,
  getAICostDetails,
  getModelUsageDistribution,
  exportStatistics,
  getDashboardData,
  getRealtimeData
}
