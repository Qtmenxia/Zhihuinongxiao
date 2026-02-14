<template>
  <div class="product-edit">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑产品' : '添加产品' }}</span>
          <el-button @click="handleBack">
            <el-icon><Back /></el-icon>返回
          </el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        class="product-form"
        v-loading="loading"
      >
        <!-- 基础信息 -->
        <div class="form-section">
          <div class="section-title">基础信息</div>
          
          <el-form-item label="产品名称" prop="name">
            <el-input
              v-model="formData.name"
              placeholder="请输入产品名称"
              maxlength="200"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="SKU编码" prop="sku_code">
            <el-input
              v-model="formData.sku_code"
              placeholder="请输入SKU编码，如：YLX-158-9E"
              :disabled="isEdit"
            >
              <template #append>
                <el-button @click="generateSKU" :disabled="isEdit">自动生成</el-button>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="产品分类" prop="category">
            <el-select
              v-model="formData.category"
              placeholder="请选择产品分类"
              filterable
              allow-create
            >
              <el-option label="水果" value="水果" />
              <el-option label="坚果" value="坚果" />
              <el-option label="粮食" value="粮食" />
              <el-option label="干果" value="干果" />
              <el-option label="蜂产品" value="蜂产品" />
              <el-option label="菌类" value="菌类" />
              <el-option label="禽蛋" value="禽蛋" />
              <el-option label="蔬菜" value="蔬菜" />
              <el-option label="茶叶" value="茶叶" />
            </el-select>
          </el-form-item>

          <el-form-item label="产品描述" prop="description">
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="4"
              placeholder="请输入产品描述"
              maxlength="2000"
              show-word-limit
            />
          </el-form-item>
        </div>

        <!-- 规格与定价 -->
        <div class="form-section">
          <div class="section-title">规格与定价</div>

          <el-form-item label="产品规格" prop="specs">
            <div class="specs-input">
              <div
                v-for="(spec, index) in specsArray"
                :key="index"
                class="spec-item"
              >
                <el-input
                  v-model="spec.key"
                  placeholder="规格名称"
                  style="width: 150px"
                />
                <span class="separator">:</span>
                <el-input
                  v-model="spec.value"
                  placeholder="规格值"
                  style="width: 200px"
                />
                <el-button
                  type="danger"
                  link
                  @click="removeSpec(index)"
                  :disabled="specsArray.length === 1"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
              <el-button type="primary" link @click="addSpec">
                <el-icon><Plus /></el-icon>添加规格
              </el-button>
            </div>
          </el-form-item>

          <el-form-item label="售价" prop="price">
            <el-input-number
              v-model="formData.price"
              :min="0.01"
              :precision="2"
              :step="1"
              placeholder="请输入售价"
            />
            <span class="unit">元</span>
          </el-form-item>

          <el-form-item label="原价" prop="original_price">
            <el-input-number
              v-model="formData.original_price"
              :min="0"
              :precision="2"
              :step="1"
              placeholder="用于显示折扣，可不填"
            />
            <span class="unit">元</span>
          </el-form-item>
        </div>

        <!-- 库存管理 -->
        <div class="form-section">
          <div class="section-title">库存管理</div>

          <el-form-item label="库存数量" prop="stock">
            <el-input-number
              v-model="formData.stock"
              :min="0"
              :step="1"
              placeholder="请输入库存数量"
            />
            <span class="unit">件</span>
          </el-form-item>

          <el-form-item label="库存预警" prop="stock_alert_threshold">
            <el-input-number
              v-model="formData.stock_alert_threshold"
              :min="0"
              :step="1"
              placeholder="库存低于此值时预警"
            />
            <span class="unit">件</span>
          </el-form-item>
        </div>

        <!-- 营销信息 -->
        <div class="form-section">
          <div class="section-title">营销信息</div>

          <el-form-item label="目标场景" prop="target_scene">
            <el-input
              v-model="formData.target_scene"
              placeholder="如：送礼/节日/日常食用"
            />
          </el-form-item>

          <el-form-item label="包装类型" prop="packaging_type">
            <el-input
              v-model="formData.packaging_type"
              placeholder="如：天地盖礼盒/简装/散装"
            />
          </el-form-item>

          <el-form-item label="产品卖点" prop="selling_points">
            <div class="selling-points">
              <el-tag
                v-for="(point, index) in formData.selling_points"
                :key="index"
                closable
                @close="removeSellingPoint(index)"
                class="point-tag"
              >
                {{ point }}
              </el-tag>
              <el-input
                v-if="showPointInput"
                ref="pointInputRef"
                v-model="newPoint"
                size="small"
                style="width: 120px"
                @keyup.enter="addSellingPoint"
                @blur="addSellingPoint"
              />
              <el-button
                v-else
                size="small"
                @click="showAddPoint"
              >
                <el-icon><Plus /></el-icon>添加卖点
              </el-button>
            </div>
          </el-form-item>
        </div>

        <!-- 媒体资源 -->
        <div class="form-section">
          <div class="section-title">媒体资源</div>

          <el-form-item label="产品图片" prop="images">
            <div class="image-upload">
              <div class="image-list">
                <div
                  v-for="(image, index) in formData.images"
                  :key="index"
                  class="image-item"
                >
                  <img :src="getImageUrl(image)" alt="产品图片" />
                  <div class="image-actions">
                    <el-button
                      type="danger"
                      size="small"
                      circle
                      @click="removeImage(index)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
                <el-upload
                  class="upload-btn"
                  :show-file-list="false"
                  :before-upload="handleBeforeUpload"
                  :http-request="handleImageUpload"
                  accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                  :disabled="uploading"
                >
                  <div class="upload-content" v-loading="uploading">
                    <el-icon><Plus /></el-icon>
                    <span>{{ uploading ? '上传中...' : '上传图片' }}</span>
                  </div>
                </el-upload>
              </div>
              <div class="tip">
                建议尺寸：800x800px，支持JPG、PNG、GIF、WebP格式，单张最大10MB
              </div>
            </div>
          </el-form-item>

          <el-form-item label="产品视频" prop="video_url">
            <el-input
              v-model="formData.video_url"
              placeholder="请输入视频URL（选填）"
            />
          </el-form-item>
        </div>

        <!-- 溯源信息 -->
        <div class="form-section">
          <div class="section-title">溯源信息（选填）</div>

          <el-form-item label="产地信息">
            <el-input
              v-model="originInfo.location"
              placeholder="如：山西省隰县"
            />
          </el-form-item>

          <el-form-item label="种植方式">
            <el-input
              v-model="originInfo.method"
              placeholder="如：有机种植/绿色种植"
            />
          </el-form-item>

          <el-form-item label="认证信息">
            <el-input
              v-model="originInfo.certification"
              placeholder="如：有机认证/绿色食品认证"
            />
          </el-form-item>
        </div>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '保存修改' : '立即创建' }}
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button @click="handleBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getProductDetail, createProduct, updateProduct } from '@/api/product'
import { uploadImage, uploadImages } from '@/api/upload'

