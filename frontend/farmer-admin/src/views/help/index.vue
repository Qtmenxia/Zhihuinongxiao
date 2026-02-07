<template>
  <div class="help-container">
    <el-row :gutter="20">
      <!-- 左侧目录 -->
      <el-col :span="6">
        <el-card shadow="never" class="menu-card">
          <template #header>
            <span>帮助目录</span>
          </template>
          <el-menu
            :default-active="activeMenu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="quickstart">
              <el-icon><Promotion /></el-icon>
              <span>快速开始</span>
            </el-menu-item>
            <el-menu-item index="service">
              <el-icon><MagicStick /></el-icon>
              <span>AI服务使用</span>
            </el-menu-item>
            <el-menu-item index="product">
              <el-icon><Goods /></el-icon>
              <span>产品管理</span>
            </el-menu-item>
            <el-menu-item index="order">
              <el-icon><Document /></el-icon>
              <span>订单处理</span>
            </el-menu-item>
            <el-menu-item index="traceability">
              <el-icon><Connection /></el-icon>
              <span>溯源系统</span>
            </el-menu-item>
            <el-menu-item index="faq">
              <el-icon><QuestionFilled /></el-icon>
              <span>常见问题</span>
            </el-menu-item>
            <el-menu-item index="contact">
              <el-icon><Phone /></el-icon>
              <span>联系我们</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <!-- 右侧内容 -->
      <el-col :span="18">
        <el-card shadow="never" class="content-card">
          <!-- 快速开始 -->
          <div v-if="activeMenu === 'quickstart'" class="help-content">
            <h2>🚀 快速开始</h2>
            <p>欢迎使用智农链销平台！以下是快速上手指南：</p>
            
            <h3>第一步：完善信息</h3>
            <p>进入"系统设置"，完善您的农户信息、认证资料和联系方式。</p>
            
            <h3>第二步：添加产品</h3>
            <p>进入"产品管理" → "添加产品"，填写您的农产品信息，包括名称、价格、库存等。</p>
            
            <h3>第三步：生成AI服务</h3>
            <p>进入"AI服务" → "生成服务"，选择产品后系统将自动生成智能客服、溯源查询等API服务。</p>
            
            <h3>第四步：部署上线</h3>
            <p>在服务列表中点击"部署"，即可将服务发布到云端，供客户访问使用。</p>

            <el-alert title="提示" type="info" show-icon :closable="false" style="margin-top: 20px">
              首次使用建议先阅读各功能模块的帮助文档，如有问题可联系客服。
            </el-alert>
          </div>

          <!-- AI服务使用 -->
          <div v-else-if="activeMenu === 'service'" class="help-content">
            <h2>🤖 AI服务使用指南</h2>
            
            <h3>什么是AI服务？</h3>
            <p>AI服务是基于您的产品信息自动生成的智能API接口，包括：</p>
            <ul>
              <li><strong>智能客服</strong>：自动回答客户关于产品的问题</li>
              <li><strong>产品查询</strong>：提供产品信息、价格、库存查询</li>
              <li><strong>订单处理</strong>：支持订单创建、查询、状态更新</li>
              <li><strong>溯源查询</strong>：提供产品溯源信息查询</li>
            </ul>

            <h3>如何生成服务？</h3>
            <el-steps :active="3" finish-status="success" simple style="margin: 20px 0">
              <el-step title="选择产品" />
              <el-step title="配置选项" />
              <el-step title="生成服务" />
              <el-step title="部署上线" />
            </el-steps>

            <h3>服务定价</h3>
            <el-table :data="pricingData" stripe style="margin-top: 10px">
              <el-table-column prop="tier" label="套餐" width="120" />
              <el-table-column prop="services" label="服务数量" />
              <el-table-column prop="calls" label="日调用量" />
              <el-table-column prop="price" label="价格" />
            </el-table>
          </div>

          <!-- 产品管理 -->
          <div v-else-if="activeMenu === 'product'" class="help-content">
            <h2>📦 产品管理指南</h2>
            
            <h3>添加产品</h3>
            <p>点击"产品管理" → "添加产品"，填写以下信息：</p>
            <ul>
              <li>产品名称、类别、描述</li>
              <li>价格、库存、单位</li>
              <li>产品图片（建议上传高清图片）</li>
              <li>产地、认证信息等</li>
            </ul>

            <h3>库存管理</h3>
            <p>系统支持实时库存管理，当库存不足时会自动提醒。您可以在产品详情页调整库存数量。</p>

            <h3>产品上下架</h3>
            <p>在产品列表中可以快速切换产品的上架/下架状态，下架后产品将不会在前台展示。</p>
          </div>

          <!-- 订单处理 -->
          <div v-else-if="activeMenu === 'order'" class="help-content">
            <h2>📋 订单处理指南</h2>
            
            <h3>订单状态说明</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="待付款">客户已下单，等待付款</el-descriptions-item>
              <el-descriptions-item label="待发货">客户已付款，等待发货</el-descriptions-item>
              <el-descriptions-item label="已发货">订单已发出，等待签收</el-descriptions-item>
              <el-descriptions-item label="已完成">订单已完成</el-descriptions-item>
              <el-descriptions-item label="已取消">订单已取消</el-descriptions-item>
            </el-descriptions>

            <h3>发货流程</h3>
            <p>1. 在订单列表找到"待发货"订单</p>
            <p>2. 点击"发货"按钮</p>
            <p>3. 填写物流公司和运单号</p>
            <p>4. 确认发货</p>
          </div>

          <!-- 溯源系统 -->
          <div v-else-if="activeMenu === 'traceability'" class="help-content">
            <h2>🔗 溯源系统指南</h2>
            
            <h3>什么是溯源？</h3>
            <p>溯源系统可以记录农产品从生产到销售的全过程，让消费者扫码即可查看产品的完整信息。</p>

            <h3>溯源记录内容</h3>
            <ul>
              <li>产品基本信息（名称、产地、规格）</li>
              <li>生产过程（播种、施肥、采收等）</li>
              <li>质检报告</li>
              <li>物流信息</li>
            </ul>

            <h3>生成溯源码</h3>
            <p>系统会自动为每批次产品生成唯一的溯源二维码，可打印贴在产品包装上。</p>
          </div>

          <!-- 常见问题 -->
          <div v-else-if="activeMenu === 'faq'" class="help-content">
            <h2>❓ 常见问题</h2>
            
            <el-collapse v-model="activeFaq">
              <el-collapse-item title="如何修改登录密码？" name="1">
                进入"系统设置" → "账号安全" → "修改密码"，输入旧密码和新密码即可。
              </el-collapse-item>
              <el-collapse-item title="AI服务生成失败怎么办？" name="2">
                请检查产品信息是否完整，如问题持续，请联系客服处理。
              </el-collapse-item>
              <el-collapse-item title="如何提升服务调用量限制？" name="3">
                您可以升级到更高级的套餐，或联系客服申请临时提升。
              </el-collapse-item>
              <el-collapse-item title="订单退款如何处理？" name="4">
                在订单详情页点击"退款"，填写退款原因后提交，系统会自动处理退款。
              </el-collapse-item>
              <el-collapse-item title="如何获取农产品认证？" name="5">
                请联系当地农业部门或认证机构，完成认证后可在平台上传认证证书。
              </el-collapse-item>
            </el-collapse>
          </div>

          <!-- 联系我们 -->
          <div v-else-if="activeMenu === 'contact'" class="help-content">
            <h2>📞 联系我们</h2>
            
            <el-descriptions :column="1" border>
              <el-descriptions-item label="客服电话">400-888-8888</el-descriptions-item>
              <el-descriptions-item label="客服邮箱">support@zhinonglianxiao.com</el-descriptions-item>
              <el-descriptions-item label="工作时间">周一至周五 9:00-18:00</el-descriptions-item>
              <el-descriptions-item label="公司地址">山西省临汾市蒲县科技园区</el-descriptions-item>
            </el-descriptions>

            <el-divider />

            <h3>在线反馈</h3>
            <el-form :model="feedbackForm" label-width="80px" style="max-width: 500px">
              <el-form-item label="问题类型">
                <el-select v-model="feedbackForm.type" placeholder="请选择">
                  <el-option label="功能建议" value="suggestion" />
                  <el-option label="Bug反馈" value="bug" />
                  <el-option label="使用咨询" value="consult" />
                  <el-option label="其他" value="other" />
                </el-select>
              </el-form-item>
              <el-form-item label="问题描述">
                <el-input v-model="feedbackForm.content" type="textarea" :rows="4" placeholder="请详细描述您的问题..." />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="submitFeedback">提交反馈</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Promotion, MagicStick, Goods, Document, Connection, QuestionFilled, Phone } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeMenu = ref('quickstart')
