<template>
  <div class="service-generate">
    <el-card class="generate-card">
      <template #header>
        <div class="card-header">
          <el-icon><MagicStick /></el-icon>
          <span>AI智能服务生成</span>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="currentStep" finish-status="success" align-center class="steps">
        <el-step title="描述需求" description="用自然语言描述您的需求" />
        <el-step title="AI生成" description="MCPybarra自动生成代码" />
        <el-step title="测试部署" description="验证并部署服务" />
      </el-steps>
      
      <!-- Step 1: 输入需求 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item label="服务需求描述" prop="requirement">
            <el-input
              v-model="form.requirement"
              type="textarea"
              :rows="6"
              placeholder="请用自然语言描述您需要的电商服务功能，例如：
• 我需要一个订单查询工具，客户输入手机号就能看到订单状态
• 帮我做一个库存管理服务，能够实时更新玉露香梨的库存数量
• 创建一个客服问答工具，自动回答关于产品价格、发货时间的问题"
              maxlength="2000"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item label="产品类别">
            <el-select v-model="form.productCategory" placeholder="选择相关产品类别（可选）">
              <el-option label="玉露香梨" value="yuluxiangli" />
              <el-option label="维纳斯黄金苹果" value="venus_apple" />
              <el-option label="苹果脆片" value="apple_chips" />
              <el-option label="梨汁饮品" value="pear_juice" />
              <el-option label="通用" value="general" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="AI模型">
            <el-radio-group v-model="form.model">
              <el-radio-button label="gemini-2.5-pro">
                Gemini 2.5 Pro
                <el-tag size="small" type="success">推荐</el-tag>
              </el-radio-button>
              <el-radio-button label="gpt-4o">GPT-4o</el-radio-button>
              <el-radio-button label="qwen-max">通义千问Max</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <!-- 成本预估 -->
          <el-alert type="info" :closable="false" class="cost-alert">
            <template #title>
              <div class="cost-info">
                <span>预估生成成本：</span>
                <strong>${{ estimatedCost.min.toFixed(3) }} - ${{ estimatedCost.max.toFixed(3) }}</strong>
                <span class="cost-cny">（约 ¥{{ (estimatedCost.max * 7.2).toFixed(2) }}）</span>
              </div>
            </template>
            <p>实际成本根据需求复杂度和生成轮次确定，通常在预估范围内。</p>
          </el-alert>
        </el-form>
        
        <div class="step-actions">
          <el-button type="primary" size="large" @click="startGeneration" :loading="generating">
            <el-icon><MagicStick /></el-icon>
            开始生成
          </el-button>
        </div>
      </div>
      
      <!-- Step 2: 生成进度 -->
      <div v-else-if="currentStep === 1" class="step-content generation-progress">
        <div class="progress-container">
          <el-progress 
            type="circle" 
            :percentage="progress" 
            :width="200"
            :stroke-width="12"
            :color="progressColor"
          >
            <template #default>
              <div class="progress-inner">
                <span class="progress-value">{{ progress }}%</span>
                <span class="progress-stage">{{ currentStage }}</span>
              </div>
            </template>
          </el-progress>
        </div>
        
        <div class="stage-timeline">
          <el-timeline>
            <el-timeline-item
              v-for="(stage, index) in stages"
              :key="stage.key"
              :type="getStageType(stage.key)"
              :hollow="!isStageComplete(stage.key)"
              :timestamp="stage.time"
              placement="top"
            >
              <el-card shadow="hover" class="stage-card">
                <div class="stage-header">
                  <el-icon :class="{ 'is-loading': isCurrentStage(stage.key) }">
                    <component :is="stage.icon" />
                  </el-icon>
                  <span>{{ stage.title }}</span>
                </div>
                <p class="stage-desc">{{ stage.description }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
        
        <div class="generation-info">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="服务ID">{{ serviceId }}</el-descriptions-item>
            <el-descriptions-item label="使用模型">{{ form.model }}</el-descriptions-item>
            <el-descriptions-item label="已用时间">{{ elapsedTime }}</el-descriptions-item>
            <el-descriptions-item label="预计剩余">{{ estimatedRemaining }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      
      <!-- Step 3: 生成完成 -->
      <div v-else class="step-content generation-complete">
        <el-result
          :icon="generationResult.success ? 'success' : 'error'"
          :title="generationResult.success ? '服务生成成功！' : '生成失败'"
          :sub-title="generationResult.message"
        >
          <template #extra>
            <div v-if="generationResult.success" class="result-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="服务名称">{{ generationResult.name }}</el-descriptions-item>
                <el-descriptions-item label="生成成本">${{ generationResult.cost?.toFixed(4) }}</el-descriptions-item>
                <el-descriptions-item label="质量评分">
                  <el-rate v-model="generationResult.qualityScore" disabled :max="5" />
                </el-descriptions-item>
                <el-descriptions-item label="生成耗时">{{ generationResult.time }}秒</el-descriptions-item>
              </el-descriptions>
              
              <div class="result-actions">
                <el-button type="primary" @click="viewService">
                  <el-icon><View /></el-icon>
                  查看详情
                </el-button>
                <el-button type="success" @click="deployService">
                  <el-icon><Upload /></el-icon>
                  立即部署
                </el-button>
                <el-button @click="generateAnother">
                  <el-icon><RefreshRight /></el-icon>
                  再生成一个
                </el-button>
              </div>
            </div>
            <div v-else class="error-actions">
              <el-button type="primary" @click="retryGeneration">
                <el-icon><RefreshRight /></el-icon>
                重新生成
              </el-button>
              <el-button @click="goBack">返回</el-button>
            </div>
          </template>
        </el-result>
      </div>
    </el-card>
    
    <!-- 生成提示 -->
    <el-card class="tips-card" v-if="currentStep === 0">
      <template #header>
        <el-icon><InfoFilled /></el-icon>
        <span>生成提示</span>
      </template>
      <ul class="tips-list">
        <li>
          <strong>描述越具体，生成效果越好</strong>
          <p>包含具体的功能点、输入输出格式、业务规则等</p>
        </li>
        <li>
          <strong>可以参考示例需求</strong>
          <p>订单查询、库存管理、智能客服、价格计算等都是常见场景</p>
        </li>
        <li>
          <strong>生成过程约需3-8分钟</strong>
          <p>包含规划、编码、测试、优化四个阶段，请耐心等待</p>
        </li>
        <li>
          <strong>生成成本极低</strong>
          <p>平均每次生成成本$0.05-0.15，远低于传统开发</p>
        </li>
      </ul>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { generateService, getServiceStatus, ServiceWebSocket } from '@/api/service'

const router = useRouter()

// 表单
const formRef = ref(null)
const form = reactive({
  requirement: '',
  productCategory: '',
  model: 'gemini-2.5-pro'
})

const rules = {
  requirement: [
    { required: true, message: '请描述您的服务需求', trigger: 'blur' },
    { min: 20, message: '需求描述至少20个字符', trigger: 'blur' }
  ]
}

// 状态
const currentStep = ref(0)
const generating = ref(false)
const serviceId = ref('')
const progress = ref(0)
const currentStage = ref('准备中')
const startTime = ref(null)
const elapsedTime = ref('0秒')
const estimatedRemaining = ref('计算中...')

// WebSocket连接
let ws = null
let timer = null

// 生成阶段
const stages = ref([
  { key: 'planning', title: 'Planning 规划', icon: 'Edit', description: '分析需求，设计API接口', time: '', complete: false },
  { key: 'coding', title: 'Coding 编码', icon: 'Document', description: '生成完整Python代码', time: '', complete: false },
  { key: 'testing', title: 'Testing 测试', icon: 'Check', description: '执行自动化测试验证', time: '', complete: false },
  { key: 'refining', title: 'Refining 优化', icon: 'MagicStick', description: '根据测试结果优化代码', time: '', complete: false }
])

// 生成结果
const generationResult = reactive({
  success: false,
  name: '',
  cost: 0,
  qualityScore: 0,
  time: 0,
  message: ''
})

// 预估成本
const estimatedCost = computed(() => {
  const baseCost = {
    'gemini-2.5-pro': { min: 0.02, max: 0.08 },
    'gpt-4o': { min: 0.05, max: 0.15 },
    'qwen-max': { min: 0.01, max: 0.05 }
  }
  return baseCost[form.model] || { min: 0.02, max: 0.10 }
})

// 进度颜色
const progressColor = computed(() => {
  if (progress.value < 30) return '#909399'
  if (progress.value < 60) return '#E6A23C'
  if (progress.value < 90) return '#409EFF'
  return '#67C23A'
})

// 阶段状态判断
function isCurrentStage(key) {
  const stageOrder = ['planning', 'coding', 'testing', 'refining']
  const currentIndex = stageOrder.indexOf(currentStage.value?.toLowerCase())
  return stageOrder.indexOf(key) === currentIndex
}

function isStageComplete(key) {
  const stage = stages.value.find(s => s.key === key)
  return stage?.complete || false
}

function getStageType(key) {
  if (isStageComplete(key)) return 'success'
  if (isCurrentStage(key)) return 'primary'
  return 'info'
}

// 开始生成
async function startGeneration() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  generating.value = true
  currentStep.value = 1
  startTime.value = Date.now()
  
  try {
    const res = await generateService({
      requirement: form.requirement,
      product_category: form.productCategory,
      model: form.model
    })
    
    serviceId.value = res.data.service_id
    
    // 启动WebSocket监听进度
    connectWebSocket()
    
    // 启动计时器
    startTimer()
    
    // 开始轮询状态（备用方案）
    pollStatus()
    
  } catch (error) {
    ElMessage.error('启动服务生成失败: ' + error.message)
    currentStep.value = 0
    generating.value = false
  }
}

// WebSocket连接
function connectWebSocket() {
  ws = new ServiceWebSocket(serviceId.value, {
    onProgress: (data) => {
      progress.value = data.progress || 0
      currentStage.value = data.current_stage || currentStage.value
      updateStageStatus(data.current_stage)
    },
    onComplete: (result) => {
      handleComplete(result)
    },
    onError: (error) => {
      handleError(error)
    }
  })
  ws.connect()
}

// 轮询状态（WebSocket的备用方案）
async function pollStatus() {
  if (currentStep.value !== 1) return
  
  try {
    const res = await getServiceStatus(serviceId.value)
    const data = res.data
    
    if (data.status === 'ready') {
      handleComplete({
        service_id: serviceId.value,
        cost: data.cost,
        quality_score: data.quality_score,
        generation_time: data.generation_time
      })
    } else if (data.status === 'failed') {
      handleError('服务生成失败')
    } else {
      progress.value = data.progress || progress.value
      currentStage.value = data.current_stage || currentStage.value
      
      // 继续轮询
      setTimeout(pollStatus, 3000)
    }
  } catch (error) {
    console.error('Poll status error:', error)
    setTimeout(pollStatus, 5000)
  }
}

// 更新阶段状态
function updateStageStatus(stage) {
  const stageOrder = ['planning', 'coding', 'testing', 'refining']
  const currentIndex = stageOrder.indexOf(stage?.toLowerCase())
  
  stages.value.forEach((s, index) => {
    if (stageOrder.indexOf(s.key) < currentIndex) {
      s.complete = true
      if (!s.time) s.time = new Date().toLocaleTimeString()
    } else if (stageOrder.indexOf(s.key) === currentIndex) {
      if (!s.time) s.time = new Date().toLocaleTimeString()
    }
  })
}

// 处理完成
function handleComplete(result) {
  stopTimer()
  ws?.disconnect()
  
  progress.value = 100
  currentStep.value = 2
  generating.value = false
  
  // 标记所有阶段完成
  stages.value.forEach(s => {
    s.complete = true
    if (!s.time) s.time = new Date().toLocaleTimeString()
  })
  
  generationResult.success = true
  generationResult.name = result.name || serviceId.value
  generationResult.cost = result.cost || 0
  generationResult.qualityScore = (result.quality_score || 80) / 20 // 转换为5分制
  generationResult.time = result.generation_time || Math.floor((Date.now() - startTime.value) / 1000)
  generationResult.message = '您的MCP服务已成功生成，可以查看代码或直接部署使用'
  
  ElMessage.success('服务生成成功！')
}

// 处理错误
function handleError(error) {
  stopTimer()
  ws?.disconnect()
  
  currentStep.value = 2
  generating.value = false
  
  generationResult.success = false
  generationResult.message = error || '服务生成过程中发生错误，请重试'
  
  ElMessage.error('服务生成失败')
}

// 计时器
function startTimer() {
  timer = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime.value) / 1000)
    const minutes = Math.floor(elapsed / 60)
    const seconds = elapsed % 60
    elapsedTime.value = minutes > 0 ? `${minutes}分${seconds}秒` : `${seconds}秒`
    
    // 估算剩余时间
    if (progress.value > 0) {
      const totalEstimate = (elapsed / progress.value) * 100
      const remaining = Math.max(0, Math.floor(totalEstimate - elapsed))
      const remMinutes = Math.floor(remaining / 60)
      const remSeconds = remaining % 60
      estimatedRemaining.value = remMinutes > 0 ? `约${remMinutes}分${remSeconds}秒` : `约${remSeconds}秒`
    }
  }, 1000)
}

function stopTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

// 操作函数
function viewService() {
  router.push(`/service/detail/${serviceId.value}`)
}

function deployService() {
  router.push(`/service/detail/${serviceId.value}?action=deploy`)
}

function generateAnother() {
  currentStep.value = 0
  progress.value = 0
  serviceId.value = ''
  form.requirement = ''
  stages.value.forEach(s => {
    s.complete = false
    s.time = ''
  })
}

function retryGeneration() {
  currentStep.value = 0
  progress.value = 0
}

function goBack() {
  router.back()
}

// 清理
onUnmounted(() => {
  stopTimer()
  ws?.disconnect()
})
</script>

<style lang="scss" scoped>
.service-generate {
  max-width: 1000px;
  margin: 0 auto;
}

.generate-card {
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
    
    .el-icon {
      color: #409EFF;
    }
  }
  
  .steps {
    margin: 30px 0;
  }
  
  .step-content {
    padding: 20px 0;
  }
  
  .cost-alert {
    margin-top: 20px;
    
    .cost-info {
      display: flex;
      align-items: center;
      gap: 8px;
      
      strong {
        color: #67C23A;
        font-size: 18px;
      }
      
      .cost-cny {
        color: #909399;
        font-size: 12px;
      }
    }
  }
  
  .step-actions {
    text-align: center;
    margin-top: 30px;
  }
}

