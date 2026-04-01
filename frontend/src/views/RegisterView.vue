<template>
  <el-card style="max-width:400px;margin:20px auto;padding:20px">
    <h2 style="text-align:center">注册</h2>
    <el-form :model="form" @submit.prevent="handleRegister">
      <el-form-item>
        <el-input v-model="form.email" placeholder="邮箱" size="large" type="email" />
      </el-form-item>
      <el-form-item>
        <el-input v-model="form.username" placeholder="用户名" size="large" />
      </el-form-item>
      <el-form-item>
        <el-input v-model="form.password" placeholder="密码" type="password" size="large" show-password />
      </el-form-item>
      <el-form-item>
        <el-input v-model="form.confirmPassword" placeholder="确认密码" type="password" size="large" show-password />
      </el-form-item>
      <el-form-item>
        <el-button 
          type="primary" 
          size="large" 
          style="width:100%" 
          @click="handleRegister" 
          :loading="loading"
        >注册</el-button>
      </el-form-item>
    </el-form>
    <div style="text-align:center;margin-top:10px">
      <el-link type="primary" @click="goLogin">已有账号？去登录</el-link>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const form = ref({ 
  email: '', 
  username: '', 
  password: '', 
  confirmPassword: '' 
})

const goLogin = () => router.push('/login')

const handleRegister = async () => {
  console.log('handleRegister called', form.value)
  
  if (!form.value.email) { 
    ElMessage.error('请输入邮箱'); 
    return 
  }
  if (!form.value.password) { 
    ElMessage.error('请输入密码'); 
    return 
  }
  if (form.value.password !== form.value.confirmPassword) { 
    ElMessage.error('两次密码不一致'); 
    return 
  }
  
  loading.value = true
  
  try {
    const response = await axios.post('/api/v1/users/users', {
      email: form.value.email,
      username: form.value.username || form.value.email.split('@')[0],
      password: form.value.password
    })
    console.log('Register response:', response.data)
    ElMessage.success('注册成功！')
    router.push('/login')
  } catch (e) {
    console.error('Register error:', e)
    ElMessage.error(e.response?.data?.detail || '注册失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@media (max-width: 480px) {
  .el-card {
    margin: 10px !important;
    max-width: 100% !important;
  }
}
</style>
