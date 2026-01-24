<template>
  <div class="product-edit">
    <el-card>
      <template #header>{{ $route.params.id ? '编辑产品' : '添加产品' }}</template>
      <el-empty description="产品编辑功能开发中..." />
    </el-card>
  </div>
</template>
<script setup></script>
