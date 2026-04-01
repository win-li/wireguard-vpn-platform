import { defineStore } from 'pinia'
import axios from 'axios'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    currentUser: (state) => state.user,
  },
  
  actions: {
    async login(email, password) {
      try {
        const response = await axios.post('/api/v1/auth/login', {
          email,
          password
        })
        
        const { access_token, refresh_token, user } = response.data
        
        this.token = access_token
        this.refreshToken = refresh_token
        this.user = user
        
        localStorage.setItem('token', access_token)
        localStorage.setItem('refreshToken', refresh_token)
        
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + access_token
        
        return response.data
      } catch (error) {
        console.error('Login error:', error)
        throw error
      }
    },
    
    async register(userData) {
      try {
        const response = await axios.post('/api/v1/users/users', userData)
        return response.data
      } catch (error) {
        console.error('Register error:', error)
        throw error
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      this.refreshToken = null
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      delete axios.defaults.headers.common['Authorization']
    },
    
    async fetchUser() {
      if (!this.token) return
      
      try {
        const response = await axios.get('/api/v1/users/me')
        this.user = response.data
        return response.data
      } catch (error) {
        this.logout()
        throw error
      }
    }
  }
})
