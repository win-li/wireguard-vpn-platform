<template>
  <div class="connection-config">
    <el-page-header @back="goBack" content="连接配置" />
    
    <el-card class="config-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>节点配置</span>
        </div>
      </template>
      
      <el-table :data="connections" style="width: 100%" v-loading="loading">
        <el-table-column prop="node_name" label="节点名称" width="180" />
        <el-table-column prop="allowed_ips" label="分配IP" width="150" />
        <el-table-column prop="connected_at" label="连接时间" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '活跃' : '非活跃' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary"
              @click="downloadConfig(scope.row.node_id)"
            >
              下载配置
            </el-button>
            <el-button 
              size="small" 
              type="danger"
              @click="disconnect(scope.row.id)"
            >
              断开
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div style="margin-top: 20px; text-align: center;" v-if="connections.length === 0 && !loading">
        <el-empty description="暂无连接配置" />
        <el-button type="primary" @click="goToNodes">前往连接节点</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

export default {
  name: 'ConnectionConfigView',
  setup() {
    const router = useRouter()
    const connections = ref([])
    const loading = ref(false)
    
    const goBack = () => {
      router.go(-1)
    }
    
    const goToNodes = () => {
      router.push('/dashboard')
    }
    
    const loadConnections = async () => {
      try {
        loading.value = true
        // Mock API call - in real app, this would fetch from API
        setTimeout(() => {
          connections.value = [
            { id: 1, node_id: 1, node_name: '香港节点1', allowed_ips: '10.8.1.101', connected_at: '2026-03-29 10:30:00', is_active: true },
            { id: 2, node_id: 2, node_name: '新加坡节点1', allowed_ips: '10.8.2.102', connected_at: '2026-03-28 15:45:00', is_active: true },
            { id: 3, node_id: 4, node_name: '美国节点1', allowed_ips: '10.8.4.103', connected_at: '2026-03-27 09:20:00', is_active: false }
          ]
          loading.value = false
        }, 500)
      } catch (error) {
        loading.value = false
        ElMessage.error('获取连接配置失败')
      }
    }
    
    const downloadConfig = async (nodeId) => {
      try {
        // In real app, this would call the API to download the config file
        ElMessage.success('正在下载节点 ' + nodeId + ' 的配置文件')
        // Simulate download
        setTimeout(() => {
          // This would normally trigger a file download
          console.log('Download config for node ' + nodeId)
        }, 100)
      } catch (error) {
        ElMessage.error('下载配置文件失败')
      }
    }
    
    const disconnect = async (connectionId) => {
      try {
        await ElMessageBox.confirm(
          '确定要断开此连接吗？您将需要重新连接才能使用VPN服务。',
          '确认断开',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // Mock API call - in real app, this would call the API
        ElMessage.success('连接已断开')
        
        // Refresh the list
        loadConnections()
      } catch (error) {
        // Cancelled
      }
    }
    
    onMounted(() => {
      loadConnections()
    })
    
    return {
      connections,
      loading,
      goBack,
      goToNodes,
      downloadConfig,
      disconnect
    }
  }
}
</script>

<style scoped>
.connection-config {
  padding: 20px;
}

.config-card {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
