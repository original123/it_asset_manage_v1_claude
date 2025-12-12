import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username, password) {
    const res = await authApi.login(username, password)
    console.log('Login response:', res)
    if (res.code === 0) {
      console.log('Token received:', res.data.access_token?.substring(0, 30))
      token.value = res.data.access_token
      user.value = res.data.user
      localStorage.setItem('token', res.data.access_token)
      console.log('Token stored:', localStorage.getItem('token')?.substring(0, 30))
      return true
    }
    throw new Error(res.message)
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (e) {
      console.error('Logout error:', e)
    }
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  async function fetchCurrentUser() {
    try {
      const res = await authApi.getMe()
      if (res.code === 0) {
        user.value = res.data
      }
    } catch (e) {
      logout()
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    fetchCurrentUser
  }
})
