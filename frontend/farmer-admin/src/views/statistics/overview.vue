<template>
  <div class="statistics-overview">
    <!-- 核心指标卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card revenue">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">总销售额</div>
              <div class="stat-value">¥{{ formatNumber(overview.totalRevenue) }}</div>
              <div class="stat-trend" :class="{ up: overview.revenueTrend > 0 }">
                <el-icon><CaretTop v-if="overview.revenueTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(overview.revenueTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card orders">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">订单总数</div>
              <div class="stat-value">{{ overview.totalOrders }}</div>
              <div class="stat-trend" :class="{ up: overview.ordersTrend > 0 }">
                <el-icon><CaretTop v-if="overview.ordersTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(overview.ordersTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card customers">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">客户总数</div>
              <div class="stat-value">{{ overview.totalCustomers }}</div>
              <div class="stat-trend" :class="{ up: overview.customersTrend > 0 }">
                <el-icon><CaretTop v-if="overview.customersTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(overview.customersTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card products">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon><Goods /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">在售产品</div>
              <div class="stat-value">{{ overview.totalProducts }}</div>
              <div class="stat-trend" :class="{ up: overview.productsTrend > 0 }">
                <el-icon><CaretTop v-if="overview.productsTrend > 0" /><CaretBottom v-else /></el-icon>
                {{ Math.abs(overview.productsTrend) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <!-- 销售趋势 -->
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>销售趋势</span>
              <el-radio-group v-model="salesPeriod" size="small" @change="loadSalesTrend">
                <el-radio-button label="week">近7天</el-radio-button>
                <el-radio-button label="month">近30天</el-radio-button>
                <el-radio-button label="year">近12月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="salesChartRef" class="chart" style="height: 350px"></div>
        </el-card>
      </el-col>

      <!-- 订单状态分布 -->
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>订单状态分布</template>
          <div ref="orderStatusChartRef" class="chart" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 产品销售排行 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>产品销售排行 TOP10</template>
          <div ref="productRankChartRef" class="chart" style="height: 400px"></div>
        </el-card>
      </el-col>

      <!-- 客户地区分布 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>客户地区分布</template>
          <div ref="regionChartRef" class="chart" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 实时数据 -->
    <el-row :gutter="20">
      <el-col :xs="24">
        <el-card class="realtime-card">
          <template #header>
            <div class="card-header">
              <span>实时数据</span>
              <el-tag type="success">
                <el-icon><Clock /></el-icon>
                实时更新
              </el-tag>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :xs="12" :sm="6" :md="3">
              <div class="realtime-item">
                <div class="item-label">今日订单</div>
                <div class="item-value">{{ realtime.todayOrders }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="3">
              <div class="realtime-item">
                <div class="item-label">今日销售额</div>
                <div class="item-value">¥{{ formatNumber(realtime.todayRevenue) }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="3">
              <div class="realtime-item">
                <div class="item-label">待发货</div>
                <div class="item-value">{{ realtime.pendingShipment }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="3">
              <div class="realtime-item">
                <div class="item-label">待付款</div>
                <div class="item-value">{{ realtime.pendingPayment }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="3">
              <div class="realtime-item">
                <div class="item-label">库存预警</div>
                <div class="item-value warning">{{ realtime.lowStock }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="3">
              <div class="realtime-item">
                <div class="item-label">新增客户</div>
                <div class="item-value">{{ realtime.newCustomers }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="3">
              <div class="realtime-item">
                <div class="item-label">客单价</div>
                <div class="item-value">¥{{ realtime.avgOrderValue }}</div>
              </div>
            </el-col>
            <el-col :xs="12" :sm="6" :md="3">
              <div class="realtime-item">
                <div class="item-label">转化率</div>
                <div class="item-value">{{ realtime.conversionRate }}%</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const salesChartRef = ref(null)
const orderStatusChartRef = ref(null)
const productRankChartRef = ref(null)
const regionChartRef = ref(null)

const salesPeriod = ref('month')

let salesChart = null
let orderStatusChart = null
let productRankChart = null
let regionChart = null
let realtimeTimer = null

const overview = reactive({
  totalRevenue: 125680,
  revenueTrend: 12.5,
  totalOrders: 856,
  ordersTrend: 8.3,
  totalCustomers: 342,
  customersTrend: 15.2,
  totalProducts: 28,
  productsTrend: 3.7
})

const realtime = reactive({
  todayOrders: 23,
  todayRevenue: 4580,
  pendingShipment: 12,
  pendingPayment: 8,
  lowStock: 5,
  newCustomers: 7,
  avgOrderValue: 199,
  conversionRate: 3.2
})

function formatNumber(num) {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function loadSalesTrend() {
  if (!salesChart) return

  const periods = {
    week: {
      xData: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      salesData: [3200, 4100, 3800, 5200, 4800, 6100, 5500],
      ordersData: [18, 24, 21, 29, 27, 35, 31]
    },
    month: {
      xData: Array.from({ length: 30 }, (_, i) => `${i + 1}日`),
      salesData: Array.from({ length: 30 }, () => Math.floor(Math.random() * 3000) + 2000),
      ordersData: Array.from({ length: 30 }, () => Math.floor(Math.random() * 20) + 10)
    },
    year: {
      xData: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
      salesData: [45000, 52000, 61000, 58000, 63000, 71000, 68000, 75000, 82000, 88000, 95000, 102000],
      ordersData: [250, 290, 340, 320, 350, 395, 380, 420, 460, 490, 530, 570]
    }
  }

  const data = periods[salesPeriod.value]

  salesChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['销售额', '订单数']
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
      data: data.xData
    },
    yAxis: [
      {
        type: 'value',
        name: '销售额(元)',
        position: 'left'
      },
      {
        type: 'value',
        name: '订单数',
        position: 'right'
      }
    ],
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: true,
        data: data.salesData,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        itemStyle: { color: '#409eff' }
      },
      {
        name: '订单数',
        type: 'line',
        smooth: true,
        yAxisIndex: 1,
        data: data.ordersData,
        itemStyle: { color: '#67c23a' }
      }
    ]
  })
}

function initCharts() {
  // 销售趋势图
  salesChart = echarts.init(salesChartRef.value)
  loadSalesTrend()

  // 订单状态分布
  orderStatusChart = echarts.init(orderStatusChartRef.value)
  orderStatusChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: 156, name: '已完成', itemStyle: { color: '#67c23a' } },
          { value: 89, name: '已发货', itemStyle: { color: '#409eff' } },
          { value: 45, name: '待发货', itemStyle: { color: '#e6a23c' } },
          { value: 23, name: '待付款', itemStyle: { color: '#f56c6c' } },
          { value: 12, name: '已取消', itemStyle: { color: '#909399' } }
        ]
      }
    ]
  })

  // 产品销售排行
  productRankChart = echarts.init(productRankChartRef.value)
  productRankChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: ['烟富苹果', '蒲香红苹果', '维纳斯苹果-大', '维纳斯苹果-小', '玉露香梨-手提', '玉露香梨-12枚', '玉露香梨-9枚']
    },
    series: [
      {
        type: 'bar',
        data: [120, 145, 168, 189, 210, 245, 280],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#67c23a' }
          ])
        },
        barWidth: '60%'
      }
    ]
  })

  // 客户地区分布
  regionChart = echarts.init(regionChartRef.value)
  regionChart.setOption({
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '70%',
        data: [
          { value: 156, name: '北京' },
          { value: 89, name: '上海' },
          { value: 78, name: '广东' },
          { value: 65, name: '浙江' },
          { value: 54, name: '江苏' },
          { value: 43, name: '山西' },
          { value: 32, name: '其他' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  })

  // 响应式
  window.addEventListener('resize', () => {
    salesChart?.resize()
    orderStatusChart?.resize()
    productRankChart?.resize()
    regionChart?.resize()
  })
}

function updateRealtime() {
  // 模拟实时数据更新
  realtime.todayOrders += Math.floor(Math.random() * 2)
  realtime.todayRevenue += Math.floor(Math.random() * 500)
}

onMounted(() => {
  initCharts()
  // 每30秒更新一次实时数据
  realtimeTimer = setInterval(updateRealtime, 30000)
})

onUnmounted(() => {
  salesChart?.dispose()
  orderStatusChart?.dispose()
  productRankChart?.dispose()
  regionChart?.dispose()
  if (realtimeTimer) {
    clearInterval(realtimeTimer)
  }
})
</script>

<style lang="scss" scoped>
.statistics-overview {
  padding: 20px;

  .stats-cards {
    margin-bottom: 20px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 20px;

        .stat-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          color: white;
        }

        .stat-info {
          flex: 1;

          .stat-label {
            font-size: 14px;
            color: #909399;
            margin-bottom: 8px;
          }

          .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #303133;
            margin-bottom: 4px;
          }

          .stat-trend {
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 4px;

            &.up {
              color: #67c23a;
            }

            &:not(.up) {
              color: #f56c6c;
            }
          }
        }
      }

      &.revenue .stat-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.orders .stat-icon {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }

      &.customers .stat-icon {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }

      &.products .stat-icon {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }
  }

  .chart-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .realtime-card {
    .realtime-item {
      text-align: center;
      padding: 15px 0;

      .item-label {
        font-size: 13px;
        color: #909399;
        margin-bottom: 8px;
      }

      .item-value {
        font-size: 20px;
        font-weight: 600;
        color: #303133;

        &.warning {
          color: #f56c6c;
        }
      }
    }
  }
}
</style>
