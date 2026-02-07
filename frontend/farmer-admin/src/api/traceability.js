/**
 * 溯源管理 API
 */
import request from './request'

// 获取批次列表
export function getBatchList(params) {
  return request.get('/traceability/batches', { params })
}

// 获取溯源列表（别名）
export function getTraceList(params) {
  return request.get('/traceability/batches', { params })
}

// 获取批次详情
export function getBatchDetail(id) {
  return request.get(`/traceability/batches/${id}`)
}

// 创建批次
export function createBatch(data) {
  return request.post('/traceability/batches', data)
}

// 更新批次
export function updateBatch(id, data) {
  return request.put(`/traceability/batches/${id}`, data)
}

// 删除批次
export function deleteBatch(id) {
  return request.delete(`/traceability/batches/${id}`)
}

// 添加生产记录
export function addProductionRecord(batchId, data) {
  return request.post(`/traceability/batches/${batchId}/records`, data)
}

// 获取生产记录
export function getProductionRecords(batchId) {
  return request.get(`/traceability/batches/${batchId}/records`)
}

// 上传质检报告
export function uploadQualityReport(batchId, file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/traceability/batches/${batchId}/quality-report`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 生成溯源二维码
export function generateQRCode(batchId) {
  return request.get(`/traceability/batches/${batchId}/qrcode`)
}

// 获取溯源统计
export function getTraceabilityStats() {
  return request.get('/traceability/stats')
}

// 获取果园信息
export function getOrchardInfo() {
  return request.get('/traceability/orchards')
}

// 更新果园信息
export function updateOrchardInfo(id, data) {
  return request.put(`/traceability/orchards/${id}`, data)
}

// 获取扫码统计
export function getScanStats(params) {
  return request.get('/traceability/scan-stats', { params })
}

export default {
  getBatchList,
  getBatchDetail,
  createBatch,
  updateBatch,
  deleteBatch,
  addProductionRecord,
  getProductionRecords,
  uploadQualityReport,
  generateQRCode,
  getTraceabilityStats,
  getOrchardInfo,
  updateOrchardInfo,
  getScanStats
}
