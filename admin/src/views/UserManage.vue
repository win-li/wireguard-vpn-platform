<template>
  <div class="table-page">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
    </div>
    
    <!-- Filter Card -->
    <div class="filter-card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="搜索">
          <el-input
            v-model="searchKeyword"
            placeholder="邮箱/用户名"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="statusFilter" placeholder="全部" clearable>
            <el-option label="正常" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- Table Card -->
    <div class="table-card">
      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="balance" label="余额" width="100">
          <template #default="{ row }">
            ¥{{ row.balance?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="traffic_used" label="已用流量" width="120">
          <template #default="{ row }">
            {{ formatTraffic(row.traffic_used) }}
          </template>
        </el-table-column>
        <el-table-column prop="traffic_limit" label="流量限额" width="120">
          <template #default="{ row }">
            {{ formatTraffic(row.traffic_limit) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="expire_at" label="到期时间" width="160">
          <template #default="{ row }">
            {{ row.expire_at ? formatDate(row.expire_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDetail(row)">详情</el-button>
            <el-button
              :type="row.status === 'active' ? 'warning' : 'success'"
              link
              @click="toggleStatus(row)"
            >
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button type="primary" link @click="showBalanceDialog(row)">余额</el-button>
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
          @size-change="fetchUsers"
          @current-change="fetchUsers"
        />
      </div>
    </div>
    
    <!-- User Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="用户详情" width="500px">
      <div class="user-detail" v-if="currentUser">
        <div class="detail-item">
          <span class="detail-label">ID:</span>
          <span class="detail-value">{{ currentUser.id }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">邮箱:</span>
          <span class="detail-value">{{ currentUser.email }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">用户名:</span>
          <span class="detail-value">{{ currentUser.username }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">余额:</span>
          <span class="detail-value">¥{{ currentUser.balance?.toFixed(2) || '0.00' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">已用流量:</span>
          <span class="detail-value">{{ formatTraffic(currentUser.traffic_used) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">流量限额:</span>
          <span class="detail-value">{{ formatTraffic(currentUser.traffic_limit) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">状态:</span>
          <span class="detail-value">
            <el-tag :type="currentUser.status === 'active' ? 'success' : 'danger'">
              {{ currentUser.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">到期时间:</span>
          <span class="detail-value">{{ currentUser.expire_at ? formatDate(currentUser.expire_at) : '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">注册时间:</span>
          <span class="detail-value">{{ formatDate(currentUser.created_at) }}</span>
        </div>
      </div>
    </el-dialog>
    
    <!-- Balance Dialog -->
    <el-dialog v-model="balanceDialogVisible" title="修改余额" width="400px">
      <el-form :model="balanceForm" label-width="80px">
        <el-form-item label="当前余额">
          <span>¥{{ currentUser?.balance?.toFixed(2) || '0.00' }}</span>
        </el-form-item>
        <el-form-item label="调整类型">
          <el-radio-group v-model="balanceForm.type">
            <el-radio label="add">增加</el-radio>
            <el-radio label="subtract">扣除</el-radio>
            <el-radio label="set">设置</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="金额">
          <el-input-number v-model="balanceForm.amount" :min="0" :precision="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="balanceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="updateBalance">确定</el-button>
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
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const statusFilter = ref('')
const detailDialogVisible = ref(false)
const balanceDialogVisible = ref(false)
const currentUser = ref(null)

const balanceForm = reactive({
  type: 'add',
  amount: 0
})

const formatTraffic = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (statusFilter.value) params.status = statusFilter.value
    
    const response = await api.get('/admin/users', { params })
    users.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const resetFilters = () => {
  searchKeyword.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  fetchUsers()
}

const showDetail = (user) => {
  currentUser.value = user
  detailDialogVisible.value = true
}

const toggleStatus = async (user) => {
  const newStatus = user.status === 'active' ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm('确定要' + newStatus + '该用户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.put('/admin/users/' + user.id + '/status', {
      status: user.status === 'active' ? 'disabled' : 'active'
    })
    
    ElMessage.success(newStatus + '成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const showBalanceDialog = (user) => {
  currentUser.value = user
  balanceForm.type = 'add'
  balanceForm.amount = 0
  balanceDialogVisible.value = true
}

const updateBalance = async () => {
  try {
    await api.put('/admin/users/' + currentUser.value.id + '/balance', balanceForm)
    ElMessage.success('余额更新成功')
    balanceDialogVisible.value = false
    fetchUsers()
  } catch (error) {
    ElMessage.error('余额更新失败')
  }
}

onMounted(() => {
  fetchUsers()
})
</script>
