<template>
  <el-card class="login-card" style="max-width: 400px; margin: 100px auto; padding: 20px;">
    <h2 style="text-align: center; margin-bottom: 20px;">登录</h2>
    <el-form @submit.prevent="handleLogin" :model="form" :rules="rules" ref="loginFormRef">
      <el-form-item prop="email">
        <el-input 
          v-model="form.email" 
          placeholder="邮箱" 
          type="email"
          size="large"
        >
          <template #prefix>
            <el-icon><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item prop="password">
        <el-input 
          v-model="form.password" 
          placeholder="密码" 
          type="password"
          size="large"
        >
          <template #prefix>
            <el-icon><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
      
      <el-form-item>
        <el-button 
          type="primary" 
          size="large" 
          style="width: 100%; margin-top: 10px;" 
          @click="handleLogin"
        >
          登录
        </el-button>
      </el-form-item>
    </el-form>
    
    <div style="text-align: center; margin-top: 20px;">
      <span>还没有账户？</span>
      <el-link type="primary" @click="router.push('/register')">立即注册</el-link>
    </div>
  </el-card>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

export default {
  name: 'LoginView',
  components: {
    User,
    Lock
  },
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    const form = reactive({
      email: '',
      password: ''
    })
    
    const rules = {
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
      ]
    }
    
    const handleLogin = async () => {
      try {
        await userStore.login(form.email, form.password)
        ElMessage.success('登录成功')
        router.push('/dashboard')
      } catch (error) {
        ElMessage.error(error.message || '登录失败')
      }
    }
    
    return {
      form,
      rules,
      handleLogin,
      loginFormRef: ref(null)
    }
  }
}
</script>
