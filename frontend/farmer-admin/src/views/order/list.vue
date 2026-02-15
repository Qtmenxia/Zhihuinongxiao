<template>
  <div class="order-list-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">订单管理</h2>
      <p class="page-subtitle">管理您的所有订单，跟踪订单状态</p>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card pending-card">
          <div class="stat-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待支付</div>
          </div>
          <div class="stat-bg-icon">
            <el-icon><Clock /></el-icon>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card paid-card">
          <div class="stat-icon">
            <el-icon><Wallet /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.paid }}</div>
            <div class="stat-label">待发货</div>
          </div>
          <div class="stat-bg-icon">
            <el-icon><Wallet /></el-icon>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card shipped-card">
          <div class="stat-icon">
            <el-icon><Van /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.shipped }}</div>
            <div class="stat-label">已发货</div>
          </div>
          <div class="stat-bg-icon">
            <el-icon><Van /></el-icon>
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <div class="stat-card completed-card">
          <div class="stat-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.completed }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <div class="stat-bg-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 搜索筛选区 -->
    <div class="search-section">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item>
          <el-input 
            v-model="searchForm.order_id" 
            placeholder="搜索订单编号"
            clearable
            @clear="handleSearch"
            prefix-icon="Search"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="searchForm.customer" 
            placeholder="客户姓名/手机号"
            clearable
            @clear="handleSearch"
            prefix-icon="User"
            style="width: 160px"
          />
        </el-form-item>
        <el-form-item>
          <el-select 
            v-model="searchForm.status" 
            placeholder="订单状态"
            clearable
            @change="handleSearch"
            style="width: 120px"
          >
            <el-option label="全部状态" value="" />
            <el-option label="待支付" value="PENDING" />
            <el-option label="已支付" value="PAID" />
            <el-option label="已发货" value="SHIPPED" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="已取消" value="CANCELLED" />
            <el-option label="已退款" value="REFUNDED" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleSearch"
            style="width: 240px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>导出
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 订单列表 -->
    <div class="order-list-section">
      <div class="section-header">
        <div class="header-left">
          <h3 class="section-title">订单列表</h3>
          <span class="order-count">共 {{ total }} 个订单</span>
        </div>
      </div>

      <div v-loading="loading" class="order-list-container">
        <!-- 订单卡片 -->
        <div 
          v-for="order in orderList" 
          :key="order.id" 
          class="order-card"
        >
          <!-- 订单头部 -->
          <div class="order-header">
            <div class="header-left">
              <span class="order-number">订单号：{{ order.id }}</span>
              <span class="order-time">
                <el-icon><Clock /></el-icon>
                {{ formatDate(order.created_at) }}
              </span>
            </div>
            <el-tag :type="getStatusType(order.status)" size="large" effect="dark">
              {{ getStatusText(order.status) }}
            </el-tag>
          </div>

          <!-- 订单主体 -->
          <div class="order-body">
            <!-- 左侧：商品列表 -->
            <div class="products-section">
              <div class="products-list">
                <div 
                  v-for="(item, index) in order.items" 
                  :key="index" 
                  class="product-item"
                >
                  <div class="product-image-wrapper">
                    <img 
                      :src="getProductImage(item)" 
                      :alt="item.product_name"
                      class="product-image"
                      @error="handleImageError"
                    />
                  </div>
                  <div class="product-details">
                    <div class="product-name">{{ item.product_name }}</div>
                    <div class="product-sku">SKU: {{ item.sku_code }}</div>
                    <div class="product-price-qty">
                      <span class="price">¥{{ item.price }}</span>
                      <span class="quantity">×{{ item.quantity }}</span>
                    </div>
                  </div>
                  <div class="product-subtotal">
                    ¥{{ (item.price * item.quantity).toFixed(2) }}
                  </div>
                </div>
              </div>
            </div>

            <!-- 中间：客户信息 -->
            <div class="customer-section">
              <div class="section-title-small">
                <el-icon><User /></el-icon>
                收货信息
              </div>
              <div class="customer-info">
                <div class="info-row">
                  <span class="label">收货人：</span>
                  <span class="value">{{ order.shipping_address?.name || '-' }}</span>
                </div>
                <div class="info-row">
                  <span class="label">联系电话：</span>
                  <span class="value">{{ order.shipping_address?.phone || '-' }}</span>
                </div>
                <div class="info-row">
                  <span class="label">收货地址：</span>
                  <span class="value">{{ formatAddress(order.shipping_address) }}</span>
                </div>
              </div>
            </div>

            <!-- 右侧：金额和操作 -->
            <div class="amount-actions-section">
              <div class="amount-details">
                <div class="amount-row">
                  <span class="label">商品金额</span>
                  <span class="value">¥{{ order.subtotal }}</span>
                </div>
                <div class="amount-row">
                  <span class="label">运费</span>
                  <span class="value">¥{{ order.shipping_fee }}</span>
                </div>
                <div v-if="order.discount > 0" class="amount-row discount-row">
                  <span class="label">优惠</span>
                  <span class="value">-¥{{ order.discount }}</span>
                </div>
                <div class="amount-total">
                  <span class="label">实付金额</span>
                  <span class="value">¥{{ order.total_amount }}</span>
                </div>
              </div>

              <div class="action-buttons">
                <el-button 
                  type="primary" 
                  plain
                  @click="handleViewDetail(order)"
                >
                  <el-icon><View /></el-icon>
                  查看详情
                </el-button>
                <el-button 
                  v-if="order.status === 'PAID'" 
                  type="success" 
                  @click="handleShip(order)"
                >
                  <el-icon><Van /></el-icon>
                  发货
                </el-button>
                <el-button 
                  v-if="order.status === 'PENDING'" 
                  type="danger" 
                  plain
                  @click="handleCancel(order)"
                >
                  <el-icon><Close /></el-icon>
                  取消订单
                </el-button>
                <el-button 
                  v-if="order.status === 'SHIPPED'" 
                  type="info" 
                  plain
                  @click="handleViewLogistics(order)"
                >
                  <el-icon><Location /></el-icon>
                  物流信息
                </el-button>
              </div>
            </div>
          </div>

          <!-- 订单备注 -->
          <div v-if="order.customer_note || order.farmer_note" class="order-footer">
            <div v-if="order.customer_note" class="note-item customer-note">
              <el-icon><ChatDotRound /></el-icon>
              <span class="note-label">客户备注：</span>
              <span class="note-content">{{ order.customer_note }}</span>
            </div>
            <div v-if="order.farmer_note" class="note-item farmer-note">
              <el-icon><Edit /></el-icon>
              <span class="note-label">商家备注：</span>
              <span class="note-content">{{ order.farmer_note }}</span>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && orderList.length === 0" 
          description="暂无订单数据"
          :image-size="200"
        >
          <el-button type="primary">刷新页面</el-button>
        </el-empty>

        <!-- 分页 -->
        <div v-if="total > 0" class="pagination-wrapper">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.page_size"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>

    <!-- 发货对话框 -->
    <el-dialog 
      v-model="shipDialogVisible" 
      title="订单发货" 
      width="500px"
    >
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="物流公司">
          <el-select v-model="shipForm.shipping_method" placeholder="请选择物流公司">
            <el-option label="顺丰快递" value="顺丰快递" />
            <el-option label="中通快递" value="中通快递" />
            <el-option label="圆通快递" value="圆通快递" />
            <el-option label="韵达快递" value="韵达快递" />
            <el-option label="申通快递" value="申通快递" />
            <el-option label="德邦物流" value="德邦物流" />
          </el-select>
        </el-form-item>
        <el-form-item label="物流单号">
          <el-input v-model="shipForm.tracking_number" placeholder="请输入物流单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmShip">确认发货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrderList, getOrderStats, shipOrder, cancelOrder, exportOrdersPDF } from '@/api/order'
