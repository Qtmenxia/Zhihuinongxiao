<template>
  <div class="traceability-records">
    <!-- 搜索栏 -->
    <el-form :inline="true" :model="searchForm" class="search-form">
      <el-form-item label="产品名称">
        <el-input v-model="searchForm.productName" placeholder="请输入产品名称" clearable />
      </el-form-item>
      <el-form-item label="批次号">
        <el-input v-model="searchForm.batchNo" placeholder="请输入批次号" clearable />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>搜索
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>重置
        </el-button>
        <el-button type="success" @click="handleAdd">
          <el-icon><Plus /></el-icon>新建溯源记录
        </el-button>
      </el-form-item>
    </el-form>

    <!-- 数据表格 -->
    <el-table :data="recordList" v-loading="loading" stripe>
      <el-table-column prop="batchNo" label="批次号" width="150" />
      <el-table-column prop="productName" label="产品名称" min-width="150" />
      <el-table-column prop="origin" label="产地" width="180" />
      <el-table-column prop="harvestDate" label="采收日期" width="120">
        <template #default="{ row }">
          {{ formatDate(row.harvestDate) }}
        </template>
      </el-table-column>
      <el-table-column prop="quantity" label="数量" width="120" align="center">
        <template #default="{ row }">
          {{ row.quantity }} {{ row.unit }}
        </template>
      </el-table-column>
      <el-table-column label="溯源码" width="100" align="center">
        <template #default="{ row }">
          <el-button type="primary" link @click="showQrCode(row)">
            <el-icon><View /></el-icon>查看
          </el-button>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleView(row)">详情</el-button>
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchRecords"
        @current-change="fetchRecords"
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="溯源详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="批次号">{{ currentRecord.batchNo }}</el-descriptions-item>
        <el-descriptions-item label="产品名称">{{ currentRecord.productName }}</el-descriptions-item>
        <el-descriptions-item label="产地">{{ currentRecord.origin }}</el-descriptions-item>
        <el-descriptions-item label="采收日期">{{ formatDate(currentRecord.harvestDate) }}</el-descriptions-item>
        <el-descriptions-item label="数量">{{ currentRecord.quantity }} {{ currentRecord.unit }}</el-descriptions-item>
        <el-descriptions-item label="认证信息">{{ currentRecord.certification || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">生产记录</el-divider>
      <el-timeline>
        <el-timeline-item
          v-for="record in currentRecord.records"
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
    <el-dialog v-model="qrVisible" title="溯源二维码" width="400px" align-center>
      <div class="qr-wrapper">
        <div class="qr-placeholder">
          <el-icon :size="200" color="#409eff"><Connection /></el-icon>
          <p>批次号：{{ currentRecord.batchNo }}</p>
          <p class="tip">扫描二维码查看完整溯源信息</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="qrVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadQrCode">下载二维码</el-button>
      </template>
    </el-dialog>

    <!-- 新建/编辑弹窗 -->
    <el-dialog 
      v-model="formVisible" 
      :title="formMode === 'add' ? '新建溯源记录' : '编辑溯源记录'" 
      width="600px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="批次号" prop="batchNo">
          <el-input v-model="formData.batchNo" placeholder="请输入批次号" />
        </el-form-item>
        <el-form-item label="产品名称" prop="productName">
          <el-input v-model="formData.productName" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="产地" prop="origin">
          <el-input v-model="formData.origin" placeholder="请输入产地" />
        </el-form-item>
        <el-form-item label="采收日期" prop="harvestDate">
          <el-date-picker
            v-model="formData.harvestDate"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="数量" prop="quantity">
          <el-input-number v-model="formData.quantity" :min="0" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-select v-model="formData.unit" placeholder="请选择单位">
            <el-option label="斤" value="斤" />
            <el-option label="公斤" value="公斤" />
            <el-option label="箱" value="箱" />
            <el-option label="枚" value="枚" />
          </el-select>
        </el-form-item>
        <el-form-item label="认证信息" prop="certification">
          <el-input v-model="formData.certification" placeholder="如：有机认证" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)
const submitLoading = ref(false)
const recordList = ref([])
const detailVisible = ref(false)
const qrVisible = ref(false)
const formVisible = ref(false)
const formMode = ref('add')
const formRef = ref(null)
const currentRecord = ref({})

const searchForm = reactive({
  productName: '',
  batchNo: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  batchNo: '',
  productName: '',
  origin: '山西省临汾市蒲县被子垣',
  harvestDate: null,
  quantity: 0,
  unit: '斤',
  certification: '有机认证'
})

const formRules = {
  batchNo: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
  productName: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  origin: [{ required: true, message: '请输入产地', trigger: 'blur' }],
  harvestDate: [{ required: true, message: '请选择采收日期', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  unit: [{ required: true, message: '请选择单位', trigger: 'change' }]
}

// 获取记录列表
async function fetchRecords() {
  loading.value = true
  try {
    // 模拟数据
    recordList.value = [
      {
        id: 1,
        batchNo: 'BZ2024020001',
        productName: '有机玉露香梨',
        origin: '山西省临汾市蒲县被子垣村',
        harvestDate: '2024-10-15',
        quantity: 500,
        unit: '斤',
        certification: '有机认证',
        records: [
          { id: 1, title: '采收完成', description: '完成采收500斤', time: '2024-10-15T17:00:00Z', operator: '张三', type: 'important' },
          { id: 2, title: '入库完成', description: '产品已入库，库位A-03', time: '2024-10-16T16:00:00Z', operator: '仓管员' },
          { id: 3, title: '质检通过', description: '产品通过质量检测，符合有机标准', time: '2024-10-18T10:00:00Z', operator: '质检员李四' }
        ]
      },
      {
        id: 2,
        batchNo: 'BZ2024020002',
        productName: '维纳斯黄金苹果',
        origin: '山西省临汾市蒲县',
        harvestDate: '2024-10-20',
        quantity: 1000,
        unit: '斤',
        certification: '有机认证',
        records: []
      }
    ]
    pagination.total = 2
  } catch (error) {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchRecords()
}

function handleReset() {
  searchForm.productName = ''
  searchForm.batchNo = ''
  handleSearch()
}

function handleAdd() {
  formMode.value = 'add'
  Object.assign(formData, {
    batchNo: '',
    productName: '',
    origin: '山西省临汾市蒲县被子垣',
    harvestDate: null,
    quantity: 0,
    unit: '斤',
    certification: '有机认证'
  })
  formVisible.value = true
}

function handleEdit(row) {
  formMode.value = 'edit'
  Object.assign(formData, row)
  formVisible.value = true
}

function handleView(row) {
  currentRecord.value = row
  detailVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除批次号"${row.batchNo}"的溯源记录吗？`, '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('删除成功')
    fetchRecords()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function showQrCode(row) {
  currentRecord.value = row
  qrVisible.value = true
}

function downloadQrCode() {
  ElMessage.success('二维码下载功能开发中...')
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitLoading.value = true
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      ElMessage.success(formMode.value === 'add' ? '创建成功' : '更新成功')
      formVisible.value = false
      fetchRecords()
    } catch (error) {
      ElMessage.error('操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD') : '-'
}

function formatDateTime(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

onMounted(() => {
  fetchRecords()
})
</script>

<style lang="scss" scoped>
.traceability-records {
  .search-form {
    margin-bottom: 20px;
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }

  .qr-wrapper {
    display: flex;
    justify-content: center;
    padding: 20px;

    .qr-placeholder {
      text-align: center;

      p {
        margin-top: 15px;
        font-size: 14px;
        color: #606266;

        &.tip {
          color: #909399;
          font-size: 12px;
        }
      }
    }
  }

  .operator {
    color: #909399;
    font-size: 12px;
    margin-top: 4px;
  }
}
</style>

