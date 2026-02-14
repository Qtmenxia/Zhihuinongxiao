<template>
  <div class="logistics-info">
    <el-alert
      title="物流信息管理"
      type="info"
      :closable="false"
      show-icon
    >
      <p>记录产品从发货到签收的全过程，让消费者实时了解物流状态。</p>
    </el-alert>

    <!-- 选择批次 -->
    <el-card class="select-card">
      <el-form :inline="true">
        <el-form-item label="选择批次">
          <el-select 
            v-model="selectedBatch" 
            placeholder="请选择批次"
            style="width: 300px"
            @change="handleBatchChange"
          >
            <el-option
              v-for="batch in batchList"
              :key="batch.batchNo"
              :label="`${batch.batchNo} - ${batch.productName}`"
              :value="batch.batchNo"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleAddNode">
            <el-icon><Plus /></el-icon>添加物流节点
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 物流时间线 -->
    <el-card v-if="selectedBatch" class="timeline-card">
      <template #header>
        <div class="card-header">
          <span>物流轨迹</span>
          <el-tag>批次号：{{ selectedBatch }}</el-tag>
        </div>
      </template>

      <el-timeline v-if="logisticsNodes.length > 0">
        <el-timeline-item
          v-for="node in logisticsNodes"
          :key="node.id"
          :timestamp="formatDateTime(node.time)"
          :type="getNodeType(node.status)"
          :icon="getNodeIcon(node.status)"
        >
          <el-card>
            <div class="node-content">
              <div class="node-header">
                <h4>{{ node.title }}</h4>
                <el-tag :type="getNodeType(node.status)" size="small">
                  {{ node.status }}
                </el-tag>
              </div>
              <p class="node-desc">{{ node.description }}</p>
              <div class="node-meta">
                <span v-if="node.location">
                  <el-icon><Location /></el-icon>{{ node.location }}
                </span>
                <span v-if="node.operator">
                  <el-icon><User /></el-icon>{{ node.operator }}
                </span>
              </div>
              <div class="node-actions">
                <el-button type="primary" link @click="handleEditNode(node)">编辑</el-button>
                <el-button type="danger" link @click="handleDeleteNode(node)">删除</el-button>
              </div>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <el-empty v-else description="暂无物流信息" />
    </el-card>

    <!-- 添加/编辑节点弹窗 -->
    <el-dialog 
      v-model="nodeDialogVisible" 
      :title="nodeMode === 'add' ? '添加物流节点' : '编辑物流节点'" 
      width="600px"
    >
      <el-form :model="nodeForm" :rules="nodeRules" ref="nodeFormRef" label-width="100px">
        <el-form-item label="节点类型" prop="status">
          <el-select v-model="nodeForm.status" placeholder="请选择节点类型">
            <el-option label="已发货" value="已发货" />
            <el-option label="运输中" value="运输中" />
            <el-option label="到达中转站" value="到达中转站" />
            <el-option label="派送中" value="派送中" />
            <el-option label="已签收" value="已签收" />
          </el-select>
        </el-form-item>

        <el-form-item label="标题" prop="title">
          <el-input v-model="nodeForm.title" placeholder="如：商品已发货" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="nodeForm.description" 
            type="textarea"
            :rows="3"
            placeholder="详细描述物流状态"
          />
        </el-form-item>

        <el-form-item label="地点" prop="location">
          <el-input v-model="nodeForm.location" placeholder="如：山西省临汾市" />
        </el-form-item>

        <el-form-item label="操作人" prop="operator">
          <el-input v-model="nodeForm.operator" placeholder="如：快递员张三" />
        </el-form-item>

        <el-form-item label="时间" prop="time">
          <el-date-picker
            v-model="nodeForm.time"
            type="datetime"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="nodeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitNode" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const selectedBatch = ref('')
const nodeDialogVisible = ref(false)
const nodeMode = ref('add')
const nodeFormRef = ref(null)
const submitting = ref(false)

const batchList = ref([
  { batchNo: 'BZ2024020001', productName: '有机玉露香梨' },
  { batchNo: 'BZ2024020002', productName: '维纳斯黄金苹果' }
])

const logisticsNodes = ref([])