import { getProductList } from '@/api/product'
import dayjs from 'dayjs'

const router = useRouter()

// 产品列表（用于匹配图片）
const productMap = ref(new Map())

// 统计数据
const stats = reactive({
  pending: 0,
  paid: 0,
  shipped: 0,
  completed: 0
})

// 搜索表单
const searchForm = reactive({
  order_id: '',
  customer: '',
  status: '',
  dateRange: null
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 10
})

// 数据
const loading = ref(false)
const orderList = ref([])
const total = ref(0)

// 发货对话框
const shipDialogVisible = ref(false)
const shipForm = reactive({
  order_id: '',
  shipping_method: '',
  tracking_number: ''
})

// 加载产品列表（用于匹配图片）
async function loadProducts() {
  try {
    const res = await getProductList({ page: 1, page_size: 1000 })
    const products = res.items || []
    
    // 创建产品名称到产品信息的映射
    productMap.value.clear()
    products.forEach(product => {
      productMap.value.set(product.name, product)
      // 也可以通过SKU匹配
      if (product.sku_code) {
        productMap.value.set(product.sku_code, product)
      }
    })
    
    console.log('Loaded products:', productMap.value.size)
  } catch (error) {
    console.error('Failed to load products:', error)
  }
}

// 加载订单列表
async function loadOrders() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    // 处理日期范围
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = dayjs(searchForm.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(searchForm.dateRange[1]).format('YYYY-MM-DD')
    }
    delete params.dateRange
    
    // 清理空参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const res = await getOrderList(params)
    orderList.value = res.items || []
    total.value = res.total || 0
    
    // 加载统计数据
    loadStats()
  } catch (error) {
    console.error('Failed to load orders:', error)
    ElMessage.error('加载订单列表失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
async function loadStats() {
  try {
    const res = await getOrderStats()
    stats.pending = res.pending_orders || 0
    stats.paid = res.paid_orders || 0
    stats.shipped = res.shipped_orders || 0
    stats.completed = res.completed_orders || 0
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

// 搜索
function handleSearch() {
  pagination.page = 1
  loadOrders()
}

// 重置
function handleReset() {
  searchForm.order_id = ''
  searchForm.customer = ''
  searchForm.status = ''
  searchForm.dateRange = null
  handleSearch()
}

// 分页变化
function handlePageChange(page) {
  pagination.page = page
  loadOrders()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  loadOrders()
}

// 查看详情
function handleViewDetail(order) {
  router.push(`/order/detail/${order.id}`)
}

// 发货
function handleShip(order) {
  shipForm.order_id = order.id
  shipForm.shipping_method = ''
  shipForm.tracking_number = ''
  shipDialogVisible.value = true
}

// 确认发货
async function confirmShip() {
  if (!shipForm.shipping_method || !shipForm.tracking_number) {
    ElMessage.warning('请填写完整的物流信息')
    return
  }
  
  try {
    await shipOrder(shipForm.order_id, {
      shipping_method: shipForm.shipping_method,
      tracking_number: shipForm.tracking_number
    })
    
    ElMessage.success('发货成功')
    shipDialogVisible.value = false
    loadOrders()
  } catch (error) {
    console.error('Failed to ship order:', error)
    ElMessage.error('发货失败')
  }
}

// 取消订单
async function handleCancel(order) {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入取消原因', '取消订单', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '请输入取消原因'
    })
    
    await cancelOrder(order.id, reason)
    ElMessage.success('订单已取消')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to cancel order:', error)
      ElMessage.error('取消订单失败')
    }
  }
}

