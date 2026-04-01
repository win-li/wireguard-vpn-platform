-- VPN 运营系统数据库设计
-- 数据库：PostgreSQL 15+
-- 创建时间：2026-03-29

-- ============================================
-- 1. 用户表 (users)
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'agent')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    balance DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    last_login_ip VARCHAR(45)
);

-- 用户索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);

-- ============================================
-- 2. 套餐表 (plans)
-- ============================================
CREATE TABLE plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    duration_days INTEGER NOT NULL,  -- 订阅天数
    bandwidth_limit BIGINT,           -- 流量限制（字节），NULL 表示不限
    device_limit INTEGER DEFAULT 3,   -- 设备数量限制
    node_access TEXT[],               -- 可访问的节点 ID 列表
    features JSONB,                   -- 其他特性
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. 订阅表 (subscriptions)
-- ============================================
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    plan_id INTEGER REFERENCES plans(id),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled', 'pending')),
    start_at TIMESTAMP NOT NULL,
    expire_at TIMESTAMP NOT NULL,
    bandwidth_used BIGINT DEFAULT 0,  -- 已用流量（字节）
    bandwidth_limit BIGINT,           -- 流量限制
    auto_renew BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订阅索引
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_expire ON subscriptions(expire_at);

-- ============================================
-- 4. VPN 节点表 (nodes)
-- ============================================
CREATE TABLE nodes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,       -- 区域：hk, sg, jp, us 等
    country VARCHAR(50) NOT NULL,
    city VARCHAR(50),
    ip_address VARCHAR(45) NOT NULL,
    port INTEGER DEFAULT 51820,
    protocol VARCHAR(20) DEFAULT 'wireguard',
    public_key TEXT,                    -- WireGuard 公钥
    bandwidth_limit BIGINT,            -- 节点带宽限制
    current_load INTEGER DEFAULT 0,    -- 当前负载（用户数）
    max_load INTEGER DEFAULT 100,      -- 最大负载
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'offline')),
    is_premium BOOLEAN DEFAULT false,  -- 高级节点
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 节点索引
CREATE INDEX idx_nodes_region ON nodes(region);
CREATE INDEX idx_nodes_status ON nodes(status);

-- ============================================
-- 5. 用户节点连接表 (user_nodes)
-- ============================================
CREATE TABLE user_nodes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    node_id INTEGER REFERENCES nodes(id),
    private_key TEXT NOT NULL,         -- 用户 WireGuard 私钥
    allowed_ips VARCHAR(255),          -- 允许的 IP 范围
    connected_at TIMESTAMP,
    disconnected_at TIMESTAMP,
    bytes_sent BIGINT DEFAULT 0,
    bytes_received BIGINT DEFAULT 0,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 6. 流量日志表 (traffic_logs)
-- ============================================
CREATE TABLE traffic_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    node_id INTEGER REFERENCES nodes(id),
    bytes_sent BIGINT DEFAULT 0,
    bytes_received BIGINT DEFAULT 0,
    session_duration INTEGER,          -- 会话时长（秒）
    client_ip VARCHAR(45),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 流量日志索引（用于快速查询）
CREATE INDEX idx_traffic_logs_user ON traffic_logs(user_id);
CREATE INDEX idx_traffic_logs_time ON traffic_logs(logged_at);

-- 分区表（按月分区，提高查询性能）
-- 注意：PostgreSQL 分区需要单独创建
-- CREATE TABLE traffic_logs_2026_03 PARTITION OF traffic_logs
--     FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- ============================================
-- 7. 支付记录表 (payments)
-- ============================================
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    subscription_id INTEGER REFERENCES subscriptions(id),
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'CNY',
    payment_method VARCHAR(50),         -- alipay, wechat, stripe 等
    transaction_id VARCHAR(255),        -- 第三方交易 ID
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'refunded')),
    metadata JSONB,                     -- 额外信息
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 支付索引
CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_transaction ON payments(transaction_id);

