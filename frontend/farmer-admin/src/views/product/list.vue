<template>
  <div class="product-list">
    <!-- 搜索筛选区 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="产品名称">
          <el-input 
            v-model="searchForm.keyword" 
            placeholder="请输入产品名称或SKU"
            clearable
            @clear="handleSearch"
          />
        </el-form-item>
        <el-form-item label="产品分类">
          <el-select 
            v-model="searchForm.category" 
            placeholder="全部分类"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="水果" value="水果" />
            <el-option label="坚果" value="坚果" />
            <el-option label="粮食" value="粮食" />
            <el-option label="干果" value="干果" />
            <el-option label="蜂产品" value="蜂产品" />
            <el-option label="菌类" value="菌类" />
            <el-option label="禽蛋" value="禽蛋" />
          </el-select>
        </el-form-item>
        <el-form-item label="产品状态">
          <el-select 
            v-model="searchForm.is_active" 
            placeholder="全部状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="全部" value="" />
            <el-option label="在售" :value="true" />
            <el-option label="下架" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 产品列表 -->
    <el-card class="product-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">产品列表</span>
            <el-tag type="info" class="count-tag">共 {{ total }} 个产品</el-tag>
          </div>
          <div class="header-right">
            <el-button type="success" @click="handleExport">
              <el-icon><Download /></el-icon>导出
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>添加产品
            </el-button>
          </div>
        </div>
      </template>

      <!-- 产品卡片网格 -->
      <div v-loading="loading" class="product-grid">
        <div 
          v-for="product in productList" 
          :key="product.id" 
          class="product-item"
          @click="handleView(product)"
        >
          <div class="product-image">
            <img 
              :src="getImageUrl(product.images?.[0])" 
              :alt="product.name"
              @error="handleImageError"
            />
            <div class="product-badges">
              <el-tag v-if="product.is_featured" type="danger" size="small">精选</el-tag>
              <el-tag v-if="!product.is_active" type="info" size="small">已下架</el-tag>
              <el-tag v-if="product.stock <= product.stock_alert_threshold" type="warning" size="small">
                库存预警
              </el-tag>
            </div>
          </div>
          
          <div class="product-info">
            <div class="product-name" :title="product.name">{{ product.name }}</div>
            <div class="product-category">
              <el-tag size="small" effect="plain">{{ product.category }}</el-tag>
              <span class="sku">SKU: {{ product.sku_code }}</span>
            </div>
            
            <div class="product-price">
              <span class="current-price">¥{{ product.price }}</span>
              <span v-if="product.original_price" class="original-price">
                ¥{{ product.original_price }}
              </span>
            </div>
            
            <div class="product-stock">
              <span class="stock-label">库存：</span>
              <span 
                class="stock-value" 
                :class="{ 'low-stock': product.stock <= product.stock_alert_threshold }"
              >
                {{ product.stock }}
              </span>
            </div>
            
            <div class="product-specs" v-if="product.specs">
              <el-tag 
                v-for="(value, key) in product.specs" 
                :key="key" 
                size="small" 
                effect="plain"
                class="spec-tag"
              >
                {{ key }}: {{ value }}
              </el-tag>
            </div>
          </div>
          
          <div class="product-actions" @click.stop>
            <el-button 
              type="primary" 
              link 
              size="small"
              @click="handleEdit(product)"
            >
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button 
              :type="product.is_active ? 'warning' : 'success'" 
              link 
              size="small"
              @click="handleToggleStatus(product)"
            >
              <el-icon><Switch /></el-icon>
              {{ product.is_active ? '下架' : '上架' }}
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small"
              @click="handleDelete(product)"
            >
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="!loading && productList.length === 0" 
        description="暂无产品数据"
      >
        <el-button type="primary" @click="handleAdd">添加第一个产品</el-button>
      </el-empty>

      <!-- 分页 -->
      <div v-if="total > 0" class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[12, 24, 48, 96]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProductList, deleteProduct, updateProduct } from '@/api/product'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: '',
  is_active: ''
})

// 分页
const pagination = reactive({
  page: 1,
  page_size: 12
})

// 数据
const loading = ref(false)
const productList = ref([])
const total = ref(0)

