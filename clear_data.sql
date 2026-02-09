-- ============================================================
-- 清空所有数据并重新插入
-- 请在 DataGrip 中选中 zhinong_db 数据库后执行
-- ============================================================

-- 第一步：清空所有表的数据（保留表结构）
TRUNCATE TABLE service_deployments CASCADE;
TRUNCATE TABLE service_logs CASCADE;
TRUNCATE TABLE mcp_services CASCADE;
TRUNCATE TABLE orders CASCADE;
TRUNCATE TABLE products CASCADE;
TRUNCATE TABLE farmers CASCADE;

-- 验证清空结果
SELECT '清空完成' as 状态, 
       (SELECT COUNT(*) FROM farmers) as 农户数,
       (SELECT COUNT(*) FROM products) as 产品数,
       (SELECT COUNT(*) FROM orders) as 订单数;

