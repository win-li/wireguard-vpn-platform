<template>
  <div class="plans-view">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="header-card">
          <div class="page-header">
            <h2>套餐选择</h2>
            <p>选择适合您的套餐，享受高速稳定的VPN服务</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;" v-loading="loading">
      <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="plan in plans" :key="plan.id">
        <el-card class="plan-card" :class="{ 'recommended': plan.sort_order === 1 }">
          <div class="plan-header">
            <h3>{{ plan.name }}</h3>
            <div class="price">
              <span class="currency">¥</span>
              <span class="amount">{{ plan.price }}</span>
            </div>
            <div class="duration">{{ plan.duration_days }} 天</div>
          </div>
          <el-divider />
          <div class="plan-features">
            <div class="feature">
              <el-icon><Check /></el-icon>
              <span>流量: {{ plan.bandwidth_limit ? formatBytes(plan.bandwidth_limit) : '不限' }}</span>
            </div>
            <div class="feature">
              <el-icon><Check /></el-icon>
              <span>设备数: {{ plan.device_limit }} 台</span>
            </div>
            <div class="feature" v-if="plan.description">
              <el-icon><Check /></el-icon>
              <span>{{ plan.description }}</span>
            </div>
          </div>
          <el-button 
            type="primary" 
            size="large" 
            style="width: 100%; margin-top: 20px;"
            @click="selectPlan(plan)"
          >
            立即购买
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 购买确认对话框 -->
    <el-dialog v-model="showPurchaseDialog" title="确认购买" width="400px">
      <div v-if="selectedPlan" class="purchase-info">
        <p><strong>套餐:</strong> {{ selectedPlan.name }}</p>
        <p><strong>价格:</strong> ¥{{ selectedPlan.price }}</p>
        <p><strong>有效期:</strong> {{ selectedPlan.duration_days }} 天</p>
      </div>
      <template #footer>
        <el-button @click="showPurchaseDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmPurchase" :loading="purchasing">
          确认购买
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

const plans = ref([])
const loading = ref(true)
const showPurchaseDialog = ref(false)
const selectedPlan = ref(null)
const purchasing = ref(false)

const fetchPlans = async () => {
  try {
    const response = await axios.get('/api/v1/plans/active')
    plans.value = response.data
  } catch (error) {
    ElMessage.error('获取套餐列表失败')
  } finally {
    loading.value = false
  }
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const selectPlan = (plan) => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  selectedPlan.value = plan
  showPurchaseDialog.value = true
}

const confirmPurchase = async () => {
  if (!selectedPlan.value) return
  
  purchasing.value = true
  try {
    const response = await axios.post('/api/v1/subscriptions/purchase', {
      plan_id: selectedPlan.value.id,
      user_id: userStore.user.id,
      auto_renew: false
    })
    
    ElMessage.success('购买成功！')
    showPurchaseDialog.value = false
    
    // 跳转到支付页面或订阅管理
    router.push('/subscription')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '购买失败')
  } finally {
    purchasing.value = false
  }
}

onMounted(() => {
  fetchPlans()
})
</script>

<style scoped>
.plans-view {
  padding: 20px;
}

.header-card {
  text-align: center;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.page-header p {
  margin: 10px 0 0;
  color: #909399;
}

.plan-card {
  margin-bottom: 20px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.plan-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.plan-card.recommended {
  border: 2px solid #409EFF;
}

.plan-header {
  text-align: center;
}

.plan-header h3 {
  margin: 0;
  color: #303133;
}

.price {
  margin: 15px 0;
}

.currency {
  font-size: 20px;
  color: #409EFF;
}

.amount {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
}

.duration {
  color: #909399;
  font-size: 14px;
}

.plan-features {
  min-height: 120px;
}

.feature {
  display: flex;
  align-items: center;
  margin: 10px 0;
  color: #606266;
}

.feature .el-icon {
  margin-right: 8px;
  color: #67C23A;
}

.purchase-info p {
  margin: 10px 0;
}
</style>
