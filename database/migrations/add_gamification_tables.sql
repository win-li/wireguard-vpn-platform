-- ============================================
-- 运营增长功能数据库表
-- 创建时间：2026-03-30
-- ============================================

-- ============================================
-- 1. 邀请码表 (user_invite_codes)
-- ============================================
CREATE TABLE IF NOT EXISTS user_invite_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invite_code VARCHAR(20) UNIQUE NOT NULL,
    total_invites INTEGER DEFAULT 0,
    successful_invites INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invite_codes_user ON user_invite_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_invite_codes_code ON user_invite_codes(invite_code);

-- ============================================
-- 2. 邀请记录表 (invitations)
-- ============================================
CREATE TABLE IF NOT EXISTS invitations (
    id SERIAL PRIMARY KEY,
    inviter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invitee_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    invite_code VARCHAR(20) NOT NULL,
    invitee_email VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'registered', 'rewarded')),
    reward_days INTEGER DEFAULT 0,
    reward_granted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invitations_inviter ON invitations(inviter_id);
CREATE INDEX IF NOT EXISTS idx_invitations_invitee ON invitations(invitee_id);
CREATE INDEX IF NOT EXISTS idx_invitations_code ON invitations(invite_code);
CREATE INDEX IF NOT EXISTS idx_invitations_status ON invitations(status);

-- ============================================
-- 3. 佣金余额表 (user_commission_balances)
-- ============================================
CREATE TABLE IF NOT EXISTS user_commission_balances (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_earned DECIMAL(10, 2) DEFAULT 0.00,
    total_withdrawn DECIMAL(10, 2) DEFAULT 0.00,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_commission_balances_user ON user_commission_balances(user_id);

-- ============================================
-- 4. 佣金记录表 (commissions)
-- ============================================
CREATE TABLE IF NOT EXISTS commissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    from_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    level INTEGER DEFAULT 1,
    order_id INTEGER REFERENCES payments(id) ON DELETE SET NULL,
    order_amount DECIMAL(10, 2),
    commission_rate DECIMAL(5, 4),
    commission_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'settled', 'withdrawn')),
    settled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_commissions_user ON commissions(user_id);
CREATE INDEX IF NOT EXISTS idx_commissions_from_user ON commissions(from_user_id);
CREATE INDEX IF NOT EXISTS idx_commissions_order ON commissions(order_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON commissions(status);

-- ============================================
-- 5. 佣金提现记录表 (commission_withdrawals)
-- ============================================
CREATE TABLE IF NOT EXISTS commission_withdrawals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    withdraw_method VARCHAR(50) NOT NULL,
    account_info TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'success', 'failed')),
    reject_reason VARCHAR(255),
    processed_at TIMESTAMP,
    transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_withdrawals_user ON commission_withdrawals(user_id);
CREATE INDEX IF NOT EXISTS idx_withdrawals_status ON commission_withdrawals(status);

-- ============================================
-- 6. 签到记录表 (daily_checkins)
-- ============================================
CREATE TABLE IF NOT EXISTS daily_checkins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    checkin_date TIMESTAMP NOT NULL,
    consecutive_days INTEGER DEFAULT 1,
    points_earned INTEGER DEFAULT 0,
    bonus_points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_checkins_user ON daily_checkins(user_id);
CREATE INDEX IF NOT EXISTS idx_checkins_date ON daily_checkins(checkin_date);

-- ============================================
-- 7. 连续签到记录表 (checkin_streaks)
-- ============================================
CREATE TABLE IF NOT EXISTS checkin_streaks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_streak INTEGER DEFAULT 0,
    max_streak INTEGER DEFAULT 0,
    last_checkin_date TIMESTAMP,
    total_checkins INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_streaks_user ON checkin_streaks(user_id);

-- ============================================
-- 8. 用户积分表 (user_points)
-- ============================================
CREATE TABLE IF NOT EXISTS user_points (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_points INTEGER DEFAULT 0,
    used_points INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_points_user ON user_points(user_id);

-- ============================================
-- 9. 积分交易记录表 (point_transactions)
-- ============================================
CREATE TABLE IF NOT EXISTS point_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    related_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_point_trans_user ON point_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_point_trans_type ON point_transactions(type);

-- ============================================
-- 10. 任务定义表 (tasks)
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    task_type VARCHAR(50) NOT NULL CHECK (task_type IN ('daily', 'one_time', 'achievement')),
    task_code VARCHAR(50) UNIQUE NOT NULL,
    points INTEGER DEFAULT 0,
    reward_days INTEGER DEFAULT 0,
    max_completions INTEGER DEFAULT 1,
    requirements TEXT,
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_code ON tasks(task_code);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_tasks_active ON tasks(is_active);

-- ============================================
-- 11. 用户任务记录表 (user_tasks)
-- ============================================
CREATE TABLE IF NOT EXISTS user_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    completion_count INTEGER DEFAULT 0,
    last_completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'completed', 'claimed')),
    points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_tasks_user ON user_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_user_tasks_task ON user_tasks(task_id);

-- ============================================
-- 12. 积分兑换规则表 (point_exchange_rules)
-- ============================================
CREATE TABLE IF NOT EXISTS point_exchange_rules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    points_required INTEGER NOT NULL,
    reward_type VARCHAR(50) NOT NULL CHECK (reward_type IN ('days', 'traffic', 'discount')),
    reward_value INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exchange_rules_active ON point_exchange_rules(is_active);

-- ============================================
-- 13. 积分兑换记录表 (point_exchanges)
-- ============================================
CREATE TABLE IF NOT EXISTS point_exchanges (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points_used INTEGER NOT NULL,
    reward_type VARCHAR(50) NOT NULL,
    reward_value INTEGER NOT NULL,
    reward_description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exchanges_user ON point_exchanges(user_id);

-- ============================================
-- 初始化默认任务
-- ============================================
INSERT INTO tasks (name, description, task_type, task_code, points, reward_days, max_completions, sort_order)
VALUES 
    ('每日签到', '每天签到可获得积分奖励', 'daily', 'daily_checkin', 10, 0, 1, 1),
    ('首次登录', '完成首次登录获得奖励', 'one_time', 'first_login', 50, 1, 1, 2),
    ('邀请好友', '成功邀请一位好友注册', 'achievement', 'invite_friend', 100, 3, 0, 3),
    ('分享给好友', '分享给好友获得奖励', 'daily', 'share', 5, 0, 1, 4),
    ('完善个人资料', '完善个人资料信息', 'one_time', 'complete_profile', 20, 0, 1, 5)
ON CONFLICT (task_code) DO NOTHING;

-- ============================================
-- 初始化默认兑换规则
-- ============================================
INSERT INTO point_exchange_rules (name, description, points_required, reward_type, reward_value, sort_order)
VALUES 
    ('兑换1天会员', '使用100积分兑换1天会员时长', 100, 'days', 1, 1),
    ('兑换7天会员', '使用500积分兑换7天会员时长', 500, 'days', 7, 2),
    ('兑换30天会员', '使用1800积分兑换30天会员时长', 1800, 'days', 30, 3)
ON CONFLICT DO NOTHING;
