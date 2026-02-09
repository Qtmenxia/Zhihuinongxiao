-- ============================================================
-- 智农链销 - 订单示例数据
-- 请在 DataGrip 中选中 zhinong_db 数据库后执行
-- ============================================================

-- ============================================================
-- 3. 插入订单数据 (15个订单，不同状态)
-- ============================================================

-- 已完成的订单
INSERT INTO orders (id, farmer_id, customer_id, items, subtotal, shipping_fee, discount, total_amount, payment_method, payment_transaction_id, paid_at, shipping_address, shipping_method, tracking_number, shipped_at, status, customer_note, completed_at, created_at, updated_at) VALUES
('order_001', 'farmer_001', 'customer_001', 
'[{"product_id": "prod_001", "product_name": "玉露香梨 - 精品礼盒装", "quantity": 2, "price": 88.00, "subtotal": 176.00}]',
176.00, 10.00, 0, 186.00, 'wechat', 'WX20240101123456', 
'2024-01-15 10:30:00', 
'{"name": "张三", "phone": "13900001111", "province": "北京市", "city": "北京市", "district": "朝阳区", "address": "朝阳路123号", "zipcode": "100000"}',
'顺丰快递', 'SF1234567890', '2024-01-15 14:00:00', 'completed', '请尽快发货，谢谢！', '2024-01-18 16:00:00',
'2024-01-15 10:30:00', '2024-01-18 16:00:00'),

('order_002', 'farmer_002', 'customer_002',
'[{"product_id": "prod_005", "product_name": "红富士苹果 - 特级果", "quantity": 3, "price": 68.00, "subtotal": 204.00}]',
204.00, 15.00, 10.00, 209.00, 'alipay', 'ALI20240102234567',
'2024-01-16 09:20:00',
'{"name": "李四", "phone": "13900002222", "province": "上海市", "city": "上海市", "district": "浦东新区", "address": "世纪大道456号", "zipcode": "200000"}',
'中通快递', 'ZT9876543210', '2024-01-16 15:00:00', 'completed', '苹果很新鲜', '2024-01-20 10:00:00',
'2024-01-16 09:20:00', '2024-01-20 10:00:00'),

('order_003', 'farmer_003', 'customer_003',
'[{"product_id": "prod_011", "product_name": "壶口冰糖心苹果", "quantity": 1, "price": 78.00, "subtotal": 78.00}]',
78.00, 12.00, 0, 90.00, 'wechat', 'WX20240103345678',
'2024-01-17 14:15:00',
'{"name": "王五", "phone": "13900003333", "province": "广东省", "city": "深圳市", "district": "南山区", "address": "科技园路789号", "zipcode": "518000"}',
'顺丰快递', 'SF2345678901', '2024-01-17 16:00:00', 'completed', null, '2024-01-21 11:00:00',
'2024-01-17 14:15:00', '2024-01-21 11:00:00'),

('order_004', 'farmer_005', 'customer_004',
'[{"product_id": "prod_017", "product_name": "土蜂蜜 - 纯天然", "quantity": 2, "price": 128.00, "subtotal": 256.00}, {"product_id": "prod_015", "product_name": "有机小米 - 精品装", "quantity": 1, "price": 48.00, "subtotal": 48.00}]',
304.00, 15.00, 20.00, 299.00, 'alipay', 'ALI20240104456789',
'2024-01-18 11:30:00',
'{"name": "赵六", "phone": "13900004444", "province": "浙江省", "city": "杭州市", "district": "西湖区", "address": "西湖路101号", "zipcode": "310000"}',
'韵达快递', 'YD3456789012', '2024-01-18 15:00:00', 'completed', '包装很好', '2024-01-22 09:00:00',
'2024-01-18 11:30:00', '2024-01-22 09:00:00'),

-- 已发货的订单
('order_005', 'farmer_001', 'customer_005',
'[{"product_id": "prod_002", "product_name": "玉露香梨 - 家庭装", "quantity": 2, "price": 58.00, "subtotal": 116.00}]',
116.00, 10.00, 0, 126.00, 'wechat', 'WX20240105567890',
'2024-02-01 10:00:00',
'{"name": "孙七", "phone": "13900005555", "province": "江苏省", "city": "南京市", "district": "鼓楼区", "address": "中山路202号", "zipcode": "210000"}',
'圆通快递', 'YT4567890123', '2024-02-01 14:00:00', 'shipped', null, null,
'2024-02-01 10:00:00', '2024-02-01 14:00:00'),

