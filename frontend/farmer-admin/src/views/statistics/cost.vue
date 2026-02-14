<template>
  <div class="cost-analysis" v-loading="pageLoading" element-loading-text="加载中..."
    <!-- 成本概览卡片 -->
    <el-row :gutter="20" class="cost-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="cost-card total">
          <div class="cost-content">
            <div class="cost-icon">
              <el-icon><Wallet /></el-icon>
            </div>
            <div class="cost-info">
              <div class="cost-label">总成本</div>
              <div class="cost-value">¥{{ formatNumber(costOverview.totalCost) }}</div>
              <div class="cost-compare">
                环比上月 {{ costOverview.totalTrend > 0 ? '+' : '' }}{{ costOverview.totalTrend }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="cost-card material">
          <div class="cost-content">
            <div class="cost-icon">
              <el-icon><Box /></el-icon>
            </div>
            <div class="cost-info">
              <div class="cost-label">原料成本</div>
              <div class="cost-value">¥{{ formatNumber(costOverview.materialCost) }}</div>
              <div class="cost-percent">占比 {{ costOverview.materialPercent }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="cost-card labor">
          <div class="cost-content">
            <div class="cost-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="cost-info">
              <div class="cost-label">人工成本</div>
              <div class="cost-value">¥{{ formatNumber(costOverview.laborCost) }}</div>
              <div class="cost-percent">占比 {{ costOverview.laborPercent }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="cost-card other">
          <div class="cost-content">
            <div class="cost-icon">
              <el-icon><More /></el-icon>
            </div>
            <div class="cost-info">
              <div class="cost-label">其他成本</div>
              <div class="cost-value">¥{{ formatNumber(costOverview.otherCost) }}</div>
              <div class="cost-percent">占比 {{ costOverview.otherPercent }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 成本分析图表 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>成本趋势分析</span>
              <el-radio-group v-model="costPeriod" size="small" @change="loadCostTrend">
                <el-radio-button label="month">本月</el-radio-button>
                <el-radio-button label="quarter">本季度</el-radio-button>
                <el-radio-button label="year">本年度</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="costTrendChartRef" class="chart" style="height: 400px"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>成本结构分布</template>
          <div ref="costStructureChartRef" class="chart" style="height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 成本明细表 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>成本明细</span>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              size="small"
              @change="loadCostDetails"
            />
            <el-select v-model="costType" placeholder="成本类型" size="small" style="width: 120px; margin-left: 10px" @change="loadCostDetails">
              <el-option label="全部" value="" />
              <el-option label="原料成本" value="material" />
              <el-option label="人工成本" value="labor" />
              <el-option label="物流成本" value="logistics" />
              <el-option label="包装成本" value="packaging" />
              <el-option label="其他成本" value="other" />
            </el-select>
            <el-button type="primary" size="small" @click="handleAddCost" style="margin-left: 10px">
              <el-icon><Plus /></el-icon>
              添加成本
            </el-button>
            <el-button type="success" size="small" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="costList" border stripe>
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="type" label="成本类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getCostTypeTag(row.type)">{{ getCostTypeName(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="成本项目" min-width="150" />
        <el-table-column prop="amount" label="金额" width="120" align="right">
          <template #default="{ row }">
            <span class="amount-text">¥{{ formatNumber(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量/工时" width="120" align="right" />
        <el-table-column prop="unitPrice" label="单价" width="100" align="right">
          <template #default="{ row }">
            ¥{{ row.unitPrice }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadCostDetails"
        @current-change="loadCostDetails"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 成本对比分析 -->
    <el-card class="chart-card">
      <template #header>成本对比分析</template>
      <div ref="costCompareChartRef" class="chart" style="height: 350px"></div>
    </el-card>

    <!-- 添加/编辑成本对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="costForm" :rules="costRules" ref="costFormRef" label-width="100px">
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="costForm.date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="成本类型" prop="type">
          <el-select v-model="costForm.type" placeholder="请选择成本类型" style="width: 100%">
            <el-option label="原料成本" value="material" />
            <el-option label="人工成本" value="labor" />
            <el-option label="物流成本" value="logistics" />
            <el-option label="包装成本" value="packaging" />
            <el-option label="其他成本" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="成本项目" prop="category">
          <el-input v-model="costForm.category" placeholder="请输入成本项目" />
        </el-form-item>
        <el-form-item label="数量/工时" prop="quantity">
          <el-input-number v-model="costForm.quantity" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单价" prop="unitPrice">
          <el-input-number v-model="costForm.unitPrice" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="总金额" prop="amount">
          <el-input-number v-model="costForm.amount" :min="0" :precision="2" style="width: 100%" disabled />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="costForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { getCostOverview, getCostTrend, getCostRecords, createCostRecord, updateCostRecord, deleteCostRecord } from '@/api/cost'

const costTrendChartRef = ref(null)
const costStructureChartRef = ref(null)
const costCompareChartRef = ref(null)
const costFormRef = ref(null)

const costPeriod = ref('month')
const dateRange = ref([])
const costType = ref('')
const dialogVisible = ref(false)
const dialogTitle = ref('添加成本')
const loading = ref(false)
const pageLoading = ref(true)

let costTrendChart = null
let costStructureChart = null
let costCompareChart = null

const costOverview = reactive({
  totalCost: 0,
  totalTrend: 0,
  materialCost: 0,
  materialPercent: 0,
  laborCost: 0,
  laborPercent: 0,
  otherCost: 0,
  otherPercent: 0
})

const costList = ref([])

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const costForm = reactive({
  date: '',
  type: '',
  category: '',
  quantity: 0,
  unitPrice: 0,
  amount: 0,
  remark: ''
})

const costRules = {
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  type: [{ required: true, message: '请选择成本类型', trigger: 'change' }],
  category: [{ required: true, message: '请输入成本项目', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量/工时', trigger: 'blur' }],
  unitPrice: [{ required: true, message: '请输入单价', trigger: 'blur' }]
}

// 监听数量和单价变化，自动计算总金额
watch([() => costForm.quantity, () => costForm.unitPrice], () => {
  costForm.amount = costForm.quantity * costForm.unitPrice
})

function formatNumber(num) {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getCostTypeName(type) {
  const names = {
    material: '原料成本',
    labor: '人工成本',
    logistics: '物流成本',
    packaging: '包装成本',
    other: '其他成本'
  }
  return names[type] || type
}

function getCostTypeTag(type) {
  const tags = {
    material: 'primary',
    labor: 'success',
    logistics: 'warning',
    packaging: 'info',
    other: 'danger'
  }
  return tags[type] || ''
}

function loadCostTrend() {
  if (!costTrendChart) return

  console.log('开始加载成本趋势...')
  getCostTrend(costPeriod.value).then(res => {
    console.log('成本趋势数据:', res)
    const trendData = res.data || []
    
    // 如果没有数据，显示空图表
    if (trendData.length === 0) {
      costTrendChart.setOption({
        title: {
          text: '暂无数据',
          left: 'center',
          top: 'center',
          textStyle: {
            color: '#999',
            fontSize: 14
          }
        }
      })
      return
    }
    
    const xData = trendData.map(item => item.date)
    const materialData = trendData.map(item => item.material)
    const laborData = trendData.map(item => item.labor)
    const logisticsData = trendData.map(item => item.logistics)
    const packagingData = trendData.map(item => item.packaging)
    const otherData = trendData.map(item => item.other)

    costTrendChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      legend: {
        data: ['原料成本', '人工成本', '物流成本', '包装成本', '其他成本']
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
        data: xData
      },
      yAxis: {
        type: 'value',
        name: '成本(元)'
      },
      series: [
        {
          name: '原料成本',
          type: 'line',
          stack: 'Total',
          smooth: true,
          data: materialData,
          areaStyle: {},
          itemStyle: { color: '#409eff' }
        },
        {
          name: '人工成本',
          type: 'line',
          stack: 'Total',
          smooth: true,
          data: laborData,
          areaStyle: {},
          itemStyle: { color: '#67c23a' }
        },
        {
          name: '物流成本',
          type: 'line',
          stack: 'Total',
          smooth: true,
          data: logisticsData,
          areaStyle: {},
          itemStyle: { color: '#e6a23c' }
        },
        {
          name: '包装成本',
          type: 'line',
          stack: 'Total',
          smooth: true,
          data: packagingData,
          areaStyle: {},
          itemStyle: { color: '#909399' }
        },
        {
          name: '其他成本',
          type: 'line',
          stack: 'Total',
          smooth: true,
          data: otherData,
          areaStyle: {},
          itemStyle: { color: '#f56c6c' }
        }
      ]
    })
  }).catch(err => {
    console.error('加载成本趋势失败', err)
  })
}

function initCharts() {
  // 成本趋势图
  costTrendChart = echarts.init(costTrendChartRef.value)
  loadCostTrend()

  // 成本结构分布
  costStructureChart = echarts.init(costStructureChartRef.value)
  updateCostStructureChart()

  // 成本对比分析
  costCompareChart = echarts.init(costCompareChartRef.value)
  costCompareChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['上月', '本月']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['原料成本', '人工成本', '物流成本', '包装成本', '其他成本']
    },
    yAxis: {
      type: 'value',
      name: '成本(元)'
    },
    series: [
      {
        name: '上月',
        type: 'bar',
        data: [0, 0, 0, 0, 0],
        itemStyle: { color: '#909399' }
      },
      {
        name: '本月',
        type: 'bar',
        data: [0, 0, 0, 0, 0],
        itemStyle: { color: '#409eff' }
      }
    ]
  })

  // 响应式
  window.addEventListener('resize', () => {
    costTrendChart?.resize()
    costStructureChart?.resize()
    costCompareChart?.resize()
  })
}

function updateCostStructureChart() {
  if (!costStructureChart) return
  
  const data = [
    { value: costOverview.materialCost, name: '原料成本', itemStyle: { color: '#409eff' } },
    { value: costOverview.laborCost, name: '人工成本', itemStyle: { color: '#67c23a' } },
    { value: costOverview.otherCost, name: '其他成本', itemStyle: { color: '#e6a23c' } }
  ].filter(item => item.value > 0)
  
  if (data.length === 0) {
    costStructureChart.setOption({
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 14
        }
      }
    })
    return
  }
  
  costStructureChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
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
          show: true,
          formatter: '{b}\n¥{c}'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: data
      }
    ]
  })
}

function loadCostDetails() {
  console.log('开始加载成本明细...')
  loading.value = true
  const params = {
    page: pagination.page,
    size: pagination.size,
    type: costType.value
  }
  
  if (dateRange.value && dateRange.value.length === 2) {
    params.start_date = dateRange.value[0]
    params.end_date = dateRange.value[1]
  }
  
  console.log('请求参数:', params)
  getCostRecords(params).then(res => {
    console.log('成本明细数据:', res)
    costList.value = res.records || []
    pagination.total = res.total || 0
  }).catch(err => {
    console.error('加载成本明细失败:', err)
    ElMessage.error('加载成本明细失败')
  }).finally(() => {
    loading.value = false
  })
}

function loadOverview() {
  console.log('开始加载成本概览...')
  getCostOverview().then(res => {
    console.log('成本概览数据:', res)
    Object.assign(costOverview, res)
    // 更新成本结构图
    updateCostStructureChart()
  }).catch(err => {
    console.error('加载成本概览失败', err)
    ElMessage.warning('加载成本概览失败，使用默认数据')
  })
}

function handleAddCost() {
  dialogTitle.value = '添加成本'
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogTitle.value = '编辑成本'
  Object.assign(costForm, row)
  dialogVisible.value = true
}

function handleDelete(row) {
  ElMessageBox.confirm('确定要删除这条成本记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    deleteCostRecord(row.id).then(() => {
      ElMessage.success('删除成功')
      loadCostDetails()
      loadOverview()
    }).catch(err => {
      ElMessage.error('删除失败')
      console.error(err)
    })
  }).catch(() => {})
}

