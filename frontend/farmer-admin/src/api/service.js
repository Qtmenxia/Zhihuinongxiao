/**
 * AI服务生成相关API
 */
import request from './request'

// 生成MCP服务
export function generateService(data) {
  return request.post('/services/generate', data)
}

// 获取服务状态
export function getServiceStatus(serviceId) {
  return request.get(`/services/${serviceId}/status`)
}

// 获取服务详情
export function getServiceDetail(serviceId) {
  return request.get(`/services/${serviceId}`)
}

// 获取服务列表
export function getServiceList(params) {
  return request.get('/services', { params })
}

// 部署服务
export function deployService(serviceId, data = {}) {
  return request.post(`/services/${serviceId}/deploy`, data)
}

// 停止服务
export function stopService(serviceId) {
  return request.post(`/services/${serviceId}/stop`)
}

// 删除服务
export function deleteService(serviceId) {
  return request.delete(`/services/${serviceId}`)
}

// 调用服务工具
export function callServiceTool(serviceId, toolName, params) {
  return request.post(`/services/${serviceId}/call`, {
    tool_name: toolName,
    params
  })
}

// 获取服务日志
export function getServiceLogs(serviceId, params) {
  return request.get(`/services/${serviceId}/logs`, { params })
}

// 触发服务优化
export function optimizeService(serviceId) {
  return request.post(`/services/${serviceId}/optimize`)
}

// 预估生成成本
export function estimateCost(data) {
  return request.post('/services/estimate-cost', data)
}

/**
 * WebSocket连接管理
 */
export class ServiceWebSocket {
  constructor(serviceId, callbacks = {}) {
    this.serviceId = serviceId
    this.callbacks = callbacks
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    this.ws = new WebSocket(`${protocol}//${host}/ws/service/${this.serviceId}`)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.callbacks.onConnect?.()
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.handleMessage(data)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.callbacks.onDisconnect?.()
      this.attemptReconnect()
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.callbacks.onError?.(error)
    }
  }

  handleMessage(data) {
    switch (data.type) {
      case 'progress':
        this.callbacks.onProgress?.(data)
        break
      case 'completed':
        this.callbacks.onComplete?.(data.result)
        break
      case 'error':
        this.callbacks.onError?.(data.error)
        break
      case 'pong':
        // 心跳响应
        break
      default:
        console.log('Unknown message type:', data.type)
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
        this.connect()
      }, 2000 * this.reconnectAttempts)
    }
  }

  sendPing() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send('ping')
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}
