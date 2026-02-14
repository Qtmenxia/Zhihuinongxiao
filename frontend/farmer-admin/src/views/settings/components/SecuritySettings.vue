<template>
  <div class="security-settings">
    <!-- 修改密码 -->
    <div class="setting-section">
      <h3>修改密码</h3>
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="120px"
        class="settings-form"
      >
        <el-form-item label="当前密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码（至少6位）"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleChangePassword" :loading="passwordLoading">
            修改密码
          </el-button>
          <el-button @click="handleResetPassword">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-divider />

    <!-- 绑定手机 -->
    <div class="setting-section">
      <h3>手机绑定</h3>
      <div class="bind-info">
        <div class="info-item">
          <span class="label">当前手机：</span>
          <span class="value">{{ maskPhone(userInfo.phone) }}</span>
          <el-tag type="success" size="small">已绑定</el-tag>
        </div>
        <el-button type="primary" plain @click="showChangePhone = true">
          更换手机号
        </el-button>
      </div>
    </div>

    <el-divider />

    <!-- 绑定邮箱 -->
    <div class="setting-section">
      <h3>邮箱绑定</h3>
      <div class="bind-info">
        <div class="info-item">
          <span class="label">当前邮箱：</span>
          <span class="value">{{ userInfo.email || '未绑定' }}</span>
          <el-tag v-if="userInfo.email" type="success" size="small">已绑定</el-tag>
          <el-tag v-else type="info" size="small">未绑定</el-tag>
        </div>
        <el-button type="primary" plain @click="showChangeEmail = true">
          {{ userInfo.email ? '更换邮箱' : '绑定邮箱' }}
        </el-button>
      </div>
    </div>

    <el-divider />

    <!-- 登录日志 -->
    <div class="setting-section">
      <h3>登录日志</h3>
      <el-table :data="loginLogs" stripe>
        <el-table-column prop="login_time" label="登录时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.login_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP地址" width="150" />
        <el-table-column prop="location" label="登录地点" />
        <el-table-column prop="device" label="设备" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 更换手机号对话框 -->
    <el-dialog v-model="showChangePhone" title="更换手机号" width="500px">
      <el-form :model="phoneForm" label-width="100px">
        <el-form-item label="新手机号">
          <el-input v-model="phoneForm.phone" placeholder="请输入新手机号" />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="code-input">
            <el-input v-model="phoneForm.code" placeholder="请输入验证码" />
            <el-button @click="handleSendCode" :disabled="codeCountdown > 0">
              {{ codeCountdown > 0 ? `${codeCountdown}秒后重试` : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChangePhone = false">取消</el-button>
        <el-button type="primary" @click="handleChangePhone">确定</el-button>
      </template>
    </el-dialog>

    <!-- 更换邮箱对话框 -->
    <el-dialog v-model="showChangeEmail" title="绑定/更换邮箱" width="500px">
      <el-form :model="emailForm" label-width="100px">
        <el-form-item label="邮箱地址">
          <el-input v-model="emailForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="code-input">
            <el-input v-model="emailForm.code" placeholder="请输入验证码" />
            <el-button @click="handleSendEmailCode" :disabled="emailCodeCountdown > 0">
              {{ emailCodeCountdown > 0 ? `${emailCodeCountdown}秒后重试` : '发送验证码' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showChangeEmail = false">取消</el-button>
        <el-button type="primary" @click="handleChangeEmail">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import dayjs from 'dayjs'

const userStore = useUserStore()
const passwordFormRef = ref(null)
const passwordLoading = ref(false)
const showChangePhone = ref(false)
const showChangeEmail = ref(false)
const codeCountdown = ref(0)
const emailCodeCountdown = ref(0)

const userInfo = reactive({
  phone: '',
  email: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const phoneForm = reactive({
  phone: '',
  code: ''
})

const emailForm = reactive({
  email: '',
  code: ''
})

const loginLogs = ref([
  {
    login_time: new Date(),
    ip: '192.168.1.100',
    location: '山西省临汾市',
    device: 'Chrome 120 / Windows 10',
    status: 'success'
  }
])

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 加载用户信息
function loadUserInfo() {
  const info = userStore.userInfo
  userInfo.phone = info.phone || ''
  userInfo.email = info.email || ''
}

// 修改密码
async function handleChangePassword() {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return

    passwordLoading.value = true
    try {
      // 调用修改密码接口
      ElMessage.success('密码修改成功，请重新登录')
      // 清空表单
      handleResetPassword()
    } catch (error) {
      console.error('Failed to change password:', error)
      ElMessage.error('密码修改失败')
    } finally {
      passwordLoading.value = false
    }
  })
}

// 重置密码表单
function handleResetPassword() {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordFormRef.value?.clearValidate()
}

// 发送验证码
function handleSendCode() {
  if (!phoneForm.phone) {
    ElMessage.warning('请输入手机号')
    return
  }

  ElMessage.success('验证码已发送')
  codeCountdown.value = 60
  const timer = setInterval(() => {
    codeCountdown.value--
    if (codeCountdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 发送邮箱验证码
function handleSendEmailCode() {
  if (!emailForm.email) {
    ElMessage.warning('请输入邮箱地址')
    return
  }

  ElMessage.success('验证码已发送')
  emailCodeCountdown.value = 60
  const timer = setInterval(() => {
    emailCodeCountdown.value--
    if (emailCodeCountdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 更换手机号
function handleChangePhone() {
  if (!phoneForm.phone || !phoneForm.code) {
    ElMessage.warning('请填写完整信息')
    return
  }

  ElMessage.success('手机号更换成功')
  showChangePhone.value = false
  phoneForm.phone = ''
  phoneForm.code = ''
}

// 更换邮箱
function handleChangeEmail() {
  if (!emailForm.email || !emailForm.code) {
    ElMessage.warning('请填写完整信息')
    return
  }

  ElMessage.success('邮箱绑定成功')
  showChangeEmail.value = false
  emailForm.email = ''
  emailForm.code = ''
}

// 格式化日期
function formatDate(date) {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 手机号脱敏
function maskPhone(phone) {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style lang="scss" scoped>
.security-settings {
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
      max-width: 500px;
    }

    .bind-info {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px;
      background: #f5f7fa;
      border-radius: 4px;

      .info-item {
        display: flex;
        align-items: center;
        gap: 10px;

        .label {
          color: #606266;
          font-size: 14px;
        }

        .value {
          color: #303133;
          font-size: 14px;
          font-weight: 500;
        }
      }
    }
  }

  .code-input {
    display: flex;
    gap: 10px;

    .el-input {
      flex: 1;
    }
  }
}
</style>