function handleSubmit() {
  costFormRef.value.validate((valid) => {
    if (valid) {
      const isEdit = !!costForm.id
      const apiCall = isEdit 
        ? updateCostRecord(costForm.id, costForm)
        : createCostRecord(costForm)
      
      apiCall.then(() => {
        ElMessage.success(dialogTitle.value + '成功')
        dialogVisible.value = false
        loadCostDetails()
        loadOverview()
      }).catch(err => {
        ElMessage.error(dialogTitle.value + '失败')
        console.error(err)
      })
    }
  })
}

function resetForm() {
  costFormRef.value?.resetFields()
  Object.assign(costForm, {
    date: '',
    type: '',
    category: '',
    quantity: 0,
    unitPrice: 0,
    amount: 0,
    remark: ''
  })
}

function handleExport() {
  ElMessage.success('导出功能开发中')
}

onMounted(async () => {
  try {
    pageLoading.value = true
    initCharts()
    
    // 并行加载数据
    await Promise.all([
      loadOverview(),
      loadCostDetails()
    ])
  } catch (err) {
    console.error('页面初始化失败', err)
    ElMessage.error('页面加载失败，请刷新重试')
  } finally {
    pageLoading.value = false
  }
})

onUnmounted(() => {
  costTrendChart?.dispose()
  costStructureChart?.dispose()
  costCompareChart?.dispose()
})
</script>

<style lang="scss" scoped>
.cost-analysis {
  padding: 20px;

  .cost-cards {
    margin-bottom: 20px;

    .cost-card {
      .cost-content {
        display: flex;
        align-items: center;
        gap: 20px;

        .cost-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          color: white;
        }

        .cost-info {
          flex: 1;

          .cost-label {
            font-size: 14px;
            color: #909399;
            margin-bottom: 8px;
          }

          .cost-value {
            font-size: 24px;
            font-weight: 700;
            color: #303133;
            margin-bottom: 4px;
          }

          .cost-compare,
          .cost-percent {
            font-size: 12px;
            color: #909399;
          }
        }
      }

      &.total .cost-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.material .cost-icon {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }

      &.labor .cost-icon {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      }

      &.other .cost-icon {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
      }
    }
  }

  .chart-card,
  .table-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;

      .header-actions {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
      }
    }
  }

  .amount-text {
    font-weight: 600;
    color: #f56c6c;
  }
}
</style>
