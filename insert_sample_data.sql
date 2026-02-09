-- ============================================================
-- 智农链销 - 示例数据插入脚本
-- 请在 DataGrip 中选中 zhinong_db 数据库后执行
-- ============================================================

-- 清空现有数据（可选，如果需要重新插入）
-- TRUNCATE TABLE service_deployments, service_logs, mcp_services, orders, products, farmers RESTART IDENTITY CASCADE;

-- ============================================================
-- 1. 插入农户数据 (5个农户)
-- ============================================================

INSERT INTO farmers (id, name, phone, password_hash, email, province, city, county, village, tier, is_verified, certification_type, services_count, api_calls_today, enable_commission, commission_rate, created_at, updated_at) VALUES
('farmer_001', '蒲县被子垣果园', '13800138000', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'demo@zhinonglianxiao.com', '山西省', '临汾市', '蒲县', '被子垣村', 'basic', true, '有机认证', 5, 12, false, 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('farmer_002', '临汾红富士果园', '13800138001', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'hongfushi@example.com', '山西省', '临汾市', '尧都区', '刘村镇', 'professional', true, '绿色食品认证', 8, 25, true, 8, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('farmer_003', '吉县壶口苹果园', '13800138002', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'hukou@example.com', '山西省', '临汾市', '吉县', '壶口镇', 'basic', true, '无公害认证', 3, 8, false, 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('farmer_004', '襄汾县优质核桃基地', '13800138003', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'hetao@example.com', '山西省', '临汾市', '襄汾县', '南贾镇', 'free', false, null, 0, 0, false, 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('farmer_005', '洪洞大槐树农场', '13800138004', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'dahuaishu@example.com', '山西省', '临汾市', '洪洞县', '大槐树镇', 'basic', true, '有机认证', 6, 15, true, 6, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ============================================================
-- 2. 插入产品数据 (每个农户3-5个产品，共20个产品)
-- ============================================================

-- 农户1的产品 (玉露香梨系列)
INSERT INTO products (id, farmer_id, name, sku_code, category, price, original_price, stock, description, specs, images, is_active, is_featured, created_at, updated_at) VALUES
('prod_001', 'farmer_001', '玉露香梨 - 精品礼盒装', 'SKU_YLXL_001', '水果', 88.00, 98.00, 100, '蒲县特产玉露香梨，皮薄肉嫩，汁多味甜。精品礼盒装，适合送礼。', '{"weight": "5斤", "grade": "特级", "package": "礼盒"}', '["https://example.com/images/ylxl_gift.jpg"]', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_002', 'farmer_001', '玉露香梨 - 家庭装', 'SKU_YLXL_002', '水果', 58.00, 68.00, 200, '蒲县特产玉露香梨，适合家庭日常食用。5斤装。', '{"weight": "5斤", "grade": "一级", "package": "纸箱"}', '["https://example.com/images/ylxl_family.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_003', 'farmer_001', '玉露香梨 - 尝鲜装', 'SKU_YLXL_003', '水果', 28.00, 35.00, 150, '小份量尝鲜装，2斤装，适合初次购买。', '{"weight": "2斤", "grade": "一级", "package": "网袋"}', '["https://example.com/images/ylxl_trial.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_004', 'farmer_001', '玉露香梨 - 批发装', 'SKU_YLXL_004', '水果', 180.00, 200.00, 80, '批发装，15斤大箱，适合团购和批发商。', '{"weight": "15斤", "grade": "一级", "package": "大纸箱"}', '["https://example.com/images/ylxl_bulk.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 农户2的产品 (红富士苹果系列)
INSERT INTO products (id, farmer_id, name, sku_code, category, price, original_price, stock, description, specs, images, is_active, is_featured, created_at, updated_at) VALUES
('prod_005', 'farmer_002', '红富士苹果 - 特级果', 'SKU_HFS_001', '水果', 68.00, 78.00, 180, '临汾红富士苹果，色泽鲜艳，脆甜多汁，特级果。', '{"weight": "5斤", "grade": "特级", "diameter": "80mm+"}', '["https://example.com/images/hfs_premium.jpg"]', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_006', 'farmer_002', '红富士苹果 - 一级果', 'SKU_HFS_002', '水果', 48.00, 58.00, 250, '一级红富士苹果，性价比高，适合家庭食用。', '{"weight": "5斤", "grade": "一级", "diameter": "75mm+"}', '["https://example.com/images/hfs_first.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_007', 'farmer_002', '红富士苹果 - 礼盒装', 'SKU_HFS_003', '水果', 128.00, 148.00, 100, '高档礼盒装，精选特级果，送礼佳品。', '{"weight": "8斤", "grade": "特级", "package": "高档礼盒"}', '["https://example.com/images/hfs_gift.jpg"]', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_008', 'farmer_002', '红富士苹果 - 果汁专用', 'SKU_HFS_004', '水果', 35.00, 40.00, 300, '果汁专用苹果，新鲜多汁，适合榨汁。', '{"weight": "5斤", "grade": "二级", "usage": "榨汁"}', '["https://example.com/images/hfs_juice.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 农户3的产品 (壶口苹果系列)
INSERT INTO products (id, farmer_id, name, sku_code, category, price, original_price, stock, description, specs, images, is_active, is_featured, created_at, updated_at) VALUES
('prod_009', 'farmer_003', '壶口红苹果 - 精品装', 'SKU_HK_001', '水果', 55.00, 65.00, 120, '吉县壶口特产红苹果，黄河岸边种植，日照充足。', '{"weight": "5斤", "grade": "特级", "origin": "壶口"}', '["https://example.com/images/hk_premium.jpg"]', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_010', 'farmer_003', '壶口苹果 - 家庭装', 'SKU_HK_002', '水果', 38.00, 45.00, 200, '家庭装壶口苹果，实惠好吃。', '{"weight": "5斤", "grade": "一级"}', '["https://example.com/images/hk_family.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_011', 'farmer_003', '壶口冰糖心苹果', 'SKU_HK_003', '水果', 78.00, 88.00, 80, '稀有冰糖心品种，核心透明如冰糖，极甜。', '{"weight": "5斤", "grade": "特级", "feature": "冰糖心"}', '["https://example.com/images/hk_bingtangxin.jpg"]', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 农户4的产品 (核桃系列)
INSERT INTO products (id, farmer_id, name, sku_code, category, price, original_price, stock, description, specs, images, is_active, is_featured, created_at, updated_at) VALUES
('prod_012', 'farmer_004', '薄皮核桃 - 精选装', 'SKU_HT_001', '坚果', 68.00, 78.00, 150, '襄汾优质薄皮核桃，皮薄仁满，营养丰富。', '{"weight": "2斤", "type": "薄皮", "shell": "易剥"}', '["https://example.com/images/hetao_premium.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_013', 'farmer_004', '核桃仁 - 即食装', 'SKU_HT_002', '坚果', 88.00, 98.00, 100, '已去壳核桃仁，即食方便，适合办公室零食。', '{"weight": "1斤", "type": "核桃仁", "ready_to_eat": true}', '["https://example.com/images/hetaoren.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_014', 'farmer_004', '核桃 - 批发装', 'SKU_HT_003', '坚果', 180.00, 200.00, 80, '批发装核桃，5斤大包装，适合批发商。', '{"weight": "5斤", "type": "薄皮", "package": "批发"}', '["https://example.com/images/hetao_bulk.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 农户5的产品 (综合农产品)
INSERT INTO products (id, farmer_id, name, sku_code, category, price, original_price, stock, description, specs, images, is_active, is_featured, created_at, updated_at) VALUES
('prod_015', 'farmer_005', '有机小米 - 精品装', 'SKU_XM_001', '粮食', 48.00, 58.00, 200, '洪洞有机小米，无农药无化肥，营养健康。', '{"weight": "2斤", "type": "有机", "certification": "有机认证"}', '["https://example.com/images/xiaomi.jpg"]', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_016', 'farmer_005', '红枣 - 特级大枣', 'SKU_HZ_001', '干果', 58.00, 68.00, 150, '特级大红枣，个大肉厚，补血养颜。', '{"weight": "2斤", "grade": "特级", "size": "大"}', '["https://example.com/images/hongzao.jpg"]', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_017', 'farmer_005', '土蜂蜜 - 纯天然', 'SKU_FM_001', '蜂产品', 128.00, 148.00, 80, '纯天然土蜂蜜，农家自产，无添加。', '{"weight": "1斤", "type": "土蜂蜜", "natural": true}', '["https://example.com/images/fengmi.jpg"]', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_018', 'farmer_005', '黑木耳 - 野生', 'SKU_ME_001', '菌类', 78.00, 88.00, 100, '野生黑木耳，肉厚味美，营养价值高。', '{"weight": "0.5斤", "type": "野生", "origin": "山区"}', '["https://example.com/images/muer.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_019', 'farmer_005', '农家土鸡蛋', 'SKU_JD_001', '禽蛋', 38.00, 45.00, 300, '散养土鸡蛋，蛋黄金黄，营养丰富。', '{"quantity": "30枚", "type": "土鸡蛋", "free_range": true}', '["https://example.com/images/jidan.jpg"]', true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
('prod_020', 'farmer_005', '杂粮礼盒', 'SKU_ZL_001', '粮食', 168.00, 188.00, 60, '杂粮大礼包，包含小米、红豆、绿豆等多种杂粮。', '{"weight": "5斤", "type": "礼盒", "variety": "多种"}', '["https://example.com/images/zaliang_gift.jpg"]', true, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- ============================================================
-- 验证插入结果
-- ============================================================

SELECT '农户数量' as 统计项, COUNT(*) as 数量 FROM farmers
UNION ALL
SELECT '产品数量', COUNT(*) FROM products
UNION ALL
SELECT '在售产品', COUNT(*) FROM products WHERE is_active = true
UNION ALL
SELECT '精选产品', COUNT(*) FROM products WHERE is_featured = true;

-- 查看每个农户的产品数量
SELECT 
    f.name as 农户名称,
    f.county as 所在县,
    f.tier as 等级,
    COUNT(p.id) as 产品数量,
    SUM(p.stock) as 总库存
FROM farmers f
LEFT JOIN products p ON f.id = p.farmer_id
GROUP BY f.id, f.name, f.county, f.tier
ORDER BY 产品数量 DESC;

