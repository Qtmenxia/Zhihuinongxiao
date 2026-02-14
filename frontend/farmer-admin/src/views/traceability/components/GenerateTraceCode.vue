<template>
  <div class="generate-trace-code">
    <el-alert
      title="生成溯源二维码"
      type="success"
      :closable="false"
      show-icon
    >
      <p>为产品批次生成唯一的溯源二维码，消费者扫码即可查看产品的完整溯源信息。</p>
    </el-alert>

    <el-card class="form-card">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="选择批次" prop="batchNo">
          <el-select 
            v-model="formData.batchNo" 
            placeholder="请选择已有批次"
            style="width: 100%"
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

        <el-divider content-position="left">批次信息</el-divider>

        <el-form-item label="产品名称">
          <el-input v-model="batchInfo.productName" disabled />
        </el-form-item>

        <el-form-item label="产地">
          <el-input v-model="batchInfo.origin" disabled />
        </el-form-item>

        <el-form-item label="采收日期">
          <el-input v-model="batchInfo.harvestDate" disabled />
        </el-form-item>

        <el-form-item label="数量">
          <el-input v-model="batchInfo.quantity" disabled>
            <template #append>{{ batchInfo.unit }}</template>
          </el-input>
        </el-form-item>

        <el-form-item label="认证信息">
          <el-input v-model="batchInfo.certification" disabled />
        </el-form-item>

        <el-divider content-position="left">二维码设置</el-divider>

        <el-form-item label="二维码尺寸">
          <el-radio-group v-model="formData.size">
            <el-radio label="small">小 (200x200)</el-radio>
            <el-radio label="medium">中 (300x300)</el-radio>
            <el-radio label="large">大 (400x400)</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="包含Logo">
          <el-switch v-model="formData.includeLogo" />
          <span class="form-tip">在二维码中心添加品牌Logo</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleGenerate" :loading="generating">
            <el-icon><Stamp /></el-icon>生成二维码
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 生成结果 -->
    <el-card v-if="qrCodeGenerated" class="result-card">
      <template #header>
        <div class="card-header">
          <span>生成结果</span>
          <el-tag type="success">生成成功</el-tag>
        </div>
      </template>

      <el-row :gutter="30">
        <el-col :xs="24" :md="12">
          <div class="qr-preview">
            <div class="qr-code">
              <el-icon :size="getSizePixels()" color="#409eff"><Connection /></el-icon>
            </div>
            <p class="qr-label">批次号：{{ formData.batchNo }}</p>
          </div>
        </el-col>

        <el-col :xs="24" :md="12">
          <div class="qr-actions">
            <h3>下载选项</h3>
            <el-space direction="vertical" :size="15" style="width: 100%">
              <el-button type="primary" @click="downloadQrCode('png')" block>
                <el-icon><Download /></el-icon>下载PNG格式
              </el-button>
              <el-button type="success" @click="downloadQrCode('svg')" block>
                <el-icon><Download /></el-icon>下载SVG格式
              </el-button>
              <el-button type="warning" @click="downloadQrCode('pdf')" block>
                <el-icon><Download /></el-icon>下载PDF格式
              </el-button>
            </el-space>

            <el-divider />

            <h3>使用说明</h3>
            <ul class="usage-tips">
              <li>建议使用防水标签纸打印</li>
              <li>粘贴在产品包装显眼位置</li>
              <li>确保二维码清晰可扫描</li>
              <li>避免折叠或损坏二维码</li>
            </ul>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const formRef = ref(null)
const generating = ref(false)
const qrCodeGenerated = ref(false)

const batchList = ref([
  {
    batchNo: 'BZ2024020001',
    productName: '有机玉露香梨',
    origin: '山西省临汾市蒲县被子垣村',
    harvestDate: '2024-10-15',
    quantity: 500,
    unit: '斤',
    certification: '有机认证'
  },
  {
    batchNo: 'BZ2024020002',
    productName: '维纳斯黄金苹果',
    origin: '山西省临汾市蒲县',
    harvestDate: '2024-10-20',
    quantity: 1000,
    unit: '斤',
    certification: '有机认证'
  }
])

const formData = reactive({
  batchNo: '',
  size: 'medium',
  includeLogo: true
})

const batchInfo = reactive({
  productName: '',
  origin: '',
  harvestDate: '',
  quantity: '',
  unit: '',
  certification: ''
})

const formRules = {
  batchNo: [{ required: true, message: '请选择批次', trigger: 'change' }]
}

function handleBatchChange(batchNo) {
  const batch = batchList.value.find(b => b.batchNo === batchNo)
  if (batch) {
    Object.assign(batchInfo, batch)
  }
  qrCodeGenerated.value = false
}

async function handleGenerate() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    generating.value = true
    try {
      await new Promise(resolve => setTimeout(resolve, 1500))
      qrCodeGenerated.value = true
      ElMessage.success('二维码生成成功')
    } catch (error) {
      ElMessage.error('生成失败')
    } finally {
      generating.value = false
    }
  })
}

function handleReset() {
  formData.batchNo = ''
  formData.size = 'medium'
  formData.includeLogo = true
  Object.assign(batchInfo, {
    productName: '',
    origin: '',
    harvestDate: '',
    quantity: '',
    unit: '',
    certification: ''
  })
  qrCodeGenerated.value = false
}

function getSizePixels() {
  const sizes = {
    small: 200,
    medium: 300,
    large: 400
  }
  return sizes[formData.size] || 300
}

function downloadQrCode(format) {
  ElMessage.success(`正在下载${format.toUpperCase()}格式二维码...`)
}
</script>

<style lang="scss" scoped>
.generate-trace-code {
  .form-card {
    margin-top: 20px;

    .form-tip {
      margin-left: 10px;
      font-size: 13px;
      color: #909399;
    }
  }

  .result-card {
    margin-top: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .qr-preview {
      text-align: center;
      padding: 30px;
      background: #f5f7fa;
      border-radius: 8px;

      .qr-code {
        display: inline-block;
        padding: 20px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      }

      .qr-label {
        margin-top: 15px;
        font-size: 14px;
        color: #606266;
        font-weight: 500;
      }
    }

    .qr-actions {
      h3 {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 15px;
      }

      .usage-tips {
        list-style: none;
        padding: 0;
        margin: 0;

        li {
          padding: 8px 0;
          font-size: 14px;
          color: #606266;
          position: relative;
          padding-left: 20px;

          &:before {
            content: "•";
            position: absolute;
            left: 0;
            color: #409eff;
            font-weight: bold;
            font-size: 18px;
          }
        }
      }
    }
  }
}
</style>

