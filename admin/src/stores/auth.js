import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('admin_user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(email, password) {
    try {
      const response = await api.post('/auth/login', { email, password })
      const { access_token, user: userData } = response.data
      
      if (userData.role !== 'admin') {
        throw new Error('Admin access required')
      }

      token.value = access_token
      user.value = userData
      
      localStorage.setItem('admin_token', access_token)
      localStorage.setItem('admin_user', JSON.stringify(userData))
      
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || error.message }
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
  }

  return { token, user, isAuthenticated, login, logout }
})