const activeFaq = ref(['1'])

// 定价数据
const pricingData = [
  { tier: '免费版', services: '1个', calls: '100次/天', price: '免费' },
  { tier: '基础版', services: '5个', calls: '1000次/天', price: '¥99/月' },
  { tier: '专业版', services: '20个', calls: '10000次/天', price: '¥299/月' },
]

// 反馈表单
const feedbackForm = reactive({
  type: '',
  content: ''
})

const handleMenuSelect = (index) => {
  activeMenu.value = index
}

const submitFeedback = () => {
  if (!feedbackForm.type || !feedbackForm.content) {
    ElMessage.warning('请填写完整信息')
    return
  }
  ElMessage.success('感谢您的反馈，我们会尽快处理！')
  feedbackForm.type = ''
  feedbackForm.content = ''
}
</script>

<style scoped>
.help-container {
  padding: 20px;
}

.menu-card {
  position: sticky;
  top: 20px;
}

.content-card {
  min-height: calc(100vh - 140px);
}

.help-content {
  padding: 10px;
}

.help-content h2 {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.help-content h3 {
  margin: 20px 0 10px;
  color: #303133;
}

.help-content p {
  line-height: 1.8;
  color: #606266;
  margin-bottom: 10px;
}

.help-content ul {
  padding-left: 20px;
  line-height: 2;
  color: #606266;
}

.help-content ul li {
  margin-bottom: 5px;
}
</style>
