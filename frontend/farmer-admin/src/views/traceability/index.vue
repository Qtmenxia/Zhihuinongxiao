<template>
  <div class="traceability-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>溯源管理</span>
          <el-button type="primary" :icon="Plus" @click="handleAdd">添加溯源记录</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="产品名称">
          <el-input v-model="searchForm.productName" placeholder="请输入产品名称" clearable />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="searchForm.batchNo" placeholder="请输入批次号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
            <el-option label="生产中" value="producing" />
            <el-option label="已入库" value="stored" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="traceList" v-loading="loading" stripe>
        <el-table-column prop="batchNo" label="批次号" width="150" />
        <el-table-column prop="productName" label="产品名称" min-width="150" />
        <el-table-column prop="origin" label="产地" min-width="150" />
        <el-table-column prop="harvestDate" label="采收日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.harvestDate) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="100" align="center">
          <template #default="{ row }">
            {{ row.quantity }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="qrCode" label="溯源码" width="120" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="showQrCode(row)">
              <el-icon><View /></el-icon> 查看
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">详情</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="handleAddRecord(row)">添加记录</el-button>
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

    <!-- 溯源详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="溯源详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="批次号">{{ currentTrace.batchNo }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ currentTrace.productName }}</el-descriptions-item>
        <el-descriptions-item label="产地">{{ currentTrace.origin }}</el-descriptions-item>
        <el-descriptions-item label="采收日期">{{ formatDate(currentTrace.harvestDate) }}</el-descriptions-item>
        <el-descriptions-item label="数量">{{ currentTrace.quantity }} {{ currentTrace.unit }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentTrace.status)">{{ getStatusText(currentTrace.status) }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">溯源记录</el-divider>
      
      <el-timeline>
        <el-timeline-item
          v-for="record in currentTrace.records"
          :key="record.id"
          :timestamp="formatDateTime(record.time)"
          :type="record.type === 'important' ? 'primary' : 'info'"
        >
          <h4>{{ record.title }}</h4>
          <p>{{ record.description }}</p>
          <p v-if="record.operator" class="operator">操作人：{{ record.operator }}</p>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>

    <!-- 二维码弹窗 -->
    <el-dialog v-model="qrDialogVisible" title="溯源二维码" width="400px" align-center>
      <div class="qr-wrapper">
        <div class="qr-placeholder">
          <el-icon :size="120"><Connection /></el-icon>
          <p>批次号：{{ currentTrace.batchNo }}</p>
          <p class="tip">扫描二维码查看完整溯源信息</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="qrDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadQrCode">下载二维码</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, Refresh, View, Connection } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getTraceList } from '@/api/traceability'

// 搜索表单
const searchForm = reactive({
  productName: '',
  batchNo: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 数据
const loading = ref(false)
const traceList = ref([])
const detailDialogVisible = ref(false)
const qrDialogVisible = ref(false)
const currentTrace = ref({})

// 状态映射
const getStatusType = (status) => {
  const map = {
    producing: 'warning',
    stored: 'info',
    shipped: 'primary',
    completed: 'success'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    producing: '生产中',
    stored: '已入库',
    shipped: '已发货',
    completed: '已完成'
  }
  return map[status] || status
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 获取溯源列表
const fetchTraceList = async () => {
  loading.value = true
  try {
    const res = await getTraceList({
      ...searchForm,
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    traceList.value = res.data?.items || []
    pagination.total = res.data?.total || 0
  } catch (error) {
    console.error('获取溯源列表失败:', error)
    // 使用模拟数据
    traceList.value = [
      { 
        id: 1, 
        batchNo: 'BZ2024010001', 
        productName: '有机红富士苹果', 
        origin: '山西省临汾市蒲县被子垣村', 
        harvestDate: '2024-10-15',
        quantity: 500,
        unit: '斤',
        status: 'completed',
        records: [
          { id: 1, title: '完成发货', description: '订单已全部发出', time: '2024-10-20T14:30:00Z', operator: '张三', type: 'important' },
          { id: 2, title: '质检通过', description: '产品通过质量检测，符合有机标准', time: '2024-10-18T10:00:00Z', operator: '质检员李四' },
          { id: 3, title: '入库完成', description: '产品已入库，库位A-03', time: '2024-10-16T16:00:00Z', operator: '仓管员' },
          { id: 4, title: '采收完成', description: '完成采收500斤', time: '2024-10-15T17:00:00Z', operator: '张三', type: 'important' },
        ]
      },
      { 
        id: 2, 
        batchNo: 'BZ2024010002', 
        productName: '农家土鸡蛋', 
        origin: '山西省临汾市蒲县', 
        harvestDate: '2024-10-20',
        quantity: 1000,
        unit: '枚',
        status: 'shipped',
        records: []
      },
      { 
        id: 3, 
        batchNo: 'BZ2024010003', 
        productName: '有机小米', 
        origin: '山西省临汾市', 
        harvestDate: '2024-09-30',
        quantity: 200,
        unit: '斤',
        status: 'stored',
        records: []
      },
    ]
    pagination.total = 3
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchTraceList()
}

// 重置
const handleReset = () => {
  searchForm.productName = ''
  searchForm.batchNo = ''
  searchForm.status = ''
  handleSearch()
}

// 分页
const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchTraceList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchTraceList()
}

// 添加溯源
const handleAdd = () => {
  ElMessage.info('添加溯源记录功能开发中...')
}

// 查看详情
const handleView = (row) => {
  currentTrace.value = row
  detailDialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  ElMessage.info('编辑功能开发中...')
}

// 添加记录
const handleAddRecord = (row) => {
  ElMessage.info('添加记录功能开发中...')
}

// 显示二维码
const showQrCode = (row) => {
  currentTrace.value = row
  qrDialogVisible.value = true
}

// 下载二维码
const downloadQrCode = () => {
  ElMessage.success('二维码下载功能开发中...')
}

onMounted(() => {
  fetchTraceList()
})
</script>

<style scoped>
.traceability-container {
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

.qr-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.qr-placeholder {
  text-align: center;
  color: #409eff;
}

.qr-placeholder p {
  margin-top: 16px;
  font-size: 14px;
  color: #606266;
}

.qr-placeholder .tip {
  color: #909399;
  font-size: 12px;
}

.operator {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}
</style>
