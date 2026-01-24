<template>
  <div class="service-detail">
    <el-page-header @back="goBack" title="返回列表" :content="service.name || '服务详情'" />
    
    <el-row :gutter="20" class="detail-content">
      <el-col :span="16">
        <!-- 基本信息 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <div>
                <el-tag :type="getStatusType(service.status)" size="large">
                  {{ getStatusText(service.status) }}
                </el-tag>
              </div>
            </div>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="服务ID">{{ service.service_id }}</el-descriptions-item>
            <el-descriptions-item label="服务名称">{{ service.name }}</el-descriptions-item>
            <el-descriptions-item label="使用模型">{{ service.model_used }}</el-descriptions-item>
            <el-descriptions-item label="生成成本">${{ service.generation_cost?.toFixed(4) }}</el-descriptions-item>
            <el-descriptions-item label="质量评分">
              <el-progress :percentage="service.quality_score || 0" :stroke-width="10" />
            </el-descriptions-item>
            <el-descriptions-item label="生成耗时">{{ service.generation_time }}秒</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(service.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ formatDate(service.updated_at) }}</el-descriptions-item>
            <el-descriptions-item label="原始需求" :span="2">
              {{ service.original_requirement }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <!-- 代码展示 -->
        <el-card class="code-card">
          <template #header>
            <div class="card-header">
              <span>生成的代码</span>
              <el-button type="primary" size="small" @click="copyCode">
                <el-icon><CopyDocument /></el-icon>
                复制代码
              </el-button>
            </div>
          </template>
          <pre class="code-block"><code>{{ service.code || '暂无代码' }}</code></pre>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <!-- 操作面板 -->
        <el-card class="action-card">
          <template #header>操作</template>
          <div class="action-buttons">
            <el-button 
              v-if="service.status === 'ready'"
              type="success" 
              size="large"
              class="action-btn"
              @click="handleDeploy"
            >
              <el-icon><Upload /></el-icon>
              部署服务
            </el-button>
            <el-button 
              v-if="service.status === 'deployed'"
              type="warning" 
              size="large"
              class="action-btn"
              @click="handleStop"
            >
              <el-icon><VideoPause /></el-icon>
              停止服务
            </el-button>
            <el-button size="large" class="action-btn" @click="handleOptimize">
              <el-icon><MagicStick /></el-icon>
              优化代码
            </el-button>
            <el-button type="danger" size="large" class="action-btn" @click="handleDelete">
              <el-icon><Delete /></el-icon>
              删除服务
            </el-button>
          </div>
        </el-card>
        
        <!-- 运行统计 -->
        <el-card class="stats-card" v-if="service.is_deployed">
          <template #header>运行统计</template>
          <el-statistic title="总调用次数" :value="service.total_calls || 0" />
          <el-statistic title="错误次数" :value="service.total_errors || 0" class="mt-20" />
          <el-statistic title="平均延迟" :value="service.avg_latency || 0" suffix="ms" class="mt-20" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getServiceDetail, deployService, stopService, deleteService } from '@/api/service'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const service = ref({})
const loading = ref(false)

async function loadDetail() {
  loading.value = true
  try {
    const res = await getServiceDetail(route.params.id)
    service.value = res.data || {}
  } catch (error) {
    ElMessage.error('加载服务详情失败')
  } finally {
    loading.value = false
  }
}

function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
}

function getStatusType(status) {
  const types = { generating: 'warning', ready: 'success', deployed: 'primary', failed: 'danger' }
  return types[status] || 'info'
}

function getStatusText(status) {
  const texts = { generating: '生成中', ready: '已就绪', deployed: '运行中', failed: '失败' }
  return texts[status] || status
}

function goBack() {
  router.push('/service/list')
}

function copyCode() {
  if (service.value.code) {
    navigator.clipboard.writeText(service.value.code)
    ElMessage.success('代码已复制到剪贴板')
  }
}

async function handleDeploy() {
  try {
    await deployService(service.value.service_id)
    ElMessage.success('部署成功')
    loadDetail()
  } catch (error) {
    ElMessage.error('部署失败')
  }
}

async function handleStop() {
  try {
    await stopService(service.value.service_id)
    ElMessage.success('服务已停止')
    loadDetail()
  } catch (error) {
    ElMessage.error('停止失败')
  }
}

function handleOptimize() {
  ElMessage.info('优化功能开发中...')
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除这个服务吗？此操作不可恢复。', '警告', { type: 'warning' })
    await deleteService(service.value.service_id)
    ElMessage.success('删除成功')
    router.push('/service/list')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadDetail()
})
</script>

<style lang="scss" scoped>
.service-detail {
  .detail-content {
    margin-top: 20px;
  }
  
  .info-card, .code-card {
    margin-bottom: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .code-block {
    background: #1e1e1e;
    color: #d4d4d4;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    max-height: 500px;
    font-family: 'Fira Code', 'Monaco', monospace;
    font-size: 13px;
    line-height: 1.5;
  }
  
  .action-card, .stats-card {
    margin-bottom: 20px;
    
    .action-buttons {
      display: flex;
      flex-direction: column;
      gap: 12px;
      
      .action-btn {
        width: 100%;
      }
    }
  }
}
</style>
