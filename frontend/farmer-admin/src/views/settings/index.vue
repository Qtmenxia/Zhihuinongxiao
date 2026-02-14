<template>
  <div class="settings-container">
    <el-card class="settings-card">
      <el-tabs v-model="activeTab" class="settings-tabs">
        <!-- 个人信息 -->
        <el-tab-pane label="个人信息" name="profile">
          <ProfileSettings />
        </el-tab-pane>
        
        <!-- 账户设置 -->
        <el-tab-pane label="账户设置" name="account">
          <AccountSettings />
        </el-tab-pane>
        
        <!-- 安全设置 -->
        <el-tab-pane label="安全设置" name="security">
          <SecuritySettings />
        </el-tab-pane>
        
        <!-- 通知设置 -->
        <el-tab-pane label="通知设置" name="notification">
          <NotificationSettings />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ProfileSettings from './components/ProfileSettings.vue'
import AccountSettings from './components/AccountSettings.vue'
import SecuritySettings from './components/SecuritySettings.vue'
import NotificationSettings from './components/NotificationSettings.vue'

const activeTab = ref('profile')
</script>

<style lang="scss" scoped>
.settings-container {
  padding: 20px;
  
  .settings-card {
    max-width: 1200px;
    margin: 0 auto;
    
    .settings-tabs {
      :deep(.el-tabs__header) {
        margin-bottom: 30px;
      }
      
      :deep(.el-tabs__item) {
        font-size: 15px;
        padding: 0 30px;
      }
    }
  }
}
</style>
