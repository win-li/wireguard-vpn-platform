import api from './index'

// VPN相关API
export const vpnApi = {
  // 获取可用节点列表
  getNodes: () => api.get('/v1/nodes'),
  
  // 创建用户与节点的连接
  createConnection: (nodeId) => api.post('/v1/nodes/connections', { node_id: nodeId }),
  
  // 获取用户的连接列表
  getUserConnections: () => api.get('/v1/nodes/connections'),
  
  // 获取特定节点的配置
  getNodeConfig: (nodeId) => api.get('/v1/configs/' + nodeId, {
    responseType: 'blob' // For downloading the config file
  }),
  
  // 删除用户与节点的连接
  deleteConnection: (connectionId) => api.delete('/v1/nodes/connections/' + connectionId),
  
  // 获取流量统计
  getTrafficStats: () => api.get('/v1/users/traffic')
}

export default vpnApi