-- ============================================
-- 8. 优惠码表 (coupons)
-- ============================================
CREATE TABLE coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    discount_type VARCHAR(20) CHECK (discount_type IN ('percentage', 'fixed')),
    discount_value DECIMAL(10, 2) NOT NULL,
    max_uses INTEGER,
    used_count INTEGER DEFAULT 0,
    valid_from TIMESTAMP,
    valid_until TIMESTAMP,
    plan_ids INTEGER[],                 -- 适用套餐 ID
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 9. 系统配置表 (settings)
-- ============================================
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 10. 管理员操作日志 (admin_logs)
-- ============================================
CREATE TABLE admin_logs (
    id BIGSERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),            -- user, node, plan 等
    target_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 初始数据
-- ============================================

-- 插入默认套餐
INSERT INTO plans (name, description, price, duration_days, bandwidth_limit, device_limit, is_active) VALUES
('基础版', '适合日常使用', 29.00, 30, 107374182400, 2, true),      -- 100GB
('标准版', '适合重度用户', 49.00, 30, 322122547200, 3, true),      -- 300GB
('高级版', '无限流量', 99.00, 30, NULL, 5, true);                  -- 无限

-- 插入默认节点
INSERT INTO nodes (name, region, country, city, ip_address, protocol, status, is_premium) VALUES
('新加坡节点-01', 'sg', '新加坡', '新加坡', '54.179.206.121', 'wireguard', 'active', false),
('香港节点-01', 'hk', '中国香港', '香港', '43.199.34.229', 'wireguard', 'active', true);

-- 插入系统默认配置
INSERT INTO settings (key, value, description) VALUES
('site_name', 'VPN服务', '网站名称'),
('default_bandwidth_limit', '107374182400', '默认流量限制（100GB）'),
('max_devices_per_user', '3', '每用户最大设备数'),
('trial_days', '3', '试用天数');

-- ============================================
-- 视图
-- ============================================

-- 用户订阅视图
CREATE VIEW v_user_subscriptions AS
SELECT
    u.id AS user_id,
    u.email,
    u.username,
    s.id AS subscription_id,
    p.name AS plan_name,
    s.status,
    s.start_at,
    s.expire_at,
    s.bandwidth_used,
    s.bandwidth_limit,
    CASE
        WHEN s.bandwidth_limit IS NULL THEN NULL
        ELSE ROUND((s.bandwidth_used::DECIMAL / s.bandwidth_limit) * 100, 2)
    END AS bandwidth_usage_percent
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id AND s.status = 'active'
LEFT JOIN plans p ON s.plan_id = p.id;

-- 节点状态视图
CREATE VIEW v_node_status AS
SELECT
    n.id,
    n.name,
    n.region,
    n.country,
    n.ip_address,
    n.status,
    n.current_load,
    n.max_load,
    ROUND((n.current_load::DECIMAL / n.max_load) * 100, 2) AS load_percent,
    n.is_premium
FROM nodes n
WHERE n.status = 'active';

-- ============================================
-- 函数
-- ============================================

-- 检查用户订阅状态
CREATE OR REPLACE FUNCTION check_subscription(user_id INTEGER)
RETURNS TABLE(
    is_active BOOLEAN,
    days_remaining INTEGER,
    bandwidth_remaining BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        EXISTS (
            SELECT 1 FROM subscriptions
            WHERE subscriptions.user_id = check_subscription.user_id
            AND status = 'active'
            AND expire_at > NOW()
        ) AS is_active,
        COALESCE(
            (SELECT EXTRACT(DAY FROM (expire_at - NOW()))::INTEGER
             FROM subscriptions
             WHERE user_id = check_subscription.user_id
             AND status = 'active'
             ORDER BY expire_at DESC LIMIT 1),
            0
        ) AS days_remaining,
        COALESCE(
            (SELECT bandwidth_limit - bandwidth_used
             FROM subscriptions
             WHERE user_id = check_subscription.user_id
             AND status = 'active'
             AND bandwidth_limit IS NOT NULL
             ORDER BY expire_at DESC LIMIT 1),
            -1  -- -1 表示无限
        ) AS bandwidth_remaining;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 触发器
-- ============================================

-- 自动更新 updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_nodes_updated_at
    BEFORE UPDATE ON nodes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
