/**
 * 用户相关API
 */
import request from './request'

// 登录
export function login(data) {
  return request.post('/farmers/login', data)
}

// 注册
export function register(data) {
  return request.post('/farmers/register', data)
}

// 获取当前用户信息
export function getUserInfo() {
  return request.get('/farmers/me')
}

// 更新用户信息
export function updateUserInfo(data) {
  return request.put('/farmers/me', data)
}

// 修改密码
export function changePassword(data) {
  return request.post('/farmers/change-password', data)
}

// 登出
export function logout() {
  return request.post('/farmers/logout')
}

// 获取订阅配额
export function getQuota() {
  return request.get('/farmers/quota')
}
