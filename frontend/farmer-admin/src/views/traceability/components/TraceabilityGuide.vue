<template>
  <div class="traceability-guide">
    <el-alert
      title="溯源系统指南"
      type="info"
      :closable="false"
      show-icon
    >
      <p>溯源系统可以记录农产品从生产到销售的全过程，让消费者扫码即可查看产品的完整信息。</p>
    </el-alert>

    <div class="guide-section">
      <h2><el-icon><QuestionFilled /></el-icon> 什么是溯源？</h2>
      <p class="description">
        溯源系统可以记录农产品从生产到销售的过程，让消费者扫码即可查看产品的完整溯源信息。
      </p>
    </div>

    <div class="guide-section">
      <h2><el-icon><Document /></el-icon> 溯源记录内容</h2>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="content-item">
            <el-icon class="item-icon" color="#409eff"><Goods /></el-icon>
            <h4>产品基本信息</h4>
            <p>名称、产地、规格</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="content-item">
            <el-icon class="item-icon" color="#67c23a"><Calendar /></el-icon>
            <h4>生产过程</h4>
            <p>播种、施肥、采收等</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="content-item">
            <el-icon class="item-icon" color="#e6a23c"><DocumentChecked /></el-icon>
            <h4>质检报告</h4>
            <p>检测结果、认证信息</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="content-item">
            <el-icon class="item-icon" color="#f56c6c"><Van /></el-icon>
            <h4>物流信息</h4>
            <p>发货、运输、签收</p>
          </div>
        </el-col>
      </el-row>
    </div>

    <div class="guide-section">
      <h2><el-icon><Stamp /></el-icon> 生成溯源码</h2>
      <p class="description">
        系统会自动为每批产品生成唯一的溯源二维码，可打印贴在产品包装上。
      </p>
      <div class="qr-example">
        <div class="qr-placeholder">
          <el-icon :size="120" color="#409eff"><Connection /></el-icon>
          <p>溯源二维码示例</p>
        </div>
        <div class="qr-info">
          <h4>二维码包含信息：</h4>
          <ul>
            <li>产品批次号</li>
            <li>生产日期</li>
            <li>产地信息</li>
            <li>农户信息</li>
            <li>质检报告</li>
            <li>查询链接</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="guide-section">
      <h2><el-icon><Guide /></el-icon> 使用流程</h2>
      <el-steps :active="4" align-center>
        <el-step title="创建溯源记录" description="填写产品基本信息" />
        <el-step title="记录生产过程" description="添加种植、采收等信息" />
        <el-step title="上传质检报告" description="添加检测结果和认证" />
        <el-step title="生成溯源码" description="生成并打印二维码" />
        <el-step title="记录物流信息" description="更新发货和配送状态" />
      </el-steps>
    </div>

    <div class="guide-section">
      <h2><el-icon><Warning /></el-icon> 注意事项</h2>
      <el-alert
        type="warning"
        :closable="false"
        show-icon
      >
        <ul class="notice-list">
          <li>每个批次的产品应创建独立的溯源记录</li>
          <li>及时更新生产和物流信息，确保数据真实准确</li>
          <li>二维码生成后不可修改批次号，请仔细核对</li>
          <li>建议使用防水标签打印二维码，避免损坏</li>
        </ul>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
</script>

<style lang="scss" scoped>
.traceability-guide {
  .guide-section {
    margin-top: 30px;
    padding: 20px;
    background: #f5f7fa;
    border-radius: 8px;

    h2 {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .description {
      font-size: 14px;
      color: #606266;
      line-height: 1.8;
      margin-bottom: 20px;
    }

    .content-item {
      text-align: center;
      padding: 20px;
      background: white;
      border-radius: 8px;
      margin-bottom: 15px;

      .item-icon {
        font-size: 36px;
        margin-bottom: 10px;
      }

      h4 {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 5px;
      }

      p {
        font-size: 13px;
        color: #909399;
        margin: 0;
      }
    }

    .qr-example {
      display: flex;
      gap: 30px;
      align-items: center;
      background: white;
      padding: 30px;
      border-radius: 8px;

      @media (max-width: 768px) {
        flex-direction: column;
      }

      .qr-placeholder {
        text-align: center;
        padding: 20px;
        border: 2px dashed #dcdfe6;
        border-radius: 8px;
        min-width: 200px;

        p {
          margin-top: 10px;
          font-size: 14px;
          color: #606266;
        }
      }

      .qr-info {
        flex: 1;

        h4 {
          font-size: 16px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 15px;
        }

        ul {
          list-style: none;
          padding: 0;
          margin: 0;

          li {
            padding: 8px 0;
            font-size: 14px;
            color: #606266;
            position: relative;
            padding-left: 20px;

            &:before {
              content: "✓";
              position: absolute;
              left: 0;
              color: #67c23a;
              font-weight: bold;
            }
          }
        }
      }
    }

    .notice-list {
      list-style: none;
      padding: 0;
      margin: 0;

      li {
        padding: 5px 0;
        font-size: 14px;
        color: #606266;
      }
    }
  }

  :deep(.el-steps) {
    margin-top: 20px;
  }
}
</style>

