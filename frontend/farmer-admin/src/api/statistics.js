/**
 * 统计分析API
 */
import request from '@/utils/request'

/**
 * 获取数据概览
 */
export function getStatisticsOverview() {
  return request({
    url: '/statistics/overview',
    method: 'get'
  })
}

/**
 * 获取销售趋势
 */
export function getSalesTrend(period = 'month') {
  return request({
    url: '/statistics/sales-trend',
    method: 'get',
    params: { period }
  })
}

/**
 * 获取订单状态分布
 */
export function getOrderStatusDistribution() {
  return request({
    url: '/statistics/order-status',
    method: 'get'
  })
}

/**
 * 获取产品销售排行
 */
export function getProductSalesRank(limit = 10) {
  return request({
    url: '/statistics/product-sales',
    method: 'get',
    params: { limit }
  })
}

/**
 * 获取客户地区分布
 */
export function getCustomerRegionDistribution() {
  return request({
    url: '/statistics/customer-region',
    method: 'get'
  })
}

/**
 * 获取实时数据
 */
export function getRealtimeData() {
  return request({
    url: '/statistics/realtime',
    method: 'get'
  })
}