('order_006', 'farmer_002', 'customer_006',
'[{"product_id": "prod_007", "product_name": "红富士苹果 - 礼盒装", "quantity": 1, "price": 128.00, "subtotal": 128.00}]',
128.00, 15.00, 0, 143.00, 'alipay', 'ALI20240106678901',
'2024-02-02 09:30:00',
'{"name": "周八", "phone": "13900006666", "province": "四川省", "city": "成都市", "district": "武侯区", "address": "天府大道303号", "zipcode": "610000"}',
'顺丰快递', 'SF5678901234', '2024-02-02 15:00:00', 'shipped', '送礼用，请包装好', null,
'2024-02-02 09:30:00', '2024-02-02 15:00:00'),

('order_007', 'farmer_005', 'customer_007',
'[{"product_id": "prod_020", "product_name": "杂粮礼盒", "quantity": 1, "price": 168.00, "subtotal": 168.00}]',
168.00, 12.00, 10.00, 170.00, 'wechat', 'WX20240107789012',
'2024-02-03 13:20:00',
'{"name": "吴九", "phone": "13900007777", "province": "湖北省", "city": "武汉市", "district": "江汉区", "address": "解放大道404号", "zipcode": "430000"}',
'中通快递', 'ZT6789012345', '2024-02-03 16:00:00', 'shipped', null, null,
'2024-02-03 13:20:00', '2024-02-03 16:00:00'),

-- 已支付待发货的订单
('order_008', 'farmer_001', 'customer_008',
'[{"product_id": "prod_004", "product_name": "玉露香梨 - 批发装", "quantity": 3, "price": 180.00, "subtotal": 540.00}]',
540.00, 20.00, 30.00, 530.00, 'alipay', 'ALI20240108890123',
'2024-02-05 10:15:00',
'{"name": "郑十", "phone": "13900008888", "province": "河南省", "city": "郑州市", "district": "金水区", "address": "花园路505号", "zipcode": "450000"}',
'德邦物流', null, null, 'paid', '批发订单，请尽快发货', null,
'2024-02-05 10:15:00', '2024-02-05 10:15:00'),

('order_009', 'farmer_003', 'customer_009',
'[{"product_id": "prod_009", "product_name": "壶口红苹果 - 精品装", "quantity": 2, "price": 55.00, "subtotal": 110.00}]',
110.00, 12.00, 0, 122.00, 'wechat', 'WX20240109901234',
'2024-02-06 11:00:00',
'{"name": "冯十一", "phone": "13900009999", "province": "陕西省", "city": "西安市", "district": "雁塔区", "address": "小寨路606号", "zipcode": "710000"}',
'顺丰快递', null, null, 'paid', null, null,
'2024-02-06 11:00:00', '2024-02-06 11:00:00'),

('order_010', 'farmer_004', 'customer_010',
'[{"product_id": "prod_012", "product_name": "薄皮核桃 - 精选装", "quantity": 2, "price": 68.00, "subtotal": 136.00}, {"product_id": "prod_013", "product_name": "核桃仁 - 即食装", "quantity": 1, "price": 88.00, "subtotal": 88.00}]',
224.00, 15.00, 15.00, 224.00, 'alipay', 'ALI20240110012345',
'2024-02-07 09:45:00',
'{"name": "陈十二", "phone": "13900010000", "province": "山东省", "city": "济南市", "district": "历下区", "address": "泉城路707号", "zipcode": "250000"}',
'中通快递', null, null, 'paid', '核桃要新鲜的', null,
'2024-02-07 09:45:00', '2024-02-07 09:45:00'),

-- 待支付的订单
('order_011', 'farmer_002', 'customer_011',
'[{"product_id": "prod_006", "product_name": "红富士苹果 - 一级果", "quantity": 2, "price": 48.00, "subtotal": 96.00}]',
96.00, 10.00, 0, 106.00, null, null, null,
'{"name": "楚十三", "phone": "13900011111", "province": "湖南省", "city": "长沙市", "district": "岳麓区", "address": "岳麓大道808号", "zipcode": "410000"}',
null, null, null, 'pending', null, null,
'2024-02-08 14:30:00', '2024-02-08 14:30:00'),

