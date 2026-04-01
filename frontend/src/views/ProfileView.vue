<template>
  <div class="profile">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>
      
      <el-form :model="form" :rules="rules" ref="profileFormRef" label-width="120px" style="max-width: 600px;">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" disabled />
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        
        <el-form-item label="手机号">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        
        <el-form-item label="账户余额">
          <el-input v-model="form.balance" disabled />
        </el-form-item>
        
        <el-form-item label="套餐类型">
          <el-input v-model="form.planType" disabled />
        </el-form-item>
        
        <el-form-item label="套餐到期时间">
          <el-input v-model="form.expireAt" disabled />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="updateProfile">更新信息</el-button>
          <el-button @click="changePasswordDialogVisible = true">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 修改密码对话框 -->
    <el-dialog v-model="changePasswordDialogVisible" title="修改密码" width="500px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmNewPassword">
          <el-input v-model="passwordForm.confirmNewPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="changePasswordDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="changePassword">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

export default {
  name: 'ProfileView',
  setup() {
    const userStore = useUserStore()
    
    const form = reactive({
      email: '',
      username: '',
      phone: '',
      balance: '0.00',
      planType: '免费版',
      expireAt: '2026-03-29'
    })
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度在3-20个字符之间', trigger: 'blur' }
      ]
    }
    
    const passwordForm = reactive({
      oldPassword: '',
      newPassword: '',
      confirmNewPassword: ''
    })
    
    const passwordRules = {
      oldPassword: [
        { required: true, message: '请输入原密码', trigger: 'blur' }
      ],
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
      ],
      confirmNewPassword: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        { validator: (rule, value, callback) => {
          if (value !== passwordForm.newPassword) {
            callback(new Error('两次输入的密码不一致'))
          } else {
            callback()
          }
        }, trigger: 'blur' }
      ]
    }
    
    const changePasswordDialogVisible = ref(false)
    
    // 模拟加载用户信息
    onMounted(() => {
      setTimeout(() => {
        form.email = userStore.currentUser?.email || 'user@example.com'
        form.username = userStore.currentUser?.username || '用户名'
        form.phone = userStore.currentUser?.phone || ''
        form.balance = '100.00'
        form.planType = '标准版套餐'
        form.expireAt = '2026-06-30'
      }, 500)
    })
    
    const updateProfile = () => {
      ElMessage.success('个人信息更新成功')
      // In real app, this would call the API to update user info
    }
    
    const changePassword = async () => {
      try {
        // In real app, this would call the API to change password
        ElMessage.success('密码修改成功')
        changePasswordDialogVisible.value = false
      } catch (error) {
        ElMessage.error('密码修改失败')
      }
    }
    
    return {
      form,
      rules,
      passwordForm,
      passwordRules,
      changePasswordDialogVisible,
      updateProfile,
      changePassword,
      profileFormRef: ref(null),
      passwordFormRef: ref(null)
    }
  }
}
</script>

<style scoped>
.profile {
  padding: 20px;
}

.profile-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
