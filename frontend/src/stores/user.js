import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout, getProfile } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  async function loginAction(employeeId, password) {
    try {
      const response = await login(employeeId, password)
      if (response.code === 200) {
        token.value = response.data.access_token
        user.value = response.data.user
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('refresh_token', response.data.refresh_token)
        return true
      }
      return false
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  async function logoutAction() {
    try {
      await logout()
    } finally {
      token.value = ''
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
    }
  }

  async function fetchProfile() {
    try {
      const response = await getProfile()
      if (response.code === 200) {
        user.value = response.data
      }
    } catch (error) {
      console.error('Fetch profile error:', error)
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    loginAction,
    logoutAction,
    fetchProfile
  }
})