('order_012', 'farmer_005', 'customer_012',
'[{"product_id": "prod_016", "product_name": "红枣 - 特级大枣", "quantity": 1, "price": 58.00, "subtotal": 58.00}]',
58.00, 10.00, 0, 68.00, null, null, null,
'{"name": "卫十四", "phone": "13900012222", "province": "安徽省", "city": "合肥市", "district": "蜀山区", "address": "长江西路909号", "zipcode": "230000"}',
null, null, null, 'pending', null, null,
'2024-02-08 15:00:00', '2024-02-08 15:00:00'),

-- 已取消的订单
('order_013', 'farmer_001', 'customer_013',
'[{"product_id": "prod_003", "product_name": "玉露香梨 - 尝鲜装", "quantity": 1, "price": 28.00, "subtotal": 28.00}]',
28.00, 10.00, 0, 38.00, null, null, null,
'{"name": "蒋十五", "phone": "13900013333", "province": "江西省", "city": "南昌市", "district": "东湖区", "address": "八一大道1010号", "zipcode": "330000"}',
null, null, null, 'cancelled', '不想要了', null,
'2024-02-07 16:00:00', '2024-02-07 16:30:00'),

-- 已退款的订单
('order_014', 'farmer_003', 'customer_014',
'[{"product_id": "prod_010", "product_name": "壶口苹果 - 家庭装", "quantity": 2, "price": 38.00, "subtotal": 76.00}]',
76.00, 10.00, 0, 86.00, 'wechat', 'WX20240108111111',
'2024-02-04 10:00:00',
'{"name": "沈十六", "phone": "13900014444", "province": "福建省", "city": "福州市", "district": "鼓楼区", "address": "五一路1111号", "zipcode": "350000"}',
'圆通快递', 'YT7890123456', '2024-02-04 14:00:00', 'refunded', '收到的苹果有破损', null,
'2024-02-04 10:00:00', '2024-02-06 10:00:00'),

('order_015', 'farmer_002', 'customer_015',
'[{"product_id": "prod_008", "product_name": "红富士苹果 - 果汁专用", "quantity": 3, "price": 35.00, "subtotal": 105.00}]',
105.00, 12.00, 0, 117.00, 'alipay', 'ALI20240109222222',
'2024-02-05 11:30:00',
'{"name": "韩十七", "phone": "13900015555", "province": "广西", "city": "南宁市", "district": "青秀区", "address": "民族大道1212号", "zipcode": "530000"}',
null, null, null, 'refunded', '地址填错了，申请退款', null,
'2024-02-05 11:30:00', '2024-02-05 14:00:00');

-- ============================================================
-- 验证订单数据
-- ============================================================

SELECT '订单总数' as 统计项, COUNT(*) as 数量 FROM orders
UNION ALL
SELECT '待支付订单', COUNT(*) FROM orders WHERE status = 'pending'
UNION ALL
SELECT '已支付订单', COUNT(*) FROM orders WHERE status = 'paid'
UNION ALL
SELECT '已发货订单', COUNT(*) FROM orders WHERE status = 'shipped'
UNION ALL
SELECT '已完成订单', COUNT(*) FROM orders WHERE status = 'completed'
UNION ALL
SELECT '已取消订单', COUNT(*) FROM orders WHERE status = 'cancelled'
UNION ALL
SELECT '已退款订单', COUNT(*) FROM orders WHERE status = 'refunded';

-- 查看订单金额统计
SELECT 
    status as 订单状态,
    COUNT(*) as 订单数量,
    SUM(total_amount) as 总金额,
    AVG(total_amount) as 平均金额
FROM orders
GROUP BY status
ORDER BY 
    CASE status
        WHEN 'completed' THEN 1
        WHEN 'shipped' THEN 2
        WHEN 'paid' THEN 3
        WHEN 'pending' THEN 4
        WHEN 'cancelled' THEN 5
        WHEN 'refunded' THEN 6
    END;

-- 查看每个农户的订单统计
SELECT 
    f.name as 农户名称,
    COUNT(o.id) as 订单数量,
    SUM(CASE WHEN o.status = 'completed' THEN o.total_amount ELSE 0 END) as 已完成金额,
    SUM(CASE WHEN o.status IN ('paid', 'shipped') THEN o.total_amount ELSE 0 END) as 进行中金额
FROM farmers f
LEFT JOIN orders o ON f.id = o.farmer_id
GROUP BY f.id, f.name
ORDER BY 订单数量 DESC;

