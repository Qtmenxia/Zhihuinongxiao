<template>
  <div class="service-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>我的服务</span>
          <el-button type="primary" @click="goGenerate">
            <el-icon><Plus /></el-icon>
            生成新服务
          </el-button>
        </div>
      </template>
      
      <!-- 筛选 -->
      <div class="filter-bar">
        <el-select v-model="filters.status" placeholder="服务状态" clearable @change="loadData">
          <el-option label="生成中" value="generating" />
          <el-option label="已就绪" value="ready" />
          <el-option label="运行中" value="deployed" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-input
          v-model="filters.keyword"
          placeholder="搜索服务名称"
          clearable
          style="width: 200px"
          @clear="loadData"
          @keyup.enter="loadData"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <!-- 服务列表 -->
      <el-table :data="services" v-loading="loading" stripe>
        <el-table-column prop="name" label="服务名称" min-width="200">
          <template #default="{ row }">
            <div class="service-name">
              <el-icon><Connection /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="model_used" label="模型" width="140" />
        
        <el-table-column prop="generation_cost" label="成本" width="100">
          <template #default="{ row }">
            ${{ row.generation_cost?.toFixed(3) || '-' }}
          </template>
        </el-table-column>
        
        <el-table-column prop="quality_score" label="质量" width="120">
          <template #default="{ row }">
            <el-progress
              v-if="row.quality_score"
              :percentage="row.quality_score"
              :color="getQualityColor(row.quality_score)"
              :stroke-width="8"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="total_calls" label="调用次数" width="100" />
        
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              详情
            </el-button>
            <el-button
              v-if="row.status === 'ready'"
              type="success"
              link
              size="small"
              @click="handleDeploy(row)"
            >
              部署
            </el-button>
            <el-button
              v-if="row.status === 'deployed'"
              type="warning"
              link
              size="small"
              @click="handleStop(row)"
            >
              停止
            </el-button>
            <el-popconfirm
              title="确定删除这个服务吗？"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button type="danger" link size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getServiceList, deployService, stopService, deleteService } from '@/api/service'
import dayjs from 'dayjs'

const router = useRouter()

const loading = ref(false)
const services = ref([])

const filters = reactive({
  status: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 加载数据
async function loadData() {
  loading.value = true
  try {
    const res = await getServiceList({
      page: pagination.page,
      page_size: pagination.pageSize,
      status: filters.status || undefined,
      keyword: filters.keyword || undefined
    })
    services.value = res.data?.items || []
    pagination.total = res.data?.total || 0
  } catch (error) {
    ElMessage.error('加载服务列表失败')
  } finally {
    loading.value = false
  }
}

// 格式化日期
function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 状态类型
function getStatusType(status) {
  const types = {
    generating: 'warning',
    ready: 'success',
    deployed: 'primary',
    failed: 'danger',
    archived: 'info'
  }
  return types[status] || 'info'
}

// 状态文本
function getStatusText(status) {
  const texts = {
    generating: '生成中',
    ready: '已就绪',
    deployed: '运行中',
    failed: '失败',
    archived: '已归档'
  }
  return texts[status] || status
}

// 质量颜色
function getQualityColor(score) {
  if (score >= 80) return '#67C23A'
  if (score >= 60) return '#E6A23C'
  return '#F56C6C'
}

// 操作
function goGenerate() {
  router.push('/service/generate')
}

function viewDetail(row) {
  router.push(`/service/detail/${row.service_id}`)
}

async function handleDeploy(row) {
  try {
    await deployService(row.service_id)
    ElMessage.success('部署成功')
    loadData()
  } catch (error) {
    ElMessage.error('部署失败: ' + error.message)
  }
}

async function handleStop(row) {
  try {
    await stopService(row.service_id)
    ElMessage.success('服务已停止')
    loadData()
  } catch (error) {
    ElMessage.error('停止失败: ' + error.message)
  }
}

async function handleDelete(row) {
  try {
    await deleteService(row.service_id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    ElMessage.error('删除失败: ' + error.message)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style lang="scss" scoped>
.service-list {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .filter-bar {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
  }
  
  .service-name {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .el-icon {
      color: #409EFF;
    }
  }
  
  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