const route = useRoute()
const router = useRouter()

// 是否为编辑模式
const isEdit = computed(() => !!route.params.id)

// 表单引用
const formRef = ref(null)
const pointInputRef = ref(null)

// 加载状态
const loading = ref(false)
const submitting = ref(false)

// 表单数据
const formData = reactive({
  name: '',
  sku_code: '',
  category: '',
  description: '',
  specs: {},
  price: null,
  original_price: null,
  stock: 0,
  stock_alert_threshold: 10,
  target_scene: '',
  packaging_type: '',
  selling_points: [],
  images: [],
  video_url: '',
  origin_info: null
})

// 规格数组（用于动态表单）
const specsArray = ref([{ key: '', value: '' }])

// 溯源信息（用于表单输入）
const originInfo = reactive({
  location: '',
  method: '',
  certification: ''
})

// 卖点输入
const showPointInput = ref(false)
const newPoint = ref('')

// 图片上传
const uploading = ref(false)

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入产品名称', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  sku_code: [
    { required: true, message: '请输入SKU编码', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请选择产品分类', trigger: 'change' }
  ],
  price: [
    { required: true, message: '请输入售价', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '售价必须大于0', trigger: 'blur' }
  ],
  stock: [
    { required: true, message: '请输入库存数量', trigger: 'blur' }
  ]
}

// 生成SKU
function generateSKU() {
  const timestamp = Date.now().toString(36).toUpperCase()
  const random = Math.random().toString(36).substring(2, 5).toUpperCase()
  formData.sku_code = `SKU-${timestamp}-${random}`
}

// 规格管理
function addSpec() {
  specsArray.value.push({ key: '', value: '' })
}

function removeSpec(index) {
  if (specsArray.value.length > 1) {
    specsArray.value.splice(index, 1)
  }
}

// 卖点管理
function showAddPoint() {
  showPointInput.value = true
  nextTick(() => {
    pointInputRef.value?.focus()
  })
}

function addSellingPoint() {
  if (newPoint.value.trim()) {
    formData.selling_points.push(newPoint.value.trim())
    newPoint.value = ''
  }
  showPointInput.value = false
}

function removeSellingPoint(index) {
  formData.selling_points.splice(index, 1)
}

// 图片管理
function getImageUrl(url) {
  // 如果是相对路径，添加API基础URL
  if (url && url.startsWith('/uploads/')) {
    return `http://localhost:8000${url}`
  }
  return url
}

function handleBeforeUpload(file) {
  // 检查文件类型
  const isImage = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  if (!isImage) {
    ElMessage.error('只能上传 JPG/PNG/GIF/WebP 格式的图片!')
    return false
  }
  
  // 检查文件大小
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  
  return true
}

async function handleImageUpload(options) {
  const { file } = options
  
  uploading.value = true
  try {
    const result = await uploadImage(file)
    formData.images.push(result.url)
    ElMessage.success('图片上传成功')
  } catch (error) {
    console.error('Upload failed:', error)
    ElMessage.error('图片上传失败')
  } finally {
    uploading.value = false
  }
}

function removeImage(index) {
  formData.images.splice(index, 1)
}