// 加载产品列表
async function loadProducts() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    // 清理空参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const res = await getProductList(params)
    productList.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('Failed to load products:', error)
    ElMessage.error('加载产品列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
function handleSearch() {
  pagination.page = 1
  loadProducts()
}

// 重置
function handleReset() {
  searchForm.keyword = ''
  searchForm.category = ''
  searchForm.is_active = ''
  handleSearch()
}

// 分页变化
function handlePageChange(page) {
  pagination.page = page
  loadProducts()
}

function handleSizeChange(size) {
  pagination.page_size = size
  pagination.page = 1
  loadProducts()
}

// 添加产品
function handleAdd() {
  router.push('/product/add')
}

// 查看详情
function handleView(product) {
  router.push(`/product/detail/${product.id}`)
}

// 编辑产品
function handleEdit(product) {
  router.push(`/product/edit/${product.id}`)
}

// 切换状态
async function handleToggleStatus(product) {
  try {
    await ElMessageBox.confirm(
      `确定要${product.is_active ? '下架' : '上架'}该产品吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await updateProduct(product.id, {
      is_active: !product.is_active
    })
    
    ElMessage.success(`${product.is_active ? '下架' : '上架'}成功`)
    loadProducts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to toggle status:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 删除产品
async function handleDelete(product) {
  try {
    await ElMessageBox.confirm(
      `确定要删除产品"${product.name}"吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    
    await deleteProduct(product.id)
    ElMessage.success('删除成功')
    
    // 如果当前页没有数据了，返回上一页
    if (productList.value.length === 1 && pagination.page > 1) {
      pagination.page--
    }
    
    loadProducts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete product:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 导出
async function handleExport() {
  try {
    loading.value = true
    
    // 准备导出参数（使用当前筛选条件）
    const params = {}
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.category) params.category = searchForm.category
    if (searchForm.is_active !== '') params.is_active = searchForm.is_active
    
    ElMessage.info('正在生成PDF文件，请稍候...')
    
    const blob = await exportProducts(params)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `products_${new Date().getTime()}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败')
  } finally {
    loading.value = false
  }
}

// 获取图片URL
function getImageUrl(url) {
  if (!url) return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="300"%3E%3Crect fill="%23f0f0f0" width="300" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="20"%3E暂无图片%3C/text%3E%3C/svg%3E'
  // 如果是相对路径，添加API基础URL
  if (url.startsWith('/uploads/')) {
    return `http://localhost:8000${url}`
  }
  return url
}

// 图片加载失败
function handleImageError(e) {
  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="300" height="300"%3E%3Crect fill="%23f0f0f0" width="300" height="300"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="20"%3E图片加载失败%3C/text%3E%3C/svg%3E'
}

// 初始化
onMounted(() => {
  loadProducts()
})
</script>

<style lang="scss" scoped>
.product-list {
  .search-card {
    margin-bottom: 20px;
    
    .search-form {
      margin-bottom: 0;
    }
  }
  
  .product-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .title {
          font-size: 16px;
          font-weight: 600;
        }
        
        .count-tag {
          font-size: 12px;
        }
      }
      
      .header-right {
        display: flex;
        gap: 8px;
      }
    }
    
    .product-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
      
      .product-item {
        border: 1px solid #e4e7ed;
        border-radius: 8px;
        overflow: hidden;
        transition: all 0.3s;
        cursor: pointer;
        background: #fff;
        
        &:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          transform: translateY(-4px);
        }
        
        .product-image {
          position: relative;
          width: 100%;
          height: 200px;
          overflow: hidden;
          background: #f5f7fa;
          
          img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s;
          }
          
          &:hover img {
            transform: scale(1.05);
          }
          
          .product-badges {
            position: absolute;
            top: 8px;
            right: 8px;
            display: flex;
            flex-direction: column;
            gap: 4px;
          }
        }
        
        .product-info {
          padding: 16px;
          
          .product-name {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
            margin-bottom: 8px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }
          
          .product-category {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            
            .sku {
              font-size: 12px;
              color: #909399;
            }
          }
          
          .product-price {
            margin-bottom: 8px;
            
            .current-price {
              font-size: 24px;
              font-weight: 700;
              color: #f56c6c;
              margin-right: 8px;
            }
            
            .original-price {
              font-size: 14px;
              color: #909399;
              text-decoration: line-through;
            }
          }
          
          .product-stock {
            margin-bottom: 12px;
            font-size: 14px;
            
            .stock-label {
              color: #606266;
            }
            
            .stock-value {
              color: #67c23a;
              font-weight: 600;
              
              &.low-stock {
                color: #e6a23c;
              }
            }
          }
          
          .product-specs {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            
            .spec-tag {
              font-size: 11px;
            }
          }
        }
        
        .product-actions {
          padding: 12px 16px;
          border-top: 1px solid #e4e7ed;
          display: flex;
          justify-content: space-around;
          background: #fafafa;
        }
      }
    }
    
    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}
</style>