// 查看物流
function handleViewLogistics(order) {
  if (order.tracking_number) {
    ElMessageBox.alert(
      `物流公司：${order.shipping_method || '未知'}\n物流单号：${order.tracking_number}`,
      '物流信息',
      {
        confirmButtonText: '确定'
      }
    )
  } else {
    ElMessage.info('暂无物流信息')
  }
}

// 导出
async function handleExport() {
  try {
    const params = { ...searchForm }
    
    // 处理日期范围
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = dayjs(searchForm.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(searchForm.dateRange[1]).format('YYYY-MM-DD')
    }
    delete params.dateRange
    
    // 清理空参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const blob = await exportOrdersPDF(params)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `订单列表_${dayjs().format('YYYYMMDD_HHmmss')}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Failed to export orders:', error)
    ElMessage.error('导出失败')
  }
}

// 格式化日期
function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 格式化地址
function formatAddress(address) {
  if (!address) return '-'
  return address.address || '-'
}

// 获取状态类型
function getStatusType(status) {
  const types = {
    PENDING: 'warning',
    PAID: 'primary',
    SHIPPED: 'info',
    COMPLETED: 'success',
    CANCELLED: 'info',
    REFUNDED: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
function getStatusText(status) {
  const texts = {
    PENDING: '待支付',
    PAID: '已支付',
    SHIPPED: '已发货',
    COMPLETED: '已完成',
    CANCELLED: '已取消',
    REFUNDED: '已退款'
  }
  return texts[status] || status
}

// 获取产品图片
function getProductImage(item) {
  // 1. 首先尝试从订单项中获取图片
  if (item.image && item.image.trim()) {
    return item.image
  }
  
  // 2. 通过产品名称匹配
  let product = productMap.value.get(item.product_name)
  
  // 3. 如果名称没匹配到，尝试通过SKU匹配
  if (!product && item.sku_code) {
    product = productMap.value.get(item.sku_code)
  }
  
  // 4. 如果找到产品且有图片
  if (product && product.images && Array.isArray(product.images) && product.images.length > 0) {
    const firstImage = product.images[0]
    
    // 如果已经是完整路径（以 / 或 http 开头），直接返回
    if (firstImage.startsWith('/') || firstImage.startsWith('http://') || firstImage.startsWith('https://')) {
      return firstImage
    }
    
    // 如果是相对路径，拼接基础URL
    return `/uploads/images/${firstImage}`
  }
  
  // 5. 使用占位图片
  return getPlaceholderImage(item.product_name)
}

// 生成带商品名称首字的占位图片
function getPlaceholderImage(productName) {
  const firstChar = productName ? productName.charAt(0) : '商'
  const colors = [
    { bg: '#667eea', text: '#ffffff' },
    { bg: '#f093fb', text: '#ffffff' },
    { bg: '#4facfe', text: '#ffffff' },
    { bg: '#43e97b', text: '#ffffff' },
    { bg: '#fa709a', text: '#ffffff' },
  ]
  const colorIndex = productName ? productName.charCodeAt(0) % colors.length : 0
  const color = colors[colorIndex]
  
  return `data:image/svg+xml;base64,${btoa(`
    <svg width="90" height="90" xmlns="http://www.w3.org/2000/svg">
      <rect width="90" height="90" fill="${color.bg}"/>
      <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="${color.text}" text-anchor="middle" dy=".35em">${firstChar}</text>
    </svg>
  `)}`
}

// 处理图片加载错误
function handleImageError(e) {
  // 获取商品名称（从父元素的兄弟元素中获取）
  const productItem = e.target.closest('.product-item')
  const productName = productItem?.querySelector('.product-name')?.textContent || '商品'
  
  // 使用占位图片替换失败的图片
  e.target.src = getPlaceholderImage(productName)
}

// 初始化
onMounted(async () => {
  // 先加载产品列表，用于匹配图片
  await loadProducts()
  // 再加载订单列表
  loadOrders()
})
</script>

<style lang="scss" scoped>
.order-list-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;

  // 页面标题
  .page-header {
    margin-bottom: 24px;

    .page-title {
      font-size: 28px;
      font-weight: 700;
      color: #1a1a1a;
      margin: 0 0 8px 0;
    }

    .page-subtitle {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  // 统计卡片
  .stats-row {
    margin-bottom: 24px;

    .stat-card {
      position: relative;
      padding: 24px;
      border-radius: 16px;
      background: #fff;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
      overflow: hidden;
      transition: all 0.3s ease;
      cursor: pointer;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
      }

      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 16px;
        position: relative;
        z-index: 2;

        .el-icon {
          font-size: 28px;
          color: #fff;
        }
      }

      .stat-content {
        position: relative;
        z-index: 2;

        .stat-value {
          font-size: 32px;
          font-weight: 700;
          color: #1a1a1a;
          line-height: 1;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
          font-weight: 500;
        }
      }

      .stat-bg-icon {
        position: absolute;
        right: -20px;
        bottom: -20px;
        opacity: 0.08;
        z-index: 1;

        .el-icon {
          font-size: 120px;
        }
      }

      &.pending-card {
        .stat-icon {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
      }

      &.paid-card {
        .stat-icon {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
      }

      &.shipped-card {
        .stat-icon {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
      }

      &.completed-card {
        .stat-icon {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
      }
    }
  }

  // 搜索区域
  .search-section {
    background: #fff;
    padding: 20px 24px;
    border-radius: 12px;
    margin-bottom: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);

    .search-form {
      margin: 0;

      :deep(.el-form-item) {
        margin-bottom: 0;
      }
    }
  }

  // 订单列表区域
  .order-list-section {
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;

      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;

        .section-title {
          font-size: 20px;
          font-weight: 600;
          color: #1a1a1a;
          margin: 0;
        }

        .order-count {
          padding: 4px 12px;
          background: #f0f2f5;
          border-radius: 12px;
          font-size: 13px;
          color: #606266;
          font-weight: 500;
        }
      }
    }

    .order-list-container {
      // 订单卡片
      .order-card {
        background: #fff;
        border-radius: 16px;
        margin-bottom: 16px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;

        &:hover {
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
          transform: translateY(-2px);
        }

        // 订单头部
        .order-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 24px;
          background: linear-gradient(135deg, #f5f7fa 0%, #f0f2f5 100%);
          border-bottom: 1px solid #e4e7ed;

          .header-left {
            display: flex;
            align-items: center;
            gap: 16px;

            .order-number {
              font-size: 15px;
              font-weight: 600;
              color: #303133;
            }

            .order-time {
              display: flex;
              align-items: center;
              gap: 4px;
              font-size: 13px;
              color: #909399;

              .el-icon {
                font-size: 14px;
              }
            }
          }
        }

        // 订单主体
        .order-body {
          display: grid;
          grid-template-columns: 2fr 1.2fr 1fr;
          gap: 24px;
          padding: 24px;

          @media (max-width: 1400px) {
            grid-template-columns: 1fr;
          }

          // 商品列表
          .products-section {
            .products-list {
              .product-item {
                display: flex;
                gap: 16px;
                padding: 12px;
                border-radius: 12px;
                background: #f9fafb;
                margin-bottom: 12px;
                transition: all 0.2s;

                &:last-child {
                  margin-bottom: 0;
                }

                &:hover {
                  background: #f0f2f5;
                }

                .product-image-wrapper {
                  width: 90px;
                  height: 90px;
                  border-radius: 10px;
                  overflow: hidden;
                  flex-shrink: 0;
                  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

                  .product-image {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    transition: transform 0.3s;

                    &:hover {
                      transform: scale(1.05);
                    }
                  }
                }

                .product-details {
                  flex: 1;
                  display: flex;
                  flex-direction: column;
                  justify-content: space-between;

                  .product-name {
                    font-size: 15px;
                    font-weight: 600;
                    color: #303133;
                    margin-bottom: 6px;
                    line-height: 1.4;
                  }

                  .product-sku {
                    font-size: 12px;
                    color: #909399;
                    margin-bottom: 8px;
                  }

                  .product-price-qty {
                    display: flex;
                    align-items: center;
                    gap: 12px;

                    .price {
                      font-size: 18px;
                      font-weight: 700;
                      color: #f56c6c;
                    }

                    .quantity {
                      font-size: 14px;
                      color: #909399;
                    }
                  }
                }

                .product-subtotal {
                  font-size: 16px;
                  font-weight: 600;
                  color: #303133;
                  align-self: center;
                }
              }
            }
          }

          // 客户信息
          .customer-section {
            .section-title-small {
              display: flex;
              align-items: center;
              gap: 6px;
              font-size: 14px;
              font-weight: 600;
              color: #606266;
              margin-bottom: 16px;

              .el-icon {
                font-size: 16px;
                color: #409eff;
              }
            }

            .customer-info {
              .info-row {
                display: flex;
                margin-bottom: 12px;
                font-size: 14px;

                &:last-child {
                  margin-bottom: 0;
                }

                .label {
                  color: #909399;
                  min-width: 70px;
                }

                .value {
                  color: #303133;
                  flex: 1;
                  word-break: break-all;
                }
              }
            }
          }

          // 金额和操作
          .amount-actions-section {
            display: flex;
            flex-direction: column;
            justify-content: space-between;

            .amount-details {
              background: #f9fafb;
              padding: 16px;
              border-radius: 12px;
              margin-bottom: 16px;

              .amount-row {
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                font-size: 14px;

                &:last-of-type {
                  margin-bottom: 0;
                }

                .label {
                  color: #606266;
                }

                .value {
                  color: #303133;
                  font-weight: 500;
                }

                &.discount-row .value {
                  color: #f56c6c;
                }
              }

              .amount-total {
                display: flex;
                justify-content: space-between;
                margin-top: 12px;
                padding-top: 12px;
                border-top: 2px dashed #e4e7ed;

                .label {
                  font-size: 15px;
                  font-weight: 600;
                  color: #303133;
                }

                .value {
                  font-size: 22px;
                  font-weight: 700;
                  color: #f56c6c;
                }
              }
            }

            .action-buttons {
              display: flex;
              flex-direction: column;
              gap: 10px;

              .el-button {
                width: 100%;
              }
            }
          }
        }

        // 订单备注
        .order-footer {
          padding: 16px 24px;
          background: #fffbf0;
          border-top: 1px solid #e4e7ed;

          .note-item {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 10px;
            font-size: 13px;

            &:last-child {
              margin-bottom: 0;
            }

            .el-icon {
              margin-top: 2px;
              font-size: 16px;
            }

            .note-label {
              font-weight: 600;
              color: #606266;
            }

            .note-content {
              flex: 1;
              color: #303133;
              line-height: 1.6;
            }

            &.customer-note .el-icon {
              color: #409eff;
            }

            &.farmer-note .el-icon {
              color: #67c23a;
            }
          }
        }
      }

      // 分页
      .pagination-wrapper {
        display: flex;
        justify-content: center;
        margin-top: 32px;
        padding: 20px;
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
      }
    }
  }
}
</style>
