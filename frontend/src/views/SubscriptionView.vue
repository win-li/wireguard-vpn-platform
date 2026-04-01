<template>
  <div class="subscription-view">
    <!-- 当前订阅状态 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="status-card" v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>当前订阅</span>
              <el-button type="primary" size="small" @click="goToPlans" v-if="!activeSubscription">
                购买套餐
              </el-button>
            </div>
          </template>
          
          <div v-if="activeSubscription" class="subscription-info">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="info-item">
                  <div class="label">套餐名称</div>
                  <div class="value">{{ activeSubscription.plan_name }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="info-item">
                  <div class="label">订阅状态</div>
                  <div class="value">
                    <el-tag :type="getStatusType(activeSubscription.status)">
                      {{ getStatusText(activeSubscription.status) }}
                    </el-tag>
                  </div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="info-item">
                  <div class="label">剩余天数</div>
                  <div class="value">{{ activeSubscription.days_remaining }} 天</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="info-item">
                  <div class="label">到期时间</div>
                  <div class="value">{{ formatDate(activeSubscription.expire_at) }}</div>
                </div>
              </el-col>
            </el-row>
            
            <el-divider />
            
            <el-row :gutter="20">
              <el-col :span="12">
                <div class="progress-item">
                  <div class="progress-label">流量使用</div>
                  <el-progress 
                    :percentage="getBandwidthPercentage()" 
                    :format="formatProgress"
                    :stroke-width="20"
                  />
                  <div class="progress-text">
                    已用: {{ formatBytes(activeSubscription.bandwidth_used) }} / 
                    总量: {{ activeSubscription.bandwidth_limit ? formatBytes(activeSubscription.bandwidth_limit) : '不限' }}
                  </div>
                </div>
              </el-col>
              <el-col :span="12">
                <div class="auto-renew">
                  <div class="renew-label">自动续费</div>
                  <el-switch 
                    v-model="activeSubscription.auto_renew" 
                    @change="toggleAutoRenew"
                    :loading="renewLoading"
                  />
                </div>
                <el-button 
                  type="danger" 
                  plain 
                  style="margin-top: 20px;"
                  @click="showCancelDialog = true"
                >
                  取消订阅
                </el-button>
              </el-col>
            </el-row>
          </div>
          
          <el-empty v-else description="暂无活跃订阅">
            <el-button type="primary" @click="goToPlans">立即购买</el-button>
          </el-empty>
        </el-card>
      </el-col>
    </el-row>

    <!-- 订阅历史 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>订阅历史</span>
          </template>
          <el-table :data="subscriptionHistory" v-loading="loadingHistory">
            <el-table-column prop="plan_id" label="套餐ID" width="100" />
            <el-table-column prop="status" label="状态" width="120">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)" size="small">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="start_at" label="开始时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.start_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="expire_at" label="到期时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.expire_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="bandwidth_used" label="已用流量">
              <template #default="scope">
                {{ formatBytes(scope.row.bandwidth_used) }}
              </template>
            </el-table-column>
            <el-table-column prop="auto_renew" label="自动续费" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.auto_renew ? 'success' : 'info'" size="small">
                  {{ scope.row.auto_renew ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 取消订阅确认对话框 -->
    <el-dialog v-model="showCancelDialog" title="确认取消" width="400px">
      <p>确定要取消当前订阅吗？取消后将不再自动续费，但可继续使用至到期。</p>
      <template #footer>
        <el-button @click="showCancelDialog = false">保留订阅</el-button>
        <el-button type="danger" @click="confirmCancel" :loading="cancelLoading">
          确认取消
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const loadingHistory = ref(false)
const activeSubscription = ref(null)
const subscriptionHistory = ref([])
const showCancelDialog = ref(false)
const cancelLoading = ref(false)
const renewLoading = ref(false)

const fetchActiveSubscription = async () => {
  try {
    const response = await axios.get('/api/v1/subscriptions/me')
    activeSubscription.value = response.data
  } catch (error) {
    if (error.response?.status !== 404) {
      ElMessage.error('获取订阅信息失败')
    }
    activeSubscription.value = null
  } finally {
    loading.value = false
  }
}

const fetchHistory = async () => {
  loadingHistory.value = true
  try {
    const response = await axios.get('/api/v1/subscriptions/history')
    subscriptionHistory.value = response.data
  } catch (error) {
    console.error('获取历史失败', error)
  } finally {
    loadingHistory.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatBytes = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getStatusType = (status) => {
  const types = {
    active: 'success',
    expired: 'info',
    cancelled: 'warning',
    pending: 'warning'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    active: '活跃',
    expired: '已过期',
    cancelled: '已取消',
    pending: '待支付'
  }
  return texts[status] || status
}

const getBandwidthPercentage = () => {
  if (!activeSubscription.value) return 0
  if (!activeSubscription.value.bandwidth_limit) return 0
  const used = activeSubscription.value.bandwidth_used || 0
  const limit = activeSubscription.value.bandwidth_limit
  return Math.min(100, Math.round((used / limit) * 100))
}

const formatProgress = (percentage) => {
  return percentage + '%'
}

const goToPlans = () => {
  router.push('/plans')
}

const toggleAutoRenew = async (value) => {
  if (!activeSubscription.value) return
  
  renewLoading.value = true
  try {
    await axios.put(`/api/v1/subscriptions/${activeSubscription.value.id}/autorenew?auto_renew=${value}`)
    ElMessage.success(value ? '已开启自动续费' : '已关闭自动续费')
  } catch (error) {
    ElMessage.error('操作失败')
    activeSubscription.value.auto_renew = !value
  } finally {
    renewLoading.value = false
  }
}

const confirmCancel = async () => {
  if (!activeSubscription.value) return
  
  cancelLoading.value = true
  try {
    await axios.post(`/api/v1/subscriptions/${activeSubscription.value.id}/cancel`)
    ElMessage.success('订阅已取消')
    showCancelDialog.value = false
    await fetchActiveSubscription()
  } catch (error) {
    ElMessage.error('取消失败')
  } finally {
    cancelLoading.value = false
  }
}

onMounted(() => {
  fetchActiveSubscription()
  fetchHistory()
})
</script>

<style scoped>
.subscription-view {
  padding: 20px;
}

.status-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subscription-info {
  padding: 10px 0;
}

.info-item {
  text-align: center;
}

.info-item .label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.info-item .value {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.progress-item {
  padding: 10px 0;
}

.progress-label {
  margin-bottom: 10px;
  color: #606266;
}

.progress-text {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.auto-renew {
  text-align: center;
}

.renew-label {
  margin-bottom: 10px;
  color: #606266;
}
</style>
