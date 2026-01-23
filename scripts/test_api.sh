#!/bin/bash

# 智农链销API测试脚本

BASE_URL="http://localhost:8000"
API_PREFIX="/api/v1"

echo "=================================="
echo "   智农链销API测试"
echo "=================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    local expected_status=${5:-200}
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "测试 $TOTAL_TESTS: $description ... "
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$API_PREFIX$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$API_PREFIX$endpoint")
    fi
    
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (状态码: $status_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (期望: $expected_status, 实际: $status_code)"
        echo "响应内容: $body"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
}

# ====================================
# 1. 健康检查
# ====================================
echo "🏥 健康检查测试"
echo "=================================="
test_endpoint "GET" "/../health" "健康检查" "" 200

# ====================================
# 2. 农户管理API测试
# ====================================
echo "👨‍🌾 农户管理API测试"
echo "=================================="

# 2.1 注册农户
REGISTER_DATA='{
  "name": "测试农户",
  "phone": "13900000001",
  "password": "test123456",
  "email": "test@example.com",
  "province": "山西省",
  "city": "临汾市",
  "county": "蒲县",
  "village": "测试村"
}'
test_endpoint "POST" "/farmers/register" "农户注册" "$REGISTER_DATA" 201

# 2.2 登录农户
LOGIN_DATA='{
  "phone": "13800138000",
  "password": "demo123456"
}'
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d "$LOGIN_DATA" \
    "$BASE_URL$API_PREFIX/farmers/login")

TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓ 登录成功，获取Token${NC}"
    echo "Token: ${TOKEN:0:50}..."
    echo ""
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}✗ 登录失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 2.3 获取当前农户信息
test_endpoint "GET" "/farmers/me" "获取当前农户信息" "" 401  # 未带Token应该401

# ====================================
# 3. 产品管理API测试
# ====================================
echo "🍐 产品管理API测试"
echo "=================================="

# 3.1 获取产品列表（公开访问）
test_endpoint "GET" "/products?page=1&page_size=10" "获取产品列表" "" 200

# 3.2 获取产品类别
test_endpoint "GET" "/products/categories/list" "获取产品类别列表" "" 200

# ====================================
# 4. 服务生成API测试（需要Token）
# ====================================
if [ -n "$TOKEN" ]; then
    echo "🤖 服务生成API测试"
    echo "=================================="
    
    # 4.1 估算成本
    ESTIMATE_DATA='{
      "user_input": "我需要一个订单查询工具",
      "model": "gemini-2.5-pro"
    }'
    
    echo -n "测试: 估算服务生成成本 ... "
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "$ESTIMATE_DATA" \
        "$BASE_URL$API_PREFIX/services/estimate-cost")
    
    if echo "$RESPONSE" | grep -q "estimated_cost"; then
        echo -e "${GREEN}✓ PASS${NC}"
        echo "响应: $RESPONSE"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "响应: $RESPONSE"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
    
    # 4.2 启动服务生成（注意：这会真实调用LLM）
    echo -e "${YELLOW}⚠️  跳过实际服务生成测试（避免消耗API额度）${NC}"
    echo ""
fi

# ====================================
# 5. 统计数据API测试
# ====================================
if [ -n "$TOKEN" ]; then
    echo "📊 统计数据API测试"
    echo "=================================="
    
    echo -n "测试: 获取仪表盘数据 ... "
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    RESPONSE=$(curl -s \
        -H "Authorization: Bearer $TOKEN" \
        "$BASE_URL$API_PREFIX/_count"; then
        echo -e "${GREEN}✓ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
fi

# ====================================
# 测试总结
# ====================================
echo "=================================="
echo "测试总结"
echo "=================================="
echo "总测试数: $TOTAL_TESTS"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 部分测试失败${NC}"
    exit 1
fi
