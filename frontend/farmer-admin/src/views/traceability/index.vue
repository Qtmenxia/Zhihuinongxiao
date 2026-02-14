<template>
  <div class="traceability-page">
    <!-- 功能导航卡片 -->
    <el-row :gutter="20" class="feature-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="feature-card" shadow="hover" @click="activeTab = 'guide'">
          <div class="card-content">
            <el-icon class="card-icon" color="#409eff"><InfoFilled /></el-icon>
            <h3>什么是溯源</h3>
            <p>了解溯源系统功能</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="feature-card" shadow="hover" @click="activeTab = 'records'">
          <div class="card-content">
            <el-icon class="card-icon" color="#67c23a"><List /></el-icon>
            <h3>溯源记录</h3>
            <p>管理产品溯源信息</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="feature-card" shadow="hover" @click="activeTab = 'generate'">
          <div class="card-content">
            <el-icon class="card-icon" color="#e6a23c"><Stamp /></el-icon>
            <h3>生成溯源码</h3>
            <p>为产品生成二维码</p>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="feature-card" shadow="hover" @click="activeTab = 'logistics'">
          <div class="card-content">
            <el-icon class="card-icon" color="#f56c6c"><Van /></el-icon>
            <h3>物流信息</h3>
            <p>记录物流节点</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主内容区 -->
    <el-card class="main-card">
      <el-tabs v-model="activeTab">
        <!-- 溯源指南 -->
        <el-tab-pane label="溯源系统指南" name="guide">
          <TraceabilityGuide />
        </el-tab-pane>

        <!-- 溯源记录管理 -->
        <el-tab-pane label="溯源记录" name="records">
          <TraceabilityRecords />
        </el-tab-pane>

        <!-- 生成溯源码 -->
        <el-tab-pane label="生成溯源码" name="generate">
          <GenerateTraceCode />
        </el-tab-pane>

        <!-- 物流信息 -->
        <el-tab-pane label="物流信息" name="logistics">
          <LogisticsInfo />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TraceabilityGuide from './components/TraceabilityGuide.vue'
import TraceabilityRecords from './components/TraceabilityRecords.vue'
import GenerateTraceCode from './components/GenerateTraceCode.vue'
import LogisticsInfo from './components/LogisticsInfo.vue'

const activeTab = ref('guide')
</script>

<style lang="scss" scoped>
.traceability-page {
  padding: 20px;

  .feature-cards {
    margin-bottom: 20px;

    .feature-card {
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      }

      .card-content {
        text-align: center;
        padding: 20px 0;

        .card-icon {
          font-size: 48px;
          margin-bottom: 15px;
        }

        h3 {
          font-size: 18px;
          font-weight: 600;
          margin-bottom: 8px;
          color: #303133;
        }

        p {
          font-size: 14px;
          color: #909399;
          margin: 0;
        }
      }
    }
  }

  .main-card {
    :deep(.el-tabs__header) {
      margin-bottom: 20px;
    }
  }
}
</style>
