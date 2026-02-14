<template>
  <div class="order-list">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pending }}</div>
              <div class="stat-label">待支付</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon paid">
              <el-icon><Wallet /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.paid }}</div>
              <div class="stat-label">待发货</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon shipped">
              <el-icon><Van /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.shipped }}</div>
              <div class="stat-label">已发货</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.completed }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索筛选区 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="订单编号">
          <el-input 
            v-model="searchForm.order_id" 
            placeholder="请输入订单编号"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="客户信息">
          <el-input 
            v-model="searchForm.customer" 
            placeholder="客户姓名/手机号"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select 
            v-model="searchForm.status" 
            placeholder="全部状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="待支付" value="PENDING" />
            <el-option label="已支付" value="PAID" />
            <el-option label="已发货" value="SHIPPED" />
            <el-option label="已完成" value="COMPLETED" />
            <el-option label="已取消" value="CANCELLED" />
            <el-option label="已退款" value="REFUNDED" />
          </el-select>
        </el-form-item>
        <el-form-item label="下单时间">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 订单列表 -->
    <el-card class="order-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">订单列表</span>
            <el-tag type="info" class="count-tag">共 {{ total }} 个订单</el-tag>
          </div>
          <div class="header-right">
            <el-button type="success" @click="handleExport">
              <el-icon><Download /></el-icon>导出订单
            </el-button>
          </div>
        </div>
      </template>

      <div v-loading="loading">
        <!-- 订单列表 -->
        <div class="order-list-container">
          <div 
            v-for="order in orderList" 
            :key="order.id" 
            class="order-item"
          >
            <!-- 订单头部 -->
            <div class="order-header">
              <div class="order-info">
                <span class="order-id">订单号：{{ order.id }}</span>
                <span class="order-time">{{ formatDate(order.created_at) }}</span>
              </div>
              <el-tag :type="getStatusType(order.status)" size="large">
                {{ getStatusText(order.status) }}
              </el-tag>
            </div>

            <!-- 订单内容 -->
            <div class="order-content">
              <!-- 商品信息 -->
              <div class="order-products">
                <div 
                  v-for="(item, index) in order.items" 
                  :key="index" 
                  class="product-item"
                >
                  <div class="product-image">
                    <img 
                      :src="getProductImage(item)" 
                      :alt="item.product_name"
                      @error="handleImageError"
                    />
                  </div>
                  <div class="product-info">
                    <div class="product-name">{{ item.product_name }}</div>
                    <div class="product-spec">
                      <span class="price">¥{{ item.price }}</span>
                      <span class="quantity">x{{ item.quantity }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 客户信息 -->
              <div class="order-customer">
                <div class="customer-name">{{ order.shipping_address?.name || '-' }}</div>
                <div class="customer-phone">{{ order.shipping_address?.phone || '-' }}</div>
                <div class="customer-address">
                  {{ formatAddress(order.shipping_address) }}
                </div>
              </div>

              <!-- 订单金额 -->
              <div class="order-amount">
                <div class="amount-item">
                  <span class="label">商品金额：</span>
                  <span class="value">¥{{ order.subtotal }}</span>
                </div>
                <div class="amount-item">
                  <span class="label">运费：</span>
                  <span class="value">¥{{ order.shipping_fee }}</span>
                </div>
                <div v-if="order.discount > 0" class="amount-item">
                  <span class="label">优惠：</span>
                  <span class="value discount">-¥{{ order.discount }}</span>
                </div>
                <div class="amount-total">
                  <span class="label">实付金额：</span>
                  <span class="value">¥{{ order.total_amount }}</span>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="order-actions">
                <el-button 
                  type="primary" 
                  link 
                  @click="handleViewDetail(order)"
                >
                  查看详情
                </el-button>
                <el-button 
                  v-if="order.status === 'PAID'" 
                  type="success" 
                  @click="handleShip(order)"
                >
                  <el-icon><Van /></el-icon>发货
                </el-button>
                <el-button 
                  v-if="order.status === 'PENDING'" 
                  type="danger" 
                  plain
                  @click="handleCancel(order)"
                >
                  取消订单
                </el-button>
                <el-button 
                  v-if="order.status === 'SHIPPED'" 
                  type="primary" 
                  plain
                  @click="handleViewLogistics(order)"
                >
                  <el-icon><Location /></el-icon>物流信息
                </el-button>
              </div>
            </div>

            <!-- 订单备注 -->
            <div v-if="order.customer_note || order.farmer_note" class="order-notes">
              <div v-if="order.customer_note" class="note-item">
                <el-icon><ChatDotRound /></el-icon>
                <span class="note-label">客户备注：</span>
                <span class="note-content">{{ order.customer_note }}</span>
              </div>
              <div v-if="order.farmer_note" class="note-item">
                <el-icon><Edit /></el-icon>
                <span class="note-label">商家备注：</span>
                <span class="note-content">{{ order.farmer_note }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && orderList.length === 0" 
          description="暂无订单数据"
        />

        <!-- 分页 -->
        <div v-if="total > 0" class="pagination">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.page_size"
            :page-sizes="[10, 20, 50, 100]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </el-card>

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
import dayjs from 'dayjs'

const router = useRouter()

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
  return `${address.province || ''} ${address.city || ''} ${address.district || ''} ${address.detail || ''}`
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
  if (item.image && item.image.trim()) {
    return item.image
  }
  // 使用 base64 占位图片，避免网络请求失败
  return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjgwIiBoZWlnaHQ9IjgwIiBmaWxsPSIjZjVmN2ZhIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzkwOTM5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPuWVhuWTgTwvdGV4dD48L3N2Zz4='
}

// 处理图片加载错误
function handleImageError(e) {
  // 使用 base64 占位图片替换失败的图片
  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHJlY3Qgd2lkdGg9IjgwIiBoZWlnaHQ9IjgwIiBmaWxsPSIjZjVmN2ZhIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzkwOTM5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPuWVhuWTgTwvdGV4dD48L3N2Zz4='
}

// 初始化
onMounted(() => {
  loadOrders()
})
</script>

<style lang="scss" scoped>
.order-list {
  .stats-row {
    margin-bottom: 20px;
    
    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        
        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;
          
          .el-icon {
            font-size: 24px;
            color: #fff;
          }
          
          &.pending {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }
          
          &.paid {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }
          
          &.shipped {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
          }
          
          &.completed {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }
        }
        
        .stat-info {
          .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #303133;
          }
          
          .stat-label {
            font-size: 14px;
            color: #909399;
            margin-top: 4px;
          }
        }
      }
    }
  }
  
  .search-card {
    margin-bottom: 20px;
    
    .search-form {
      margin-bottom: 0;
    }
  }
  
  .order-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .title {
          font-size: 16px;
          font-weight: 600;
        }
        
        .count-tag {
          font-size: 12px;
        }
      }
    }
    
    .order-list-container {
      .order-item {
        border: 1px solid #e4e7ed;
        border-radius: 8px;
        margin-bottom: 16px;
        overflow: hidden;
        transition: all 0.3s;
        
        &:hover {
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }
        
        .order-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          background: #f5f7fa;
          border-bottom: 1px solid #e4e7ed;
          
          .order-info {
            display: flex;
            gap: 20px;
            
            .order-id {
              font-weight: 600;
              color: #303133;
            }
            
            .order-time {
              color: #909399;
              font-size: 14px;
            }
          }
        }
        
        .order-content {
          display: grid;
          grid-template-columns: 2fr 1fr 1fr 120px;
          gap: 20px;
          padding: 20px;
          align-items: center;
          
          @media (max-width: 1200px) {
            grid-template-columns: 1fr;
          }
          
          .order-products {
            .product-item {
              display: flex;
              gap: 12px;
              margin-bottom: 12px;
              
              &:last-child {
                margin-bottom: 0;
              }
              
              .product-image {
                width: 80px;
                height: 80px;
                border-radius: 4px;
                overflow: hidden;
                flex-shrink: 0;
                
                img {
                  width: 100%;
                  height: 100%;
                  object-fit: cover;
                }
              }
              
              .product-info {
                flex: 1;
                
                .product-name {
                  font-size: 14px;
                  color: #303133;
                  margin-bottom: 8px;
                  overflow: hidden;
                  text-overflow: ellipsis;
                  white-space: nowrap;
                }
                
                .product-spec {
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                  
                  .price {
                    font-size: 16px;
                    font-weight: 600;
                    color: #f56c6c;
                  }
                  
                  .quantity {
                    color: #909399;
                  }
                }
              }
            }
          }
          
          .order-customer {
            .customer-name {
              font-weight: 600;
              color: #303133;
              margin-bottom: 4px;
            }
            
            .customer-phone {
              color: #606266;
              font-size: 14px;
              margin-bottom: 4px;
            }
            
            .customer-address {
              color: #909399;
              font-size: 13px;
              line-height: 1.5;
            }
          }
          
          .order-amount {
            .amount-item {
              display: flex;
              justify-content: space-between;
              margin-bottom: 4px;
              font-size: 14px;
              
              .label {
                color: #606266;
              }
              
              .value {
                color: #303133;
                
                &.discount {
                  color: #f56c6c;
                }
              }
            }
            
            .amount-total {
              display: flex;
              justify-content: space-between;
              margin-top: 8px;
              padding-top: 8px;
              border-top: 1px dashed #e4e7ed;
              
              .label {
                font-weight: 600;
                color: #303133;
              }
              
              .value {
                font-size: 18px;
                font-weight: 700;
                color: #f56c6c;
              }
            }
          }
          
          .order-actions {
            display: flex;
            flex-direction: column;
            gap: 8px;
          }
        }
        
        .order-notes {
          padding: 12px 20px;
          background: #fef0f0;
          border-top: 1px solid #e4e7ed;
          
          .note-item {
            display: flex;
            align-items: flex-start;
            gap: 8px;
            margin-bottom: 8px;
            font-size: 13px;
            
            &:last-child {
              margin-bottom: 0;
            }
            
            .el-icon {
              color: #f56c6c;
              margin-top: 2px;
            }
            
            .note-label {
              color: #606266;
              font-weight: 600;
            }
            
            .note-content {
              color: #303133;
              flex: 1;
            }
          }
        }
      }
    }
    
    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}
</style>
