import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/AdminLogin.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/AdminDashboard.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/UserManage.vue')
      },
      {
        path: 'nodes',
        name: 'Nodes',
        component: () => import('@/views/NodeManage.vue')
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/OrderManage.vue')
      },
      {
        path: 'withdraw',
        name: 'Withdraw',
        component: () => import('@/views/WithdrawManage.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
