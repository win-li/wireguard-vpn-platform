# WireGuard VPN 运营平台

一个完整的 WireGuard VPN 订阅管理系统，支持用户注册、套餐购买、流量统计、节点管理等功能。

## ✨ 功能特性

- 🔐 **用户认证** - 邮箱注册、登录、JWT 认证
- 📦 **套餐管理** - 多种套餐、按月/按流量计费
- 🌐 **节点管理** - 多节点支持、负载均衡
- 📊 **流量统计** - 实时流量监控、用量提醒
- 💳 **支付系统** - USDT 支付 (TRC20/ERC20)
- 🎁 **运营功能** - 签到奖励、邀请返利、积分兑换
- 🔧 **管理后台** - 用户管理、订单管理、节点监控

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus |
| 后端 | FastAPI + Python 3.10+ |
| 数据库 | PostgreSQL 15 |
| VPN | WireGuard + wg-easy |
| 部署 | Docker + Docker Compose |
| 监控 | Prometheus + Grafana |

## 📁 目录结构

```
.
├── frontend/          # 用户前端 (Vue 3)
├── admin/             # 管理后台 (Vue 3)
├── backend/           # API 服务 (FastAPI)
├── database/          # 数据库脚本
├── nginx/             # Nginx 配置
├── docs/              # 项目文档
├── docker-compose.yml # Docker 编排
└── init.sql           # 数据库初始化
```

## 🚀 快速部署

### 1. 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 内存

### 2. 克隆项目

```bash
git clone https://github.com/win-li/wireguard-vpn-platform.git
cd wireguard-vpn-platform
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑配置
nano backend/.env
```

### 4. 启动服务

```bash
docker-compose up -d
```

### 5. 访问服务

| 服务 | 地址 |
|------|------|
| 用户前端 | http://localhost:3000 |
| 管理后台 | http://localhost:3001 |
| API 文档 | http://localhost:8000/api/docs |

## 📊 API 概览

### 用户端 API (v2)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v2/dashboard` | GET | 用户仪表盘 |
| `/api/v2/config` | GET | VPN 配置 |
| `/api/v2/plans` | GET | 套餐列表 |
| `/api/v2/subscribe` | POST | 购买订阅 |
| `/api/v2/checkin` | POST | 每日签到 |
| `/api/v2/payments` | GET | 支付历史 |

### 管理端 API (v2)

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v2/admin/dashboard` | GET | 管理仪表盘 |
| `/api/v2/admin/users` | GET | 用户列表 |
| `/api/v2/admin/nodes` | GET | 节点列表 |
| `/api/v2/admin/orders` | GET | 订单列表 |

## 🗄️ 数据库模型

```
users          - 用户表
subscriptions  - 订阅表
plans          - 套餐表
nodes          - 节点表
orders         - 订单表
payments       - 支付表
traffic_logs   - 流量日志
```

## 🌐 L2TP 节点集群

### AWS 马来西亚 (ap-southeast-5)

| 名称 | IP |
|------|-----|
| l2tp-malaysia | 56.68.89.1 |
| l2tp-malaysia-2 | 43.216.59.54 |
| l2tp-malaysia-3 | 43.217.77.135 |

### 阿里云吉隆坡 (ap-southeast-3)

| 名称 | IP |
|------|-----|
| CentOS-yfaf | 47.250.213.202 |
| CentOS-zgbo | 47.250.55.88 |
| 裴裴 | 47.250.87.70 |

### wg-easy 服务器

| 名称 | IP | Web UI |
|------|-----|--------|
| wg-easy-ubuntu | 47.250.159.232 | http://47.250.159.232:51821 |

## 🔧 配置说明

### WireGuard 配置

```ini
[Interface]
PrivateKey = <客户端私钥>
Address = 10.0.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = <服务器公钥>
Endpoint = <服务器IP>:51820
AllowedIPs = 0.0.0.0/0
```

### L2TP 配置

```
类型: L2TP/IPSec PSK
PSK: MYL2TP2026
用户名: vpnuser
密码: MYvpnPass123
```

## 📝 开发进度

| 模块 | 状态 |
|------|------|
| 用户前端 | ✅ 95% |
| 后端 API | ✅ 98% |
| 管理后台 API | ✅ 100% |
| 管理后台前端 | 🚧 0% |
| 支付系统 | ✅ 80% |
| L2TP 集群 | ✅ 100% |
| wg-easy | ✅ 100% |

**整体完成度: 90%**

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

*最后更新: 2026-04-21*
