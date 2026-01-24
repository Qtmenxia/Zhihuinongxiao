<template>
  <div class="dashboard">
    <!-- 欢迎卡片 -->
    <el-row :gutter="20" class="welcome-row">
      <el-col :span="24">
        <el-card class="welcome-card">
          <div class="welcome-content">
            <div class="welcome-text">
              <h2>欢迎回来，{{ userStore.userInfo.name || '农户' }}！</h2>
              <p>智农链销 - 让AI帮您轻松开店</p>
            </div>
            <el-button type="primary" size="large" @click="goGenerate">
              <el-icon><MagicStick /></el-icon>
              立即生成服务
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 数据统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.servicesCount }}</div>
            <div class="stat-label">我的服务</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
            <el-icon><ShoppingCart /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.ordersToday }}</div>
            <div class="stat-label">今日订单</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
            <el-icon><Money /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.salesToday }}</div>
            <div class="stat-label">今日销售</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
            <el-icon><Coin /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">${{ stats.costToday }}</div>
            <div class="stat-label">今日成本</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 主要内容区 -->
    <el-row :gutter="20">
      <!-- 快捷操作 -->
      <el-col :xs="24" :md="8">
        <el-card class="quick-actions">
          <template #header>
            <span>快捷操作</span>
          </template>
          <div class="action-grid">
            <div class="action-item" @click="goGenerate">
              <el-icon class="action-icon"><MagicStick /></el-icon>
              <span>生成服务</span>
            </div>
            <div class="action-item" @click="router.push('/product/add')">
              <el-icon class="action-icon"><Goods /></el-icon>
              <span>添加产品</span>
            </div>
            <div class="action-item" @click="router.push('/order/list')">
              <el-icon class="action-icon"><Document /></el-icon>
              <span>订单管理</span>
            </div>
            <div class="action-item" @click="router.push('/statistics/overview')">
              <el-icon class="action-icon"><DataAnalysis /></el-icon>
              <span>数据分析</span>
            </div>
          </div>
        </el-card>
        
        <!-- 配额信息 -->
        <el-card class="quota-card">
          <template #header>
            <div class="quota-header">
              <span>服务配额</span>
              <el-tag :type="quotaType">{{ userStore.userInfo.tier }}</el-tag>
            </div>
          </template>
          <div class="quota-item">
            <span>已用服务数</span>
            <el-progress 
              :percentage="quotaPercentage" 
              :stroke-width="10"
              :color="quotaColor"
            />
            <span class="quota-text">{{ stats.servicesCount }} / {{ quotaLimit }}</span>
          </div>
          <el-button type="primary" plain size="small" class="upgrade-btn">
            升级套餐
          </el-button>
        </el-card>
      </el-col>
      
      <!-- 销售趋势图表 -->
      <el-col :xs="24" :md="16">
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span>最近30天销售趋势</span>
              <el-radio-group v-model="chartType" size="small">
                <el-radio-button label="sales">销售额</el-radio-button>
                <el-radio-button label="orders">订单数</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <v-chart :option="chartOption" autoresize style="height: 300px" />
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近服务 -->
    <el-row :gutter="20" class="recent-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="section-header">
              <span>最近生成的服务</span>
              <el-button type="primary" link @click="router.push('/service/list')">
                查看全部 <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          <el-table :data="recentServices" stripe>
            <el-table-column prop="name" label="服务名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="generation_cost" label="生成成本" width="100">
              <template #default="{ row }">
                ${{ row.generation_cost?.toFixed(3) || '0.000' }}
              </template>
            </el-table-column>
            <el-table-column prop="quality_score" label="质量评分" width="100">
              <template #default="{ row }">
                <el-rate 
                  v-model="row.quality_score" 
                  disabled 
                  :max="5"
                  :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                />
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="viewService(row)">
                  查看
                </el-button>
                <el-button 
                  v-if="row.status === 'ready'" 
                  type="success" 
                  link 
                  size="small"
                  @click="deployService(row)"
                >
                  部署
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { getServiceList } from '@/api/service'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

