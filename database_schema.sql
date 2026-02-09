-- ============================================================
-- 智农链销 - 数据库表结构 SQL 脚本
-- 数据库: zhinong_db
-- ============================================================

-- 1. 农户表 (farmers)
CREATE TABLE IF NOT EXISTS farmers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    email VARCHAR(100),
    
    -- 地址信息
    province VARCHAR(50),
    city VARCHAR(50),
    county VARCHAR(50),
    village VARCHAR(100),
    
    -- 认证信息
    is_verified BOOLEAN DEFAULT FALSE,
    certification_type VARCHAR(50),
    certification_doc VARCHAR(500),
    
    -- 订阅信息
    tier VARCHAR(20) DEFAULT 'free' CHECK (tier IN ('free', 'basic', 'professional')),
    subscription_start TIMESTAMP,
    subscription_end TIMESTAMP,
    
    -- 额度控制
    services_count INTEGER DEFAULT 0,
    api_calls_today INTEGER DEFAULT 0,
    
    -- 财务设置
    enable_commission BOOLEAN DEFAULT FALSE,
    commission_rate INTEGER DEFAULT 5,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_farmers_name ON farmers(name);
CREATE INDEX IF NOT EXISTS idx_farmers_phone ON farmers(phone);
CREATE INDEX IF NOT EXISTS idx_farmers_county ON farmers(county);

COMMENT ON TABLE farmers IS '农户信息表';
COMMENT ON COLUMN farmers.tier IS '订阅等级: free-免费版, basic-基础版, professional-专业版';


-- 2. 产品表 (products)
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    farmer_id VARCHAR(50) NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    
    -- 基础信息
    name VARCHAR(200) NOT NULL,
    sku_code VARCHAR(50) UNIQUE NOT NULL,
    category VARCHAR(100),
    
    -- 规格与定价
    specs JSONB,
    price NUMERIC(10, 2) NOT NULL,
    original_price NUMERIC(10, 2),
    
    -- 库存管理
    stock INTEGER DEFAULT 0,
    stock_alert_threshold INTEGER DEFAULT 10,
    
    -- 营销信息
    target_scene VARCHAR(100),
    packaging_type VARCHAR(50),
    selling_points JSONB,
    
    -- 媒体资源
    images JSONB,
    video_url VARCHAR(500),
    
    -- 溯源信息
    origin_info JSONB,
    
    -- 描述
    description TEXT,
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_products_farmer_id ON products(farmer_id);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_sku_code ON products(sku_code);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_is_active ON products(is_active);

COMMENT ON TABLE products IS '产品信息表';


-- 3. 订单表 (orders)
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    farmer_id VARCHAR(50) NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    customer_id VARCHAR(50),
    
    -- 订单商品
    items JSONB NOT NULL,
    
    -- 金额
    subtotal NUMERIC(10, 2) NOT NULL,
    shipping_fee NUMERIC(10, 2) DEFAULT 0,
    discount NUMERIC(10, 2) DEFAULT 0,
    total_amount NUMERIC(10, 2) NOT NULL,
    
    -- 支付信息
    payment_method VARCHAR(50),
    payment_transaction_id VARCHAR(100),
    paid_at TIMESTAMP,
    
    -- 配送信息
    shipping_address JSONB NOT NULL,
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(100),
    shipped_at TIMESTAMP,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded')),
    
    -- 备注
    customer_note TEXT,
    farmer_note TEXT,
    
    -- 完成时间
    completed_at TIMESTAMP,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_orders_farmer_id ON orders(farmer_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

COMMENT ON TABLE orders IS '订单信息表';
COMMENT ON COLUMN orders.status IS '订单状态: pending-待支付, paid-已支付, shipped-已发货, completed-已完成, cancelled-已取消, refunded-已退款';


-- 4. MCP服务表 (mcp_services)
CREATE TABLE IF NOT EXISTS mcp_services (
    id VARCHAR(50) PRIMARY KEY,
    farmer_id VARCHAR(50) NOT NULL REFERENCES farmers(id) ON DELETE CASCADE,
    
    -- 服务信息
    service_name VARCHAR(200) NOT NULL,
    service_type VARCHAR(50),
    description TEXT,
    
    -- 需求信息
    requirement TEXT NOT NULL,
    target_products JSONB,
    
    -- 生成状态
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'planning', 'generating', 'testing', 'completed', 'failed', 'deployed')),
    progress INTEGER DEFAULT 0,
    
    -- 生成结果
    generated_code TEXT,
    api_endpoint VARCHAR(500),
    deployment_url VARCHAR(500),
    
    -- 成本统计
    total_cost NUMERIC(10, 4) DEFAULT 0,
    token_usage JSONB,
    
    -- 质量评分
    quality_score NUMERIC(5, 2),
    test_results JSONB,
    
    -- 错误信息
    error_message TEXT,
    
    -- 时间戳
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_mcp_services_farmer_id ON mcp_services(farmer_id);
CREATE INDEX IF NOT EXISTS idx_mcp_services_status ON mcp_services(status);

