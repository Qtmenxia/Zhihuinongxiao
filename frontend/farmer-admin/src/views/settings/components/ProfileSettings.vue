<template>
  <div class="profile-settings">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      class="settings-form"
    >
      <el-form-item label="头像">
        <div class="avatar-upload">
          <el-avatar :size="100" :src="formData.avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <el-upload
            class="upload-btn"
            :show-file-list="false"
            :before-upload="handleAvatarUpload"
            accept="image/*"
          >
            <el-button type="primary" size="small">
              <el-icon><Upload /></el-icon>更换头像
            </el-button>
          </el-upload>
        </div>
      </el-form-item>

      <el-form-item label="姓名" prop="name">
        <el-input v-model="formData.name" placeholder="请输入姓名" />
      </el-form-item>

      <el-form-item label="手机号" prop="phone">
        <el-input v-model="formData.phone" disabled />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input v-model="formData.email" placeholder="请输入邮箱" />
      </el-form-item>

      <el-form-item label="省份" prop="province">
        <el-input v-model="formData.province" placeholder="请输入省份" />
      </el-form-item>

      <el-form-item label="城市" prop="city">
        <el-input v-model="formData.city" placeholder="请输入城市" />
      </el-form-item>

      <el-form-item label="区县" prop="county">
        <el-input v-model="formData.county" placeholder="请输入区县" />
      </el-form-item>

      <el-form-item label="村庄" prop="village">
        <el-input v-model="formData.village" placeholder="请输入村庄" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleSave" :loading="loading">
          保存修改
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'

const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const formData = reactive({
  avatar: '',
  name: '',
  phone: '',
  email: '',
  province: '',
  city: '',
  county: '',
  village: ''
})

const formRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 加载用户信息
function loadUserInfo() {
  const userInfo = userStore.userInfo
  Object.assign(formData, {
    avatar: userInfo.avatar || '',
    name: userInfo.name || '',
    phone: userInfo.phone || '',
    email: userInfo.email || '',
    province: userInfo.province || '',
    city: userInfo.city || '',
    county: userInfo.county || '',
    village: userInfo.village || ''
  })
}

// 上传头像
async function handleAvatarUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }

  // 这里应该调用上传接口
  ElMessage.success('头像上传成功')
  return false
}

// 保存修改
async function handleSave() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      // 调用更新接口
      await userStore.updateUserInfo(formData)
      ElMessage.success('保存成功')
    } catch (error) {
      console.error('Failed to save:', error)
      ElMessage.error('保存失败')
    } finally {
      loading.value = false
    }
  })
}

// 重置
function handleReset() {
  loadUserInfo()
  ElMessage.info('已重置')
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style lang="scss" scoped>
.profile-settings {
  max-width: 600px;

  .settings-form {
    .avatar-upload {
      display: flex;
      align-items: center;
      gap: 20px;

      .upload-btn {
        :deep(.el-upload) {
          display: block;
        }
      }
    }
  }
}
</style>

