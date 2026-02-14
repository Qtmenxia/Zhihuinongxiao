<template>
  <div class="notification-settings">
    <div class="setting-section">
      <h3>通知偏好</h3>
      <el-form label-width="150px" class="settings-form">
        <el-form-item label="订单通知">
          <el-switch v-model="settings.order_notification" />
          <span class="form-tip">新订单、订单状态变更时通知</span>
        </el-form-item>

        <el-form-item label="客户消息通知">
          <el-switch v-model="settings.customer_message" />
          <span class="form-tip">客户发送消息时通知</span>
        </el-form-item>

        <el-form-item label="系统通知">
          <el-switch v-model="settings.system_notification" />
          <span class="form-tip">系统更新、维护等重要通知</span>
        </el-form-item>

        <el-form-item label="营销通知">
          <el-switch v-model="settings.marketing_notification" />
          <span class="form-tip">促销活动、优惠信息等</span>
        </el-form-item>
      </el-form>
    </div>

    <el-divider />

    <div class="setting-section">
      <h3>通知方式</h3>
      <el-form label-width="150px" class="settings-form">
        <el-form-item label="站内消息">
          <el-switch v-model="settings.in_app_notification" />
          <span class="form-tip">在系统内接收通知</span>
        </el-form-item>

        <el-form-item label="短信通知">
          <el-switch v-model="settings.sms_notification" />
          <span class="form-tip">通过短信接收重要通知</span>
        </el-form-item>

        <el-form-item label="邮件通知">
          <el-switch v-model="settings.email_notification" />
          <span class="form-tip">通过邮件接收通知</span>
        </el-form-item>

        <el-form-item label="微信通知">
          <el-switch v-model="settings.wechat_notification" />
          <span class="form-tip">通过微信公众号接收通知</span>
        </el-form-item>
      </el-form>
    </div>

    <el-divider />

    <div class="setting-section">
      <h3>免打扰时段</h3>
      <el-form label-width="150px" class="settings-form">
        <el-form-item label="启用免打扰">
          <el-switch v-model="settings.do_not_disturb" />
        </el-form-item>

        <el-form-item label="免打扰时段" v-if="settings.do_not_disturb">
          <el-time-picker
            v-model="settings.dnd_start_time"
            placeholder="开始时间"
            format="HH:mm"
            value-format="HH:mm"
          />
          <span style="margin: 0 10px;">至</span>
          <el-time-picker
            v-model="settings.dnd_end_time"
            placeholder="结束时间"
            format="HH:mm"
            value-format="HH:mm"
          />
        </el-form-item>
      </el-form>
    </div>

    <el-divider />

    <div class="setting-section">
      <h3>通知历史</h3>
      <el-table :data="notifications" stripe>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getNotificationType(row.type)" size="small">
              {{ getNotificationTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_read" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_read ? 'info' : 'success'" size="small">
              {{ row.is_read ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleMarkRead(row)">
              标记已读
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          layout="total, prev, pager, next"
          @current-change="loadNotifications"
        />
      </div>
    </div>

    <div class="save-actions">
      <el-button type="primary" @click="handleSave" :loading="loading">
        保存设置
      </el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)

const settings = reactive({
  order_notification: true,
  customer_message: true,
  system_notification: true,
  marketing_notification: false,
  in_app_notification: true,
  sms_notification: true,
  email_notification: false,
  wechat_notification: false,
  do_not_disturb: false,
  dnd_start_time: '22:00',
  dnd_end_time: '08:00'
})

const notifications = ref([
  {
    id: 1,
    title: '新订单通知',
    content: '您有一笔新订单，订单号：ORD20240214001',
    type: 'order',
    created_at: new Date(),
    is_read: false
  },
  {
    id: 2,
    title: '系统更新通知',
    content: '系统将于今晚22:00进行维护升级，预计持续1小时',
    type: 'system',
    created_at: new Date(Date.now() - 3600000),
    is_read: true
  }
])

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 2
})

// 加载通知历史
function loadNotifications() {
  // 这里应该调用API加载通知
}

// 保存设置
async function handleSave() {
  loading.value = true
  try {
    // 调用保存接口
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('Failed to save:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

// 重置
function handleReset() {
  Object.assign(settings, {
    order_notification: true,
    customer_message: true,
    system_notification: true,
    marketing_notification: false,
    in_app_notification: true,
    sms_notification: true,
    email_notification: false,
    wechat_notification: false,
    do_not_disturb: false,
    dnd_start_time: '22:00',
    dnd_end_time: '08:00'
  })
  ElMessage.info('已重置')
}

// 标记已读
function handleMarkRead(row) {
  row.is_read = true
  ElMessage.success('已标记为已读')
}

// 格式化日期
function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 获取通知类型
function getNotificationType(type) {
  const types = {
    order: 'primary',
    customer: 'success',
    system: 'warning',
    marketing: 'info'
  }
  return types[type] || 'info'
}

// 获取通知类型文本
function getNotificationTypeText(type) {
  const texts = {
    order: '订单',
    customer: '客户',
    system: '系统',
    marketing: '营销'
  }
  return texts[type] || type
}

onMounted(() => {
  loadNotifications()
})
</script>

<style lang="scss" scoped>
.notification-settings {
  max-width: 800px;

  .setting-section {
    margin-bottom: 30px;

    h3 {
      font-size: 18px;
      font-weight: 600;
      margin-bottom: 20px;
      color: #303133;
    }

    .settings-form {
      .form-tip {
        margin-left: 10px;
        font-size: 13px;
        color: #909399;
      }
    }

    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }

  .save-actions {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
  }
}
</style>

