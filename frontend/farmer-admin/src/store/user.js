/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getUserInfo } from '@/api/user'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref({
    id: '',
    name: '',
    phone: '',
    avatar: '',
    tier: 'free',
    servicesCount: 0,
    apiCallsToday: 0
  })

  // 计算属性
  const isLoggedIn = computed(() => !!token.value)
  const isPremium = computed(() => ['basic', 'professional'].includes(userInfo.value.tier))

  // 登录
  async function doLogin(loginForm) {
    try {
      const res = await login(loginForm)

      console.log('后端登录返回数据:', res)

      // 获取 access_token
      const accessToken = res.access_token || res.token

      if (!accessToken) {
        throw new Error('登录响应中未找到 Token')
      }

      token.value = accessToken
      localStorage.setItem('token', accessToken)

      // 保存用户信息
      if (res.farmer) {
        userInfo.value = {
          id: res.farmer.id,
          name: res.farmer.name,
          phone: res.farmer.phone,
          avatar: res.farmer.avatar || '',
          tier: res.farmer.tier,
          servicesCount: res.farmer.services_count || 0,
          apiCallsToday: res.farmer.api_calls_today || 0
        }
      }

      ElMessage.success('登录成功')
      return true
    } catch (error) {
      console.error('登录出错:', error)
      ElMessage.error(error.response?.data?.detail || error.message || '登录失败')
      return false
    }
  }


  // 获取用户信息
  async function fetchUserInfo() {
    try {
      const res = await getUserInfo()
      // 处理响应数据，可能是 res 或 res.data
      const data = res.data || res
      userInfo.value = {
        id: data.id,
        name: data.name,
        phone: data.phone,
        avatar: data.avatar || '',
        tier: data.tier,
        servicesCount: data.services_count || 0,
        apiCallsToday: data.api_calls_today || 0
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error)
    }
  }

  // 登出
  async function doLogout() {
    try {
      await logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = ''
      userInfo.value = {
        id: '',
        name: '',
        phone: '',
        avatar: '',
        tier: 'free',
        servicesCount: 0,
        apiCallsToday: 0
      }
      localStorage.removeItem('token')
    }
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isPremium,
    login: doLogin,
    logout: doLogout,
    fetchUserInfo
  }
})
