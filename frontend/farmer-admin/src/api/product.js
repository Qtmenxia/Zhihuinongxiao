/**
 * 产品管理 API
 */
import request from './request'

// 获取产品列表
export function getProductList(params) {
  return request.get('/products', { params })
}

// 获取产品详情
export function getProductDetail(id) {
  return request.get(`/products/${id}`)
}

// 创建产品
export function createProduct(data) {
  return request.post('/products', data)
}

// 更新产品
export function updateProduct(id, data) {
  return request.put(`/products/${id}`, data)
}

// 删除产品
export function deleteProduct(id) {
  return request.delete(`/products/${id}`)
}

// 批量更新产品状态
export function batchUpdateStatus(ids, is_active) {
  return request.post('/products/batch-update', { ids, is_active })
}

// 批量删除产品
export function batchDeleteProducts(ids) {
  return request.post('/products/batch-delete', { ids })
}

// 导出产品
export function exportProducts(params) {
  return request.get('/products/export/pdf', { 
    params, 
    responseType: 'blob' 
  })
}

// 导入产品
export function importProducts(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/products/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 获取产品分类
export function getProductCategories() {
  return request.get('/products/categories')
}

export default {
  getProductList,
  getProductDetail,
  createProduct,
  updateProduct,
  deleteProduct,
  batchUpdateStatus,
  batchDeleteProducts,
  exportProducts,
  importProducts,
  getProductCategories
}
