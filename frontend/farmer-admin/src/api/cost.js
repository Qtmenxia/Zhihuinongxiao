/**
 * 成本管理API
 */
import request from './request'

/**
 * 获取成本概览
 */
export function getCostOverview() {
  return request({
    url: '/costs/overview',
    method: 'get'
  })
}

/**
 * 获取成本趋势
 */
export function getCostTrend(period = 'month') {
  return request({
    url: '/costs/trend',
    method: 'get',
    params: { period }
  })
}

/**
 * 获取成本记录列表
 */
export function getCostRecords(params) {
  return request({
    url: '/costs/records',
    method: 'get',
    params
  })
}

/**
 * 创建成本记录
 */
export function createCostRecord(data) {
  return request({
    url: '/costs/records',
    method: 'post',
    data
  })
}

/**
 * 更新成本记录
 */
export function updateCostRecord(id, data) {
  return request({
    url: `/costs/records/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除成本记录
 */
export function deleteCostRecord(id) {
  return request({
    url: `/costs/records/${id}`,
    method: 'delete'
  })
}

/**
 * 导出成本记录
 */
export function exportCostRecords(params) {
  return request({
    url: '/costs/records/export',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