// 加载产品详情
async function loadProduct() {
  if (!isEdit.value) return

  loading.value = true
  try {
    const product = await getProductDetail(route.params.id)
    
    // 填充表单数据
    Object.assign(formData, {
      name: product.name,
      sku_code: product.sku_code,
      category: product.category,
      description: product.description || '',
      specs: product.specs || {},
      price: product.price,
      original_price: product.original_price,
      stock: product.stock,
      stock_alert_threshold: product.stock_alert_threshold,
      target_scene: product.target_scene || '',
      packaging_type: product.packaging_type || '',
      selling_points: product.selling_points || [],
      images: product.images || [],
      video_url: product.video_url || '',
      origin_info: product.origin_info
    })

    // 转换规格为数组
    if (product.specs && Object.keys(product.specs).length > 0) {
      specsArray.value = Object.entries(product.specs).map(([key, value]) => ({
        key,
        value: String(value)
      }))
    }

    // 填充溯源信息
    if (product.origin_info) {
      Object.assign(originInfo, product.origin_info)
    }
  } catch (error) {
    console.error('Failed to load product:', error)
    ElMessage.error('加载产品信息失败')
    handleBack()
  } finally {
    loading.value = false
  }
}

// 提交表单
async function handleSubmit() {
  try {
    await formRef.value.validate()

    // 转换规格数组为对象
    const specs = {}
    specsArray.value.forEach(spec => {
      if (spec.key && spec.value) {
        specs[spec.key] = spec.value
      }
    })

    if (Object.keys(specs).length === 0) {
      ElMessage.warning('请至少添加一个产品规格')
      return
    }

    // 构建溯源信息
    const origin = {}
    if (originInfo.location) origin.location = originInfo.location
    if (originInfo.method) origin.method = originInfo.method
    if (originInfo.certification) origin.certification = originInfo.certification

    // 准备提交数据，清理空值
    const submitData = {
      name: formData.name,
      sku_code: formData.sku_code,
      category: formData.category,
      specs: specs,
      price: formData.price,
      stock: formData.stock,
      stock_alert_threshold: formData.stock_alert_threshold
    }

    // 添加可选字段（只有非空时才添加）
    if (formData.description) submitData.description = formData.description
    if (formData.original_price) submitData.original_price = formData.original_price
    if (formData.target_scene) submitData.target_scene = formData.target_scene
    if (formData.packaging_type) submitData.packaging_type = formData.packaging_type
    if (formData.video_url) submitData.video_url = formData.video_url
    
    // 数组字段：只有非空时才添加
    if (formData.selling_points && formData.selling_points.length > 0) {
      submitData.selling_points = formData.selling_points
    }
    if (formData.images && formData.images.length > 0) {
      submitData.images = formData.images
    }
    
    // 溯源信息：只有非空时才添加
    if (Object.keys(origin).length > 0) {
      submitData.origin_info = origin
    }

    console.log('提交数据:', submitData)

    submitting.value = true

    if (isEdit.value) {
      await updateProduct(route.params.id, submitData)
      ElMessage.success('产品更新成功')
    } else {
      await createProduct(submitData)
      ElMessage.success('产品创建成功')
    }

    handleBack()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to submit:', error)
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    }
  } finally {
    submitting.value = false
  }
}

// 重置表单
function handleReset() {
  formRef.value?.resetFields()
  specsArray.value = [{ key: '', value: '' }]
  Object.assign(originInfo, {
    location: '',
    method: '',
    certification: ''
  })
}

// 返回列表
function handleBack() {
  router.push('/product/list')
}

// 初始化
onMounted(() => {
  if (isEdit.value) {
    loadProduct()
  }
})
</script>

<style lang="scss" scoped>
.product-edit {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .product-form {
    max-width: 800px;

    .form-section {
      margin-bottom: 32px;
      padding: 24px;
      background: #f9fafb;
      border-radius: 8px;

      .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid #409eff;
      }
    }

    .unit {
      margin-left: 8px;
      color: #909399;
    }

    .specs-input {
      width: 100%;

      .spec-item {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;

        .separator {
          color: #909399;
          font-weight: 600;
        }
      }
    }

    .selling-points {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;

      .point-tag {
        margin: 0;
      }
    }

    .image-upload {
      width: 100%;

      .image-list {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 12px;

        .image-item {
          position: relative;
          width: 120px;
          height: 120px;
          border: 1px solid #dcdfe6;
          border-radius: 8px;
          overflow: hidden;

          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }

          .image-actions {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s;
          }

          &:hover .image-actions {
            opacity: 1;
          }
        }

        .upload-btn {
          width: 120px;
          height: 120px;

          :deep(.el-upload) {
            width: 100%;
            height: 100%;
          }

          .upload-content {
            width: 120px;
            height: 120px;
            border: 2px dashed #dcdfe6;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s;
            color: #909399;

            &:hover {
              border-color: #409eff;
              color: #409eff;
            }

            .el-icon {
              font-size: 28px;
              margin-bottom: 8px;
            }

            span {
              font-size: 14px;
            }
          }
        }
      }

      .tip {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}
</style>
