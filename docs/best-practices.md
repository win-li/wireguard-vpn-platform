# VPN系统最佳实践功能文档

本文档描述了已实现的五项最佳实践功能。

## 1. Prometheus监控集成

### 文件位置
- `backend/api/metrics_router.py`

### 功能
提供Prometheus格式的监控指标，包括：
- 用户总数 / 活跃用户数
- 活跃订阅数 / 过期订阅数
- 节点总数 / 在线节点数
- 活跃连接数
- 24小时流量统计
- 总带宽使用量

### API端点
```
GET /api/v1/metrics/metrics       # Prometheus格式指标
GET /api/v1/metrics/health        # 健康检查
```

### Prometheus配置示例
```yaml
scrape_configs:
  - job_name: vpn-system
    static_configs:
      - targets: [localhost:8000]
    metrics_path: /api/v1/metrics/metrics
```

---

## 2. QR码配置生成

### 文件位置
- `backend/utils/qrcode_gen.py`
- `backend/api/qrcode_router.py`

### 功能
为WireGuard配置生成QR码，方便移动端扫描导入。

### API端点
```
POST /api/v1/qrcode/generate      # 生成QR码（返回base64）
POST /api/v1/qrcode/generate/png  # 生成QR码PNG图片
GET  /api/v1/qrcode/user-node/{id} # 获取用户节点QR码
GET  /api/v1/qrcode/config/{id}    # 获取WireGuard配置文件
```

### 使用示例
```python
from utils.qrcode_gen import QRCodeGenerator

# 生成QR码
qr_base64 = QRCodeGenerator.generate_wireguard_qr_base64(
    private_key="用户私钥",
    address="10.0.0.2/24",
    peer_public_key="服务器公钥",
    peer_endpoint="vpn.example.com:51820"
)
```

---

## 3. 客户端过期检查

### 文件位置
- `backend/utils/expiry_checker.py`
- `backend/api/expiry_router.py`
- `backend/tasks/scheduler_tasks.py`

### 功能
- 自动检测过期订阅
- 自动禁用过期用户的连接
- 提醒即将过期的订阅
- 定时任务自动执行

### API端点
```
POST /api/v1/expiry/check         # 触发过期检查（异步）
GET  /api/v1/expiry/run           # 执行过期检查（同步）
GET  /api/v1/expiry/statistics    # 获取过期统计
GET  /api/v1/expiry/expiring-soon # 获取即将过期的订阅
```

### 定时任务配置
在 `tasks/celery_app.py` 中配置：
- 每小时检查过期订阅
- 每6小时检查即将过期订阅
- 每天清理旧告警

### 启动Celery
```bash
# Worker
celery -A tasks.celery_app worker --loglevel=info

# Beat scheduler
celery -A tasks.celery_app beat --loglevel=info
```

---

## 4. NAT穿透配置

### 文件位置
- `backend/utils/nat_traversal.py`
- `backend/api/nat_router.py`

### 功能
- NAT类型检测（Full Cone, Restricted, Symmetric）
- 公网IP/端口获取
- STUN服务器配置
- 推荐WireGuard keepalive设置
- UDP打洞辅助接口

### API端点
```
GET /api/v1/nat/info               # 获取NAT信息
GET /api/v1/nat/config             # 获取NAT配置
GET /api/v1/nat/recommended-keepalive # 推荐keepalive值
GET /api/v1/nat/stun-servers       # STUN服务器列表
```

### NAT类型说明
- **Full Cone**: 最宽松，无需特殊配置
- **Restricted Cone**: 中等严格，需要keepalive
- **Port Restricted**: 较严格，需要频繁keepalive
- **Symmetric**: 最严格，每个目标使用不同端口

---

## 5. 设备姿态检查

### 文件位置
- `backend/models/device_posture.py`
- `backend/utils/device_checker.py`
- `backend/api/device_router.py`

### 功能
- 设备注册与识别
- 客户端版本检查
- 越狱检测
- 设备信任/封禁管理
- 安全告警系统

### 数据库表
- `device_postures`: 设备信息表
- `device_alerts`: 设备告警表

### API端点
```
POST /api/v1/devices/register      # 注册设备
POST /api/v1/devices/check         # 执行设备检查
GET  /api/v1/devices/user/{user_id} # 获取用户设备列表
POST /api/v1/devices/block         # 封禁设备
POST /api/v1/devices/trust         # 信任设备
GET  /api/v1/devices/alerts        # 获取设备告警
```

### 检查项目
1. 客户端版本是否过期
2. 设备是否越狱/root
3. 磁盘是否加密
4. 设备是否被信任

---

## 数据库迁移

创建新的设备姿态表：
```bash
cd /home/ubuntu/vpn-system/backend
python -m database.migrations.add_device_posture
```

---

## 依赖安装

确保requirements.txt包含：
```
qrcode>=7.4.2
Pillow>=10.0.0  # QR码生成需要
celery>=5.4.0
redis>=5.2.0
```

---

## 部署检查清单

- [ ] 运行数据库迁移创建设备表
- [ ] 安装Pillow库（QR码生成）
- [ ] 启动Redis服务
- [ ] 启动Celery Worker
- [ ] 启动Celery Beat
- [ ] 配置Prometheus抓取指标
- [ ] 测试所有API端点
