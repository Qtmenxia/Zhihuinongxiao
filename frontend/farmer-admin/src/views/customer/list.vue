<template>
  <div class="customer-list">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon total">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_customers }}</div>
              <div class="stat-label">总客户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon new">
              <el-icon><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.new_customers_this_month }}</div>
              <div class="stat-label">本月新增</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon active">
              <el-icon><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.active_customers }}</div>
              <div class="stat-label">活跃客户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon vip">
              <el-icon><Medal /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.vip_customers }}</div>
              <div class="stat-label">VIP客户</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索筛选区 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="客户姓名">
          <el-input 
            v-model="searchForm.name" 
            placeholder="请输入客户姓名"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input 
            v-model="searchForm.phone" 
            placeholder="请输入手机号"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="客户等级">
          <el-select 
            v-model="searchForm.level" 
            placeholder="全部等级"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="普通客户" value="普通客户" />
            <el-option label="VIP客户" value="VIP客户" />
            <el-option label="黄金客户" value="黄金客户" />
            <el-option label="钻石客户" value="钻石客户" />
          </el-select>
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

    <!-- 客户列表 -->
    <el-card class="customer-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">客户列表</span>
            <el-tag type="info" class="count-tag">共 {{ total }} 位客户</el-tag>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>添加客户
            </el-button>
            <el-button type="success" @click="handleExport">
              <el-icon><Download /></el-icon>导出客户
            </el-button>
          </div>
        </div>
      </template>

      <div v-loading="loading">
        <!-- 客户表格 -->
        <el-table :data="customerList" stripe>
          <el-table-column prop="id" label="客户编号" width="150" />
          <el-table-column prop="name" label="客户姓名" width="120" />
          <el-table-column prop="phone" label="手机号" width="130" />
          <el-table-column label="地址" min-width="200">
            <template #default="{ row }">
              {{ formatAddress(row) }}
            </template>
          </el-table-column>
          <el-table-column prop="level" label="客户等级" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.level)">{{ row.level }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_orders" label="订单数" width="100" align="center" />
          <el-table-column label="累计消费" width="120" align="right">
            <template #default="{ row }">
              <span class="amount">¥{{ row.total_amount?.toFixed(2) || '0.00' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="注册时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleView(row)">查看</el-button>
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 空状态 -->
        <el-empty 
          v-if="!loading && customerList.length === 0" 
          description="暂无客户数据"
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

    <!-- 客户详情/编辑弹窗 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="600px"
    >
      <el-form 
        ref="formRef"
        :model="currentCustomer" 
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="客户姓名" prop="name">
          <el-input 
            v-model="currentCustomer.name" 
            :disabled="dialogMode === 'view'" 
            placeholder="请输入客户姓名"
          />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input 
            v-model="currentCustomer.phone" 
            :disabled="dialogMode === 'view'" 
            placeholder="请输入手机号"
          />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input 
            v-model="currentCustomer.email" 
            :disabled="dialogMode === 'view'" 
            placeholder="请输入邮箱（可选）"
          />
        </el-form-item>
        <el-form-item label="省份" prop="province">
          <el-input 
            v-model="currentCustomer.province" 
            :disabled="dialogMode === 'view'" 
            placeholder="请输入省份"
          />
        </el-form-item>
        <el-form-item label="城市" prop="city">
          <el-input 
            v-model="currentCustomer.city" 
            :disabled="dialogMode === 'view'" 
            placeholder="请输入城市"
          />
        </el-form-item>
        <el-form-item label="区县" prop="district">
          <el-input 
            v-model="currentCustomer.district" 
            :disabled="dialogMode === 'view'" 
            placeholder="请输入区县"
          />
        </el-form-item>
        <el-form-item label="详细地址" prop="address">
          <el-input 
            v-model="currentCustomer.address" 
            type="textarea"
            :rows="3"
            :disabled="dialogMode === 'view'" 
            placeholder="请输入详细地址"
          />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'edit'" label="客户等级" prop="level">
          <el-select v-model="currentCustomer.level" placeholder="请选择客户等级">
            <el-option label="普通客户" value="普通客户" />
            <el-option label="VIP客户" value="VIP客户" />
            <el-option label="黄金客户" value="黄金客户" />
            <el-option label="钻石客户" value="钻石客户" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="currentCustomer.remark" 
            type="textarea"
            :rows="3"
            :disabled="dialogMode === 'view'" 
            placeholder="请输入备注信息（可选）"
          />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'view'" label="订单数">
          <span>{{ currentCustomer.total_orders || 0 }}</span>
        </el-form-item>
        <el-form-item v-if="dialogMode === 'view'" label="累计消费">
          <span class="amount">¥{{ currentCustomer.total_amount?.toFixed(2) || '0.00' }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button v-if="dialogMode !== 'view'" type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  getCustomerList, 
  getCustomerStats,
  createCustomer, 
  updateCustomer,
  deleteCustomer,
  exportCustomersPDF
} from '@/api/customer'
import dayjs from 'dayjs'

// 统计数据
const stats = reactive({
  total_customers: 0,
  new_customers_this_month: 0,
  active_customers: 0,
  vip_customers: 0
})

// 搜索表单
const searchForm = reactive({
  name: '',
  phone: '',
  level: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 10
})

// 数据
const loading = ref(false)
const customerList = ref([])
const total = ref(0)

// 弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogMode = ref('view') // view | edit | add
const currentCustomer = ref({})
const formRef = ref(null)

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入客户姓名', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ]
}

// 加载客户列表
async function loadCustomers() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    // 清理空参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const res = await getCustomerList(params)
    customerList.value = res.items || []
    total.value = res.total || 0
    
    // 加载统计数据
    loadStats()
  } catch (error) {
    console.error('Failed to load customers:', error)
    ElMessage.error('加载客户列表失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
async function loadStats() {
  try {
    const res = await getCustomerStats()
    Object.assign(stats, res)
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

// 搜索
function handleSearch() {
  pagination.page = 1
  loadCustomers()
}

// 重置
function handleReset() {
  searchForm.name = ''
  searchForm.phone = ''
  searchForm.level = ''
  handleSearch()
}

// 分页变化
function handlePageChange(page) {
  pagination.page = page
  loadCustomers()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  loadCustomers()
}

// 添加客户
function handleAdd() {
  dialogMode.value = 'add'
  dialogTitle.value = '添加客户'
  currentCustomer.value = {}
  dialogVisible.value = true
}

// 查看客户
function handleView(row) {
  dialogMode.value = 'view'
  dialogTitle.value = '客户详情'
  currentCustomer.value = { ...row }
  dialogVisible.value = true
}

// 编辑客户
function handleEdit(row) {
  dialogMode.value = 'edit'
  dialogTitle.value = '编辑客户'
  currentCustomer.value = { ...row }
  dialogVisible.value = true
}

// 保存
async function handleSave() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      if (dialogMode.value === 'add') {
        await createCustomer(currentCustomer.value)
        ElMessage.success('添加成功')
      } else {
        await updateCustomer(currentCustomer.value.id, currentCustomer.value)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      loadCustomers()
    } catch (error) {
      console.error('Failed to save customer:', error)
      ElMessage.error('操作失败')
    }
  })
}

// 删除客户
async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除客户"${row.name}"吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteCustomer(row.id)
    ElMessage.success('删除成功')
    loadCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete customer:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 导出
async function handleExport() {
  try {
    const params = { ...searchForm }
    
    // 清理空参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const blob = await exportCustomersPDF(params)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `客户列表_${dayjs().format('YYYYMMDD_HHmmss')}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Failed to export customers:', error)
    ElMessage.error('导出失败')
  }
}

// 格式化日期
function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 格式化地址
function formatAddress(customer) {
  const parts = [customer.province, customer.city, customer.district, customer.address]
  return parts.filter(p => p).join(' ') || '-'
}

// 获取等级类型
function getLevelType(level) {
  const types = {
    '普通客户': '',
    'VIP客户': 'warning',
    '黄金客户': 'warning',
    '钻石客户': 'danger'
  }
  return types[level] || ''
}

// 初始化
onMounted(() => {
  loadCustomers()
})
</script>

<style lang="scss" scoped>
.customer-list {
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
          
          &.total {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }
          
          &.new {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }
          
          &.active {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }
          
          &.vip {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
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
  
  .customer-card {
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
      
      .header-right {
        display: flex;
        gap: 10px;
      }
    }
    
    .amount {
      color: #f56c6c;
      font-weight: 600;
    }
    
    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}
</style>
