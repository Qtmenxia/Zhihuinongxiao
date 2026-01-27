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
      token.value = res.data.token
      localStorage.setItem('token', res.data.token)

      // 获取用户信息
      await fetchUserInfo()

      ElMessage.success('登录成功')
      return true
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
      return false
    }
  }

  // 获取用户信息
  async function fetchUserInfo() {
    try {
      const res = await getUserInfo()
      userInfo.value = {
        id: res.data.id,
        name: res.data.name,
        phone: res.data.phone,
        avatar: res.data.avatar || '',
        tier: res.data.tier,
        servicesCount: res.data.services_count,
        apiCallsToday: res.data.api_calls_today
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
