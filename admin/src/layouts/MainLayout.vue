<template>
  <div class="admin-layout">
    <div class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="logo">
        <el-icon><Monitor /></el-icon>
        <span v-show="!isCollapsed">VPN Admin</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        router
      >
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <template #title>数据概览</template>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        <el-menu-item index="/nodes">
          <el-icon><Connection /></el-icon>
          <template #title>节点管理</template>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><List /></el-icon>
          <template #title>订单管理</template>
        </el-menu-item>
        <el-menu-item index="/withdraw">
          <el-icon><Wallet /></el-icon>
          <template #title>提现审核</template>
        </el-menu-item>
      </el-menu>
    </div>
    
    <div class="main-container">
      <div class="header">
        <div class="header-left">
          <el-icon class="toggle-btn" @click="isCollapsed = !isCollapsed">
            <component :is="isCollapsed ? 'Expand' : 'Fold'" />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ authStore.user?.email || 'Admin' }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <div class="main-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserFilled } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapsed = ref(false)

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => {
  const titles = {
    '/': '数据概览',
    '/users': '用户管理',
    '/nodes': '节点管理',
    '/orders': '订单管理',
    '/withdraw': '提现审核'
  }
  return titles[route.path] || ''
})

const handleCommand = (command) => {
  switch (command) {
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        authStore.logout()
        router.push('/login')
      })
      break
    case 'password':
      // TODO: 修改密码对话框
      break
    case 'profile':
      // TODO: 个人信息对话框
      break
  }
}
</script>
