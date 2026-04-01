<template>
  <div class="table-page">
    <div class="page-header">
      <h2 class="page-title">提现审核</h2>
    </div>
    
    <!-- Filter Card -->
    <div class="filter-card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- Statistics -->
    <div class="stat-row">
      <div class="stat-item">
        <span class="stat-label">待审核:</span>
        <span class="stat-value pending">{{ stats.pending }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">今日提现:</span>
        <span class="stat-value">¥{{ stats.todayAmount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">本月提现:</span>
        <span class="stat-value">¥{{ stats.monthAmount }}</span>
      </div>
    </div>
    
    <!-- Table Card -->
    <div class="table-card">
      <el-table :data="withdrawals" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order_no" label="提现单号" width="180" />
        <el-table-column prop="user_email" label="用户邮箱" />
        <el-table-column prop="amount" label="提现金额" width="120">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="bank_name" label="银行" width="100" />
        <el-table-column prop="bank_account" label="银行卡号" width="160">
          <template #default="{ row }">
            {{ maskBankAccount(row.bank_account) }}
          </template>
        </el-table-column>
        <el-table-column prop="real_name" label="真实姓名" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDetail(row)">详情</el-button>
            <template v-if="row.status === 'pending'">
              <el-button type="success" link @click="approveWithdrawal(row)">通过</el-button>
              <el-button type="danger" link @click="rejectWithdrawal(row)">拒绝</el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchWithdrawals"
          @current-change="fetchWithdrawals"
        />
      </div>
    </div>
    
    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="提现详情" width="600px">
      <el-descriptions :column="2" border v-if="currentItem">
        <el-descriptions-item label="提现单号">{{ currentItem.order_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentItem.status)">
            {{ getStatusText(currentItem.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户邮箱">{{ currentItem.user_email }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ currentItem.user_id }}</el-descriptions-item>
        <el-descriptions-item label="提现金额">
          <span class="amount">¥{{ currentItem.amount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="银行名称">{{ currentItem.bank_name }}</el-descriptions-item>
        <el-descriptions-item label="银行卡号">{{ currentItem.bank_account }}</el-descriptions-item>
        <el-descriptions-item label="真实姓名">{{ currentItem.real_name }}</el-descriptions-item>
        <el-descriptions-item label="申请时间">
          {{ formatDate(currentItem.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="处理时间">
          {{ currentItem.processed_at ? formatDate(currentItem.processed_at) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentItem.remark || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="拒绝原因" :span="2" v-if="currentItem.reject_reason">
          {{ currentItem.reject_reason }}
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer v-if="currentItem?.status === 'pending'">
        <el-button @click="detailDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="rejectWithdrawal(currentItem)">拒绝</el-button>
        <el-button type="success" @click="approveWithdrawal(currentItem)">通过</el-button>
      </template>
    </el-dialog>
    
    <!-- Reject Dialog -->
    <el-dialog v-model="rejectDialogVisible" title="拒绝原因" width="400px">
      <el-form :model="rejectForm" label-width="80px">
        <el-form-item label="拒绝原因">
          <el-input
            v-model="rejectForm.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入拒绝原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)
const withdrawals = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref([])
const detailDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const currentItem = ref(null)

const filters = reactive({
  status: ''
})

const stats = reactive({
  pending: 0,
  todayAmount: 0,
  monthAmount: 0
})

const rejectForm = reactive({
  reason: ''
})

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝'
  }
  return texts[status] || status
}

const maskBankAccount = (account) => {
  if (!account || account.length < 8) return account
  return account.substring(0, 4) + '****' + account.substring(account.length - 4)
}

const fetchWithdrawals = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filters.status) params.status = filters.status
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await api.get('/admin/withdrawals', { params })
    withdrawals.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    ElMessage.error('获取提现列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const response = await api.get('/admin/withdrawals/stats')
    Object.assign(stats, response.data)
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchWithdrawals()
}

const resetFilters = () => {
  filters.status = ''
  dateRange.value = []
  currentPage.value = 1
  fetchWithdrawals()
}

const showDetail = (item) => {
  currentItem.value = item
  detailDialogVisible.value = true
}

const approveWithdrawal = async (item) => {
  try {
    await ElMessageBox.confirm('确定通过该提现申请吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.post('/admin/withdrawals/' + item.id + '/approve')
    ElMessage.success('已通过')
    detailDialogVisible.value = false
    fetchWithdrawals()
    fetchStats()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const rejectWithdrawal = (item) => {
  currentItem.value = item
  rejectForm.reason = ''
  rejectDialogVisible.value = true
}

const confirmReject = async () => {
  if (!rejectForm.reason.trim()) {
    ElMessage.warning('请输入拒绝原因')
    return
  }
  
  try {
    await api.post('/admin/withdrawals/' + currentItem.value.id + '/reject', {
      reason: rejectForm.reason
    })
    ElMessage.success('已拒绝')
    rejectDialogVisible.value = false
    detailDialogVisible.value = false
    fetchWithdrawals()
    fetchStats()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  fetchWithdrawals()
  fetchStats()
})
</script>

<style scoped>
.stat-row {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 15px 20px;
  background: #fff;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.stat-label {
  color: #909399;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.stat-value.pending {
  color: #E6A23C;
}

.amount {
  color: #f56c6c;
  font-weight: bold;
}
</style>