COMMENT ON TABLE mcp_services IS 'MCP服务生成记录表';
COMMENT ON COLUMN mcp_services.status IS '服务状态: pending-待处理, planning-规划中, generating-生成中, testing-测试中, completed-已完成, failed-失败, deployed-已部署';


-- 5. 服务日志表 (service_logs)
CREATE TABLE IF NOT EXISTS service_logs (
    id VARCHAR(50) PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL REFERENCES mcp_services(id) ON DELETE CASCADE,
    
    -- 日志信息
    log_level VARCHAR(20) DEFAULT 'info' CHECK (log_level IN ('debug', 'info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    details JSONB,
    
    -- 阶段信息
    stage VARCHAR(50),
    agent_name VARCHAR(100),
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_service_logs_service_id ON service_logs(service_id);
CREATE INDEX IF NOT EXISTS idx_service_logs_log_level ON service_logs(log_level);
CREATE INDEX IF NOT EXISTS idx_service_logs_created_at ON service_logs(created_at);

COMMENT ON TABLE service_logs IS '服务生成日志表';


-- 6. 服务部署表 (service_deployments)
CREATE TABLE IF NOT EXISTS service_deployments (
    id VARCHAR(50) PRIMARY KEY,
    service_id VARCHAR(50) NOT NULL REFERENCES mcp_services(id) ON DELETE CASCADE,
    
    -- 部署信息
    deployment_type VARCHAR(50) DEFAULT 'docker',
    deployment_url VARCHAR(500),
    container_id VARCHAR(100),
    
    -- 配置信息
    environment_vars JSONB,
    port INTEGER,
    
    -- 状态
    status VARCHAR(20) DEFAULT 'deploying' CHECK (status IN ('deploying', 'running', 'stopped', 'failed')),
    health_check_url VARCHAR(500),
    last_health_check TIMESTAMP,
    
    -- 资源使用
    cpu_usage NUMERIC(5, 2),
    memory_usage NUMERIC(10, 2),
    
    -- 错误信息
    error_message TEXT,
    
    -- 时间戳
    deployed_at TIMESTAMP,
    stopped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_service_deployments_service_id ON service_deployments(service_id);
CREATE INDEX IF NOT EXISTS idx_service_deployments_status ON service_deployments(status);

COMMENT ON TABLE service_deployments IS '服务部署记录表';


-- ============================================================
-- 插入演示数据
-- ============================================================

-- 插入演示农户
INSERT INTO farmers (
    id, name, phone, password_hash, email,
    province, city, county, village,
    tier, is_verified, certification_type,
    services_count, api_calls_today,
    enable_commission, commission_rate,
    created_at, updated_at
) VALUES (
    'farmer_demo_001',
    '蒲县被子垣果园',
    '13800138000',
    '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', -- 密码: demo123456 (SHA256)
    'demo@zhinonglianxiao.com',
    '山西省',
    '临汾市',
    '蒲县',
    '被子垣村',
    'basic',
    TRUE,
    '有机认证',
    0,
    0,
    FALSE,
    5,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
) ON CONFLICT (phone) DO NOTHING;


-- 插入演示产品
INSERT INTO products (
    id, farmer_id, name, sku_code,
    price, stock, category, description,
    is_active, is_featured,
    created_at, updated_at
) VALUES 
(
    'prod_demo_001',
    'farmer_demo_001',
    '玉露香梨 - 精品礼盒装',
    'SKU_YLXL_001',
    88.00,
    100,
    '水果',
    '蒲县特产玉露香梨，皮薄肉嫩，汁多味甜。精品礼盒装，适合送礼。',
    TRUE,
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'prod_demo_002',
    'farmer_demo_001',
    '玉露香梨 - 家庭装',
    'SKU_YLXL_002',
    58.00,
    200,
    '水果',
    '蒲县特产玉露香梨，适合家庭日常食用。5斤装。',
    TRUE,
    FALSE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
),
(
    'prod_demo_003',
    'farmer_demo_001',
    '有机苹果 - 富士',
    'SKU_APPLE_001',
    45.00,
    150,
    '水果',
    '有机种植富士苹果，脆甜可口，营养丰富。',
    TRUE,
    FALSE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (sku_code) DO NOTHING;


-- ============================================================
-- 创建更新时间戳的触发器函数
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新时间戳触发器
CREATE TRIGGER update_farmers_updated_at BEFORE UPDATE ON farmers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mcp_services_updated_at BEFORE UPDATE ON mcp_services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_deployments_updated_at BEFORE UPDATE ON service_deployments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- 验证表创建
-- ============================================================

-- 查看所有表
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 查看演示数据
SELECT '农户数量:' as info, COUNT(*) as count FROM farmers
UNION ALL
SELECT '产品数量:', COUNT(*) FROM products
UNION ALL
SELECT '订单数量:', COUNT(*) FROM orders;

