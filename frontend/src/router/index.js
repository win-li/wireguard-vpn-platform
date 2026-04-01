import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import ProfileView from '../views/ProfileView.vue'
import ConnectionConfigView from '../views/ConnectionConfigView.vue'
import PlansView from '../views/PlansView.vue'
import SubscriptionView from '../views/SubscriptionView.vue'
import WelcomeView from '../views/WelcomeView.vue'
import CheckinView from '../views/CheckinView.vue'
import InviteView from '../views/InviteView.vue'
import PaymentView from '../views/PaymentView.vue'

const routes = [
  {
    path: '/',
    redirect: '/welcome'
  },
  {
    path: '/welcome',
    name: 'welcome',
    component: WelcomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/configs',
    name: 'configs',
    component: ConnectionConfigView,
    meta: { requiresAuth: true }
  },
  {
    path: '/plans',
    name: 'plans',
    component: PlansView
  },
  {
    path: '/subscription',
    name: 'subscription',
    component: SubscriptionView,
    meta: { requiresAuth: true }
  },
  {
    path: '/checkin',
    name: 'checkin',
    component: CheckinView,
    meta: { requiresAuth: true }
  },
  {
    path: '/invite',
    name: 'invite',
    component: InviteView,
    meta: { requiresAuth: true }
  },
  {
    path: '/payment',
    name: 'payment',
    component: PaymentView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