const router = useRouter()
const userStore = useUserStore()

// 统计数据
const stats = reactive({
  servicesCount: 0,
  ordersToday: 0,
  salesToday: 0,
  costToday: 0
})

// 最近服务
const recentServices = ref([])

// 图表类型
const chartType = ref('sales')

// 配额计算
const quotaLimit = computed(() => {
  const limits = { free: 3, basic: 20, professional: 100 }
  return limits[userStore.userInfo.tier] || 3
})

const quotaPercentage = computed(() => {
  return Math.min((stats.servicesCount / quotaLimit.value) * 100, 100)
})

const quotaColor = computed(() => {
  if (quotaPercentage.value >= 90) return '#F56C6C'
  if (quotaPercentage.value >= 70) return '#E6A23C'
  return '#67C23A'
})

const quotaType = computed(() => {
  const types = { free: 'info', basic: 'warning', professional: 'success' }
  return types[userStore.userInfo.tier] || 'info'
})

// 图表配置
const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: generateLast30Days()
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: chartType.value === 'sales' ? '销售额' : '订单数',
      type: 'line',
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      data: generateMockData()
    }
  ]
}))

// 生成最近30天日期
function generateLast30Days() {
  const days = []
  for (let i = 29; i >= 0; i--) {
    days.push(dayjs().subtract(i, 'day').format('MM-DD'))
  }
  return days
}

// 生成模拟数据
function generateMockData() {
  return Array.from({ length: 30 }, () => Math.floor(Math.random() * 1000) + 100)
}

// 格式化日期
function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取状态类型
function getStatusType(status) {
  const types = {
    generating: 'warning',
    ready: 'success',
    deployed: 'primary',
    failed: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
function getStatusText(status) {
  const texts = {
    generating: '生成中',
    ready: '已就绪',
    deployed: '运行中',
    failed: '失败'
  }
  return texts[status] || status
}

// 跳转生成页面
function goGenerate() {
  router.push('/service/generate')
}

// 查看服务
function viewService(row) {
  router.push(`/service/detail/${row.service_id}`)
}

// 部署服务
function deployService(row) {
  // TODO: 实现部署逻辑
}

// 加载数据
onMounted(async () => {
  try {
    // 获取统计数据
    stats.servicesCount = userStore.userInfo.servicesCount || 0
    
    // 获取最近服务
    const res = await getServiceList({ page: 1, page_size: 5 })
    recentServices.value = res.data?.items || []
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  .welcome-row {
    margin-bottom: 20px;
  }
  
  .welcome-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    
    .welcome-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .welcome-text {
        color: #fff;
        
        h2 {
          margin: 0 0 8px;
          font-size: 24px;
        }
        
        p {
          margin: 0;
          opacity: 0.8;
        }
      }
    }
  }
  
  .stats-row {
    margin-bottom: 20px;
    
    .stat-card {
      display: flex;
      align-items: center;
      padding: 20px;
      
      .stat-icon {
        width: 64px;
        height: 64px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        
        .el-icon {
          font-size: 28px;
          color: #fff;
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
  
  .quick-actions {
    margin-bottom: 20px;
    
    .action-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      
      .action-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        background: #f5f7fa;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s;
        
        &:hover {
          background: #ecf5ff;
          transform: translateY(-2px);
        }
        
        .action-icon {
          font-size: 32px;
          color: #409EFF;
          margin-bottom: 8px;
        }
        
        span {
          font-size: 14px;
          color: #606266;
        }
      }
    }
  }
  
  .quota-card {
    .quota-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .quota-item {
      margin-bottom: 16px;
      
      .quota-text {
        float: right;
        font-size: 12px;
        color: #909399;
      }
    }
    
    .upgrade-btn {
      width: 100%;
    }
  }
  
  .chart-card {
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .recent-row {
    margin-top: 20px;
  }
}
</style>
