<template>
  <div class="table-page">
    <div class="page-header">
      <h2 class="page-title">节点管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加节点
      </el-button>
    </div>
    
    <!-- Filter Card -->
    <div class="filter-card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="节点名称">
          <el-input v-model="searchKeyword" placeholder="搜索节点" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="statusFilter" placeholder="全部" clearable>
            <el-option label="在线" value="online" />
            <el-option label="离线" value="offline" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchNodes">搜索</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <!-- Table Card -->
    <div class="table-card">
      <el-table :data="nodes" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="节点名称" />
        <el-table-column prop="server" label="服务器地址" />
        <el-table-column prop="port" label="端口" width="80" />
        <el-table-column prop="method" label="加密方式" width="100" />
        <el-table-column prop="region" label="地区" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="负载" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="row.load || 0"
              :color="getLoadColor(row.load)"
              :stroke-width="10"
            />
          </template>
        </el-table-column>
        <el-table-column prop="users_count" label="连接用户" width="100" />
        <el-table-column prop="traffic_used" label="流量" width="120">
          <template #default="{ row }">
            {{ formatTraffic(row.traffic_used) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="showEditDialog(row)">编辑</el-button>
            <el-button type="warning" link @click="testNode(row)">测试</el-button>
            <el-button type="danger" link @click="deleteNode(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="fetchNodes"
          @current-change="fetchNodes"
        />
      </div>
    </div>
    
    <!-- Add/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑节点' : '添加节点'" width="500px">
      <el-form :model="nodeForm" :rules="nodeRules" ref="nodeFormRef" label-width="100px">
        <el-form-item label="节点名称" prop="name">
          <el-input v-model="nodeForm.name" placeholder="请输入节点名称" />
        </el-form-item>
        <el-form-item label="服务器地址" prop="server">
          <el-input v-model="nodeForm.server" placeholder="请输入服务器地址" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="nodeForm.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="加密方式" prop="method">
          <el-select v-model="nodeForm.method" placeholder="请选择加密方式">
            <el-option label="aes-256-gcm" value="aes-256-gcm" />
            <el-option label="aes-128-gcm" value="aes-128-gcm" />
            <el-option label="chacha20-poly1305" value="chacha20-poly1305" />
            <el-option label="xchacha20-poly1305" value="xchacha20-poly1305" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="nodeForm.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="地区" prop="region">
          <el-input v-model="nodeForm.region" placeholder="如：香港、美国" />
        </el-form-item>
        <el-form-item label="倍率" prop="rate">
          <el-input-number v-model="nodeForm.rate" :min="0.1" :max="10" :precision="1" :step="0.1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNode">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const nodes = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const searchKeyword = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const nodeFormRef = ref(null)

const nodeForm = reactive({
  id: null,
  name: '',
  server: '',
  port: 8388,
  method: 'aes-256-gcm',
  password: '',
  region: '',
  rate: 1.0
})

const nodeRules = {
  name: [{ required: true, message: '请输入节点名称', trigger: 'blur' }],
  server: [{ required: true, message: '请输入服务器地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口', trigger: 'blur' }],
  method: [{ required: true, message: '请选择加密方式', trigger: 'change' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const formatTraffic = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getLoadColor = (load) => {
  if (load < 50) return '#67C23A'
  if (load < 80) return '#E6A23C'
  return '#F56C6C'
}

const fetchNodes = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchKeyword.value) params.search = searchKeyword.value
    if (statusFilter.value) params.status = statusFilter.value
    
    const response = await api.get('/admin/nodes', { params })
    nodes.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    ElMessage.error('获取节点列表失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  nodeForm.id = null
  nodeForm.name = ''
  nodeForm.server = ''
  nodeForm.port = 8388
  nodeForm.method = 'aes-256-gcm'
  nodeForm.password = ''
  nodeForm.region = ''
  nodeForm.rate = 1.0
}

const showAddDialog = () => {
  resetForm()
  isEdit.value = false
  dialogVisible.value = true
}

const showEditDialog = (node) => {
  isEdit.value = true
  Object.assign(nodeForm, {
    id: node.id,
    name: node.name,
    server: node.server,
    port: node.port,
    method: node.method,
    password: '', // 不显示密码
    region: node.region,
    rate: node.rate
  })
  dialogVisible.value = true
}

const submitNode = async () => {
  if (!nodeFormRef.value) return
  
  await nodeFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      if (isEdit.value) {
        await api.put('/admin/nodes/' + nodeForm.id, nodeForm)
        ElMessage.success('节点更新成功')
      } else {
        await api.post('/admin/nodes', nodeForm)
        ElMessage.success('节点添加成功')
      }
      dialogVisible.value = false
      fetchNodes()
    } catch (error) {
      ElMessage.error(isEdit.value ? '节点更新失败' : '节点添加失败')
    }
  })
}

const testNode = async (node) => {
  try {
    ElMessage.info('正在测试节点连接...')
    const response = await api.post('/admin/nodes/' + node.id + '/test')
    if (response.data.success) {
      ElMessage.success('节点连接正常')
    } else {
      ElMessage.error('节点连接失败: ' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('节点测试失败')
  }
}

const deleteNode = async (node) => {
  try {
    await ElMessageBox.confirm('确定要删除节点 ' + node.name + ' 吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await api.delete('/admin/nodes/' + node.id)
    ElMessage.success('节点删除成功')
    fetchNodes()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('节点删除失败')
    }
  }
}

onMounted(() => {
  fetchNodes()
})
</script>
