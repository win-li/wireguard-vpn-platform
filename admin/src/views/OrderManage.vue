<template>
  <div class="table-page">
    <div class="page-header">
      <h2 class="page-title">订单管理</h2>
    </div>
    
    <!-- Filter Card -->
    <div class="filter-card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="订单号">
          <el-input v-model="filters.order_no" placeholder="搜索订单号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="失败" value="failed" />
            <el-option label="已退款" value="refunded" />
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
    
    <!-- Table Card -->
    <div class="table-card">
      <el-table :data="orders" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="user_email" label="用户邮箱" />
        <el-table-column prop="plan_name" label="套餐" width="120" />
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">
            <span class="amount">¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">
            {{ getPaymentMethodText(row.payment_method) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="支付时间" width="160">
          <template #default="{ row }">
            {{ row.paid_at ? formatDate(row.paid_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showDetail(row)">详情</el-button>
            <el-button
              v-if="row.status === 'paid'"
              type="warning"
              link
              @click="showRefundDialog(row)"
            >
              退款
            </el-button>
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
          @size-change="fetchOrders"
          @current-change="fetchOrders"
        />
      </div>
    </div>
    
    <!-- Order Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="600px">
      <el-descriptions :column="2" border v-if="currentOrder">
        <el-descriptions-item label="订单号">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentOrder.status)">
            {{ getStatusText(currentOrder.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户邮箱">{{ currentOrder.user_email }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ currentOrder.user_id }}</el-descriptions-item>
        <el-descriptions-item label="套餐名称">{{ currentOrder.plan_name }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">
          <span class="amount">¥{{ currentOrder.amount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="支付方式">
          {{ getPaymentMethodText(currentOrder.payment_method) }}
        </el-descriptions-item>
        <el-descriptions-item label="支付金额">
          <span v-if="currentOrder.paid_amount">¥{{ currentOrder.paid_amount }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(currentOrder.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="支付时间">
          {{ currentOrder.paid_at ? formatDate(currentOrder.paid_at) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="交易号" :span="2">
          {{ currentOrder.transaction_id || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentOrder.remark || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
    
    <!-- Refund Dialog -->
    <el-dialog v-model="refundDialogVisible" title="订单退款" width="400px">
      <el-form :model="refundForm" label-width="80px">
        <el-form-item label="订单号">
          <span>{{ currentOrder?.order_no }}</span>
        </el-form-item>
        <el-form-item label="订单金额">
          <span>¥{{ currentOrder?.amount }}</span>
        </el-form-item>
        <el-form-item label="退款原因">
          <el-input
            v-model="refundForm.reason"
            type="textarea"
            :rows="3"
            placeholder="请输入退款原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="refundDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="processRefund">确认退款</el-button>
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
const orders = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dateRange = ref([])
const detailDialogVisible = ref(false)
const refundDialogVisible = ref(false)
const currentOrder = ref(null)

const filters = reactive({
  order_no: '',
  status: ''
})

const refundForm = reactive({
  reason: ''
})

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    paid: 'success',
    failed: 'danger',
    refunded: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待支付',
    paid: '已支付',
    failed: '失败',
    refunded: '已退款'
  }
  return texts[status] || status
}

const getPaymentMethodText = (method) => {
  const texts = {
    alipay: '支付宝',
    wechat: '微信支付',
    balance: '余额支付'
  }
  return texts[method] || method
}

const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filters.order_no) params.order_no = filters.order_no
    if (filters.status) params.status = filters.status
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const response = await api.get('/admin/orders', { params })
    orders.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchOrders()
}

const resetFilters = () => {
  filters.order_no = ''
  filters.status = ''
  dateRange.value = []
  currentPage.value = 1
  fetchOrders()
}

const showDetail = (order) => {
  currentOrder.value = order
  detailDialogVisible.value = true
}

const showRefundDialog = (order) => {
  currentOrder.value = order
  refundForm.reason = ''
  refundDialogVisible.value = true
}

const processRefund = async () => {
  try {
    await ElMessageBox.confirm('确定要对该订单进行退款吗？此操作不可撤销。', '警告', {
      confirmButtonText: '确定退款',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.post('/admin/orders/' + currentOrder.value.id + '/refund', refundForm)
    ElMessage.success('退款成功')
    refundDialogVisible.value = false
    fetchOrders()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退款失败')
    }
  }
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.amount {
  color: #f56c6c;
  font-weight: bold;
}
</style>
