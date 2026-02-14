<template>
  <div class="account-settings">
    <el-descriptions title="账户信息" :column="2" border>
      <el-descriptions-item label="账户ID">
        {{ accountInfo.id }}
      </el-descriptions-item>
      <el-descriptions-item label="注册时间">
        {{ formatDate(accountInfo.created_at) }}
      </el-descriptions-item>
      <el-descriptions-item label="账户等级">
        <el-tag :type="getTierType(accountInfo.tier)">
          {{ getTierText(accountInfo.tier) }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="认证状态">
        <el-tag :type="accountInfo.is_verified ? 'success' : 'warning'">
          {{ accountInfo.is_verified ? '已认证' : '未认证' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="订阅开始">
        {{ formatDate(accountInfo.subscription_start) || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="订阅结束">
        {{ formatDate(accountInfo.subscription_end) || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="服务数量">
        {{ accountInfo.services_count || 0 }}
      </el-descriptions-item>
      <el-descriptions-item label="今日API调用">
        {{ accountInfo.api_calls_today || 0 }}
      </el-descriptions-item>
    </el-descriptions>

    <el-divider />

    <div class="commission-settings">
      <h3>佣金设置</h3>
      <el-form :model="commissionForm" label-width="120px" class="settings-form">
        <el-form-item label="启用佣金">
          <el-switch v-model="commissionForm.enable_commission" />
          <span class="form-tip">开启后，平台将从订单中收取佣金</span>
        </el-form-item>

        <el-form-item label="佣金比例" v-if="commissionForm.enable_commission">
          <el-input-number
            v-model="commissionForm.commission_rate"
            :min="0"
            :max="30"
            :step="1"
          />
          <span class="form-tip">%（建议范围：3%-10%）</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSaveCommission" :loading="loading">
            保存设置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-divider />

    <div class="upgrade-section">
      <h3>升级套餐</h3>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8" v-for="tier in tiers" :key="tier.value">
          <el-card 
            class="tier-card" 
            :class="{ active: accountInfo.tier === tier.value }"
            shadow="hover"
          >
            <div class="tier-header">
              <h4>{{ tier.name }}</h4>
              <div class="tier-price">
                <span class="price">¥{{ tier.price }}</span>
                <span class="unit">/月</span>
              </div>
            </div>
            <ul class="tier-features">
              <li v-for="feature in tier.features" :key="feature">
                <el-icon color="#67c23a"><Check /></el-icon>
                {{ feature }}
              </li>
            </ul>
            <el-button 
              type="primary" 
              :disabled="accountInfo.tier === tier.value"
              @click="handleUpgrade(tier.value)"
              block
            >
              {{ accountInfo.tier === tier.value ? '当前套餐' : '升级' }}
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import dayjs from 'dayjs'

const userStore = useUserStore()
const loading = ref(false)

const accountInfo = reactive({
  id: '',
  created_at: '',
  tier: 'FREE',
  is_verified: false,
  subscription_start: null,
  subscription_end: null,
  services_count: 0,
  api_calls_today: 0
})

const commissionForm = reactive({
  enable_commission: false,
  commission_rate: 5
})

const tiers = [
  {
    value: 'FREE',
    name: '免费版',
    price: 0,
    features: [
      '基础产品管理',
      '订单管理',
      '客户管理',
      '每月3次AI服务生成'
    ]
  },
  {
    value: 'BASIC',
    name: '基础版',
    price: 99,
    features: [
      '免费版所有功能',
      '每月20次AI服务生成',
      '数据统计分析',
      '溯源管理',
      '优先客服支持'
    ]
  },
  {
    value: 'PROFESSIONAL',
    name: '专业版',
    price: 299,
    features: [
      '基础版所有功能',
      '无限次AI服务生成',
      '高级数据分析',
      '自定义品牌',
      '专属客服',
      'API接口'
    ]
  }
]

// 加载账户信息
function loadAccountInfo() {
  const userInfo = userStore.userInfo
  Object.assign(accountInfo, {
    id: userInfo.id || '',
    created_at: userInfo.created_at || '',
    tier: userInfo.tier || 'FREE',
    is_verified: userInfo.is_verified || false,
    subscription_start: userInfo.subscription_start,
    subscription_end: userInfo.subscription_end,
    services_count: userInfo.services_count || 0,
    api_calls_today: userInfo.api_calls_today || 0
  })

  commissionForm.enable_commission = userInfo.enable_commission || false
  commissionForm.commission_rate = userInfo.commission_rate || 5
}

// 保存佣金设置
async function handleSaveCommission() {
  loading.value = true
  try {
    await userStore.updateUserInfo(commissionForm)
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('Failed to save:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

// 升级套餐
function handleUpgrade(tier) {
  ElMessage.info(`升级到${getTierText(tier)}功能开发中...`)
}

// 格式化日期
function formatDate(date) {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : ''
}

// 获取等级类型
function getTierType(tier) {
  const types = {
    FREE: 'info',
    BASIC: 'warning',
    PROFESSIONAL: 'success'
  }
  return types[tier] || 'info'
}

// 获取等级文本
function getTierText(tier) {
  const texts = {
    FREE: '免费版',
    BASIC: '基础版',
    PROFESSIONAL: '专业版'
  }
  return texts[tier] || tier
}

onMounted(() => {
  loadAccountInfo()
})
</script>

<style lang="scss" scoped>
.account-settings {
  max-width: 900px;

  .commission-settings,
  .upgrade-section {
    margin-top: 30px;

    h3 {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 20px;
      color: #303133;
    }

    .settings-form {
      max-width: 600px;

      .form-tip {
        margin-left: 10px;
        font-size: 13px;
        color: #909399;
      }
    }
  }

  .tier-card {
    margin-bottom: 20px;
    transition: all 0.3s;

    &.active {
      border-color: #409eff;
      box-shadow: 0 2px 12px rgba(64, 158, 255, 0.3);
    }

    .tier-header {
      text-align: center;
      padding-bottom: 20px;
      border-bottom: 1px solid #ebeef5;

      h4 {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 10px;
        color: #303133;
      }

      .tier-price {
        .price {
          font-size: 32px;
          font-weight: 700;
          color: #409eff;
        }

        .unit {
          font-size: 14px;
          color: #909399;
        }
      }
    }

    .tier-features {
      list-style: none;
      padding: 20px 0;
      margin: 0;

      li {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        font-size: 14px;
        color: #606266;

        .el-icon {
          font-size: 16px;
        }
      }
    }
  }
}
</style>