const nodeForm = reactive({
  status: '',
  title: '',
  description: '',
  location: '',
  operator: '',
  time: null
})

const nodeRules = {
  status: [{ required: true, message: '请选择节点类型', trigger: 'change' }],
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入描述', trigger: 'blur' }],
  time: [{ required: true, message: '请选择时间', trigger: 'change' }]
}

function handleBatchChange(batchNo) {
  // 模拟加载物流数据
  if (batchNo === 'BZ2024020001') {
    logisticsNodes.value = [
      {
        id: 1,
        status: '已签收',
        title: '客户已签收',
        description: '您的包裹已被本人签收，感谢使用顺丰速运',
        location: '北京市朝阳区',
        operator: '客户本人',
        time: '2024-10-25T14:30:00'
      },
      {
        id: 2,
        status: '派送中',
        title: '快递员正在派送',
        description: '快递员张三正在为您派送，请保持电话畅通',
        location: '北京市朝阳区',
        operator: '快递员张三',
        time: '2024-10-25T09:00:00'
      },
      {
        id: 3,
        status: '到达中转站',
        title: '到达北京中转站',
        description: '快件已到达北京中转站，准备派送',
        location: '北京市',
        operator: '中转站',
        time: '2024-10-24T18:00:00'
      },
      {
        id: 4,
        status: '运输中',
        title: '运输途中',
        description: '您的快件正在运输途中',
        location: '河北省石家庄市',
        operator: '运输车辆',
        time: '2024-10-23T12:00:00'
      },
      {
        id: 5,
        status: '已发货',
        title: '商品已发货',
        description: '您的订单已从山西蒲县发出，顺丰速运承运',
        location: '山西省临汾市蒲县',
        operator: '发货员',
        time: '2024-10-22T10:00:00'
      }
    ]
  } else {
    logisticsNodes.value = []
  }
}

function handleAddNode() {
  if (!selectedBatch.value) {
    ElMessage.warning('请先选择批次')
    return
  }
  
  nodeMode.value = 'add'
  Object.assign(nodeForm, {
    status: '',
    title: '',
    description: '',
    location: '',
    operator: '',
    time: new Date()
  })
  nodeDialogVisible.value = true
}

function handleEditNode(node) {
  nodeMode.value = 'edit'
  Object.assign(nodeForm, {
    ...node,
    time: new Date(node.time)
  })
  nodeDialogVisible.value = true
}

async function handleDeleteNode(node) {
  try {
    await ElMessageBox.confirm('确定要删除这个物流节点吗？', '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    logisticsNodes.value = logisticsNodes.value.filter(n => n.id !== node.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleSubmitNode() {
  if (!nodeFormRef.value) return

  await nodeFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (nodeMode.value === 'add') {
        logisticsNodes.value.unshift({
          id: Date.now(),
          ...nodeForm
        })
        ElMessage.success('添加成功')
      } else {
        ElMessage.success('更新成功')
      }
      
      nodeDialogVisible.value = false
    } catch (error) {
      ElMessage.error('操作失败')
    } finally {
      submitting.value = false
    }
  })
}

function formatDateTime(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

function getNodeType(status) {
  const types = {
    '已发货': 'primary',
    '运输中': 'info',
    '到达中转站': 'warning',
    '派送中': 'success',
    '已签收': 'success'
  }
  return types[status] || 'info'
}

function getNodeIcon(status) {
  const icons = {
    '已发货': 'Van',
    '运输中': 'Van',
    '到达中转站': 'Location',
    '派送中': 'User',
    '已签收': 'CircleCheck'
  }
  return icons[status] || 'InfoFilled'
}
</script>

<style lang="scss" scoped>
.logistics-info {
  .select-card {
    margin-top: 20px;
  }

  .timeline-card {
    margin-top: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .node-content {
      .node-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;

        h4 {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin: 0;
        }
      }

      .node-desc {
        font-size: 14px;
        color: #606266;
        margin-bottom: 10px;
      }

      .node-meta {
        display: flex;
        gap: 20px;
        font-size: 13px;
        color: #909399;
        margin-bottom: 10px;

        span {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }

      .node-actions {
        display: flex;
        gap: 10px;
      }
    }
  }
}
</style>

