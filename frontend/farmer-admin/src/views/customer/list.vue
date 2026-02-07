<template>
  <div class="customer-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>客户管理</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">添加客户</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="客户名称">
          <el-input v-model="searchForm.name" placeholder="请输入客户名称" clearable />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="searchForm.phone" placeholder="请输入手机号" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="customerList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="客户名称" min-width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="orderCount" label="订单数" width="100" align="center" />
        <el-table-column prop="totalAmount" label="累计消费" width="120" align="right">
          <template #default="{ row }">
            ¥{{ row.totalAmount?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="注册时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 客户详情/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="currentCustomer" label-width="80px">
        <el-form-item label="客户名称">
          <el-input v-model="currentCustomer.name" :disabled="dialogMode === 'view'" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="currentCustomer.phone" :disabled="dialogMode === 'view'" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="currentCustomer.address" type="textarea" :disabled="dialogMode === 'view'" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="currentCustomer.remark" type="textarea" :disabled="dialogMode === 'view'" />
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
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getCustomerList, createCustomer, updateCustomer } from '@/api/customer'

// 搜索表单
const searchForm = reactive({
  name: '',
  phone: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 数据
const loading = ref(false)
const customerList = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogMode = ref('view') // view | edit | add
const currentCustomer = ref({})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取客户列表
const fetchCustomerList = async () => {
  loading.value = true
  try {
    const res = await getCustomerList({
      ...searchForm,
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    customerList.value = res.data?.items || []
    pagination.total = res.data?.total || 0
  } catch (error) {
    console.error('获取客户列表失败:', error)
    // 使用模拟数据
    customerList.value = [
      { id: 1, name: '张三', phone: '13800138001', address: '山西省临汾市蒲县', orderCount: 5, totalAmount: 1250.00, createdAt: '2024-01-15T10:30:00Z' },
      { id: 2, name: '李四', phone: '13800138002', address: '山西省临汾市洪洞县', orderCount: 3, totalAmount: 680.50, createdAt: '2024-01-20T14:20:00Z' },
      { id: 3, name: '王五', phone: '13800138003', address: '北京市朝阳区', orderCount: 8, totalAmount: 2350.00, createdAt: '2024-02-01T09:15:00Z' },
    ]
    pagination.total = 3
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchCustomerList()
}

// 重置
const handleReset = () => {
  searchForm.name = ''
  searchForm.phone = ''
  handleSearch()
}

// 分页
const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchCustomerList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchCustomerList()
}

// 添加客户
const handleAdd = () => {
  dialogMode.value = 'add'
  dialogTitle.value = '添加客户'
  currentCustomer.value = {}
  dialogVisible.value = true
}

// 查看客户
const handleView = (row) => {
  dialogMode.value = 'view'
  dialogTitle.value = '客户详情'
  currentCustomer.value = { ...row }
  dialogVisible.value = true
}

// 编辑客户
const handleEdit = (row) => {
  dialogMode.value = 'edit'
  dialogTitle.value = '编辑客户'
  currentCustomer.value = { ...row }
  dialogVisible.value = true
}

// 保存
const handleSave = async () => {
  try {
    if (dialogMode.value === 'add') {
      await createCustomer(currentCustomer.value)
      ElMessage.success('添加成功')
    } else {
      await updateCustomer(currentCustomer.value.id, currentCustomer.value)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    fetchCustomerList()
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  }
}

onMounted(() => {
  fetchCustomerList()
})
</script>

<style scoped>
.customer-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
