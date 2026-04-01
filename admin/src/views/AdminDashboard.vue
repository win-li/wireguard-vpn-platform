<template>
  <div class="dashboard">
    <!-- Statistics Cards -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon users">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-title">用户总数</div>
          <div class="stat-value">{{ stats.totalUsers }}</div>
          <div class="stat-trend up" v-if="stats.userGrowth > 0">
            <el-icon><Top /></el-icon>
            较上月增长 {{ stats.userGrowth }}%
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon income">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-title">本月收入</div>
          <div class="stat-value">¥{{ stats.monthlyIncome }}</div>
          <div class="stat-trend up" v-if="stats.incomeGrowth > 0">
            <el-icon><Top /></el-icon>
            较上月增长 {{ stats.incomeGrowth }}%
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon traffic">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-title">今日流量</div>
          <div class="stat-value">{{ formatTraffic(stats.todayTraffic) }}</div>
          <div class="stat-trend up" v-if="stats.trafficGrowth > 0">
            <el-icon><Top /></el-icon>
            较昨日增长 {{ stats.trafficGrowth }}%
          </div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon orders">
          <el-icon><List /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-title">本月订单</div>
          <div class="stat-value">{{ stats.monthlyOrders }}</div>
          <div class="stat-trend up" v-if="stats.orderGrowth > 0">
            <el-icon><Top /></el-icon>
            较上月增长 {{ stats.orderGrowth }}%
          </div>
        </div>
      </div>
    </div>
    
    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">用户增长趋势</div>
        <div class="chart-container" ref="userChartRef"></div>
      </div>
      
      <div class="chart-card">
        <div class="chart-title">收入趋势</div>
        <div class="chart-container" ref="incomeChartRef"></div>
      </div>
    </div>
    
    <!-- Data Tables Row -->
    <div class="data-row">
      <div class="data-card">
        <div class="card-header">
          <span class="card-title">最近注册用户</span>
          <el-button type="primary" link @click="$router.push('/users')">
            查看全部
          </el-button>
        </div>
        <el-table :data="recentUsers" style="width: 100%">
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="created_at" label="注册时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
                {{ row.status === 'active' ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div class="data-card">
        <div class="card-header">
          <span class="card-title">最近订单</span>
          <el-button type="primary" link @click="$router.push('/orders')">
            查看全部
          </el-button>
        </div>
        <el-table :data="recentOrders" style="width: 100%">
          <el-table-column prop="order_no" label="订单号" width="140" />
          <el-table-column prop="amount" label="金额" width="100">
            <template #default="{ row }">
              ¥{{ row.amount }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getOrderStatusType(row.status)">
                {{ getOrderStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="160">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '@/api'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const userChartRef = ref(null)
const incomeChartRef = ref(null)

const stats = ref({
  totalUsers: 0,
  monthlyIncome: 0,
  todayTraffic: 0,
  monthlyOrders: 0,
  userGrowth: 0,
  incomeGrowth: 0,
  trafficGrowth: 0,
  orderGrowth: 0
})

const recentUsers = ref([])
const recentOrders = ref([])

const formatTraffic = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getOrderStatusType = (status) => {
  const types = {
    pending: 'warning',
    paid: 'success',
    failed: 'danger',
    refunded: 'info'
  }
  return types[status] || 'info'
}

const getOrderStatusText = (status) => {
  const texts = {
    pending: '待支付',
    paid: '已支付',
    failed: '失败',
    refunded: '已退款'
  }
  return texts[status] || status
}

const fetchDashboardData = async () => {
  try {
    const [statsRes, usersRes, ordersRes] = await Promise.all([
      api.get('/admin/stats'),
      api.get('/admin/users', { params: { limit: 5 } }),
      api.get('/admin/orders', { params: { limit: 5 } })
    ])
    
    stats.value = statsRes.data
    recentUsers.value = usersRes.data.items || []
    recentOrders.value = ordersRes.data.items || []
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error)
  }
}

const initCharts = () => {
  // User growth chart
  const userChart = echarts.init(userChartRef.value)
  const userOption = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: getLast7Days()
    },
    yAxis: { type: 'value' },
    series: [{
      data: [120, 132, 101, 134, 90, 230, 210],
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
          { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
        ])
      },
      lineStyle: { color: '#667eea' },
      itemStyle: { color: '#667eea' }
    }]
  }
  userChart.setOption(userOption)
  
  // Income chart
  const incomeChart = echarts.init(incomeChartRef.value)
  const incomeOption = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: getLast7Days()
    },
    yAxis: { type: 'value' },
    series: [{
      data: [820, 932, 901, 934, 1290, 1330, 1320],
      type: 'bar',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#f093fb' },
          { offset: 1, color: '#f5576c' }
        ])
      }
    }]
  }
  incomeChart.setOption(incomeOption)
  
  // Resize handler
  window.addEventListener('resize', () => {
    userChart.resize()
    incomeChart.resize()
  })
}

const getLast7Days = () => {
  const days = []
  for (let i = 6; i >= 0; i--) {
    days.push(dayjs().subtract(i, 'day').format('MM-DD'))
  }
  return days
}

onMounted(async () => {
  await fetchDashboardData()
  await nextTick()
  initCharts()
})
</script>
