<template>
  <div class="product-list">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>产品管理</span>
          <el-button type="primary" @click="$router.push('/product/add')">
            <el-icon><Plus /></el-icon>添加产品
          </el-button>
        </div>
      </template>
      <el-empty description="产品管理功能开发中..." />
    </el-card>
  </div>
</template>

<script setup>
</script>