.generation-progress {
  .progress-container {
    display: flex;
    justify-content: center;
    margin-bottom: 40px;
    
    .progress-inner {
      display: flex;
      flex-direction: column;
      align-items: center;
      
      .progress-value {
        font-size: 32px;
        font-weight: 600;
        color: #303133;
      }
      
      .progress-stage {
        font-size: 14px;
        color: #909399;
        margin-top: 8px;
      }
    }
  }
  
  .stage-timeline {
    max-width: 600px;
    margin: 0 auto 30px;
    
    .stage-card {
      .stage-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        margin-bottom: 8px;
        
        .el-icon {
          font-size: 18px;
          color: #409EFF;
          
          &.is-loading {
            animation: rotate 1s linear infinite;
          }
        }
      }
      
      .stage-desc {
        margin: 0;
        font-size: 13px;
        color: #909399;
      }
    }
  }
  
  .generation-info {
    max-width: 500px;
    margin: 0 auto;
  }
}

.generation-complete {
  .result-info {
    .el-descriptions {
      margin-bottom: 30px;
    }
    
    .result-actions {
      display: flex;
      justify-content: center;
      gap: 16px;
    }
  }
  
  .error-actions {
    display: flex;
    justify-content: center;
    gap: 16px;
  }
}

.tips-card {
  margin-top: 20px;
  
  :deep(.el-card__header) {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .el-icon {
      color: #E6A23C;
    }
  }
  
  .tips-list {
    margin: 0;
    padding-left: 20px;
    
    li {
      margin-bottom: 16px;
      
      strong {
        color: #303133;
      }
      
      p {
        margin: 4px 0 0;
        font-size: 13px;
        color: #909399;
      }
    }
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
