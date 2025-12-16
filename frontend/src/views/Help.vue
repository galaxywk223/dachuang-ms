<template>
  <div class="help-page">
    <div class="page-content">
      <el-card class="help-card">
        <template #header>
          <div class="card-header">
            <el-icon><InfoFilled /></el-icon>
            <span>系统使用说明</span>
          </div>
        </template>
        <div class="help-content">
          <el-collapse>
            <el-collapse-item title="如何申报项目？" name="1">
              <p>1. 点击左侧菜单的"立项管理"</p>
              <p>2. 点击"新建项目"按钮</p>
              <p>3. 填写项目基本信息</p>
              <p>4. 提交申报材料</p>
            </el-collapse-item>
            <el-collapse-item title="如何查看项目审核进度？" name="2">
              <p>1. 进入"项目管理"页面</p>
              <p>2. 查看项目状态列</p>
              <p>3. 点击项目可查看详细信息</p>
            </el-collapse-item>

            <el-collapse-item title="如何申请结题？" name="4">
              <p>1. 进入"结题管理"页面</p>
              <p>2. 选择已完成的项目</p>
              <p>3. 提交结题报告和相关材料</p>
              <p>4. 等待审核</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>

      <el-card class="contact-card">
        <template #header>
          <div class="card-header">
            <el-icon><Phone /></el-icon>
            <span>联系我们</span>
          </div>
        </template>
        <div class="contact-content">
          <p><strong>技术支持邮箱：</strong> support@example.com</p>
          <p><strong>联系电话：</strong> 0000-00000000</p>
          <p><strong>工作时间：</strong> 周一至周五 9:00-17:00</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { InfoFilled, Phone } from "@element-plus/icons-vue";
</script>

<style scoped lang="scss">
.help-page {
  .page-header {
    background: #ffffff;
    padding: 24px;
    border-radius: 8px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

    h2 {
      margin: 0 0 8px 0;
      font-size: 24px;
      color: #262626;
    }

    p {
      margin: 0;
      color: #8c8c8c;
      font-size: 14px;
    }
  }

  .page-content {
    .help-card,
    .contact-card {
      margin-bottom: 24px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

      .card-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 16px;
        font-weight: 500;

        .el-icon {
          color: #409eff;
        }
      }

      .help-content {
        :deep(.el-collapse-item__header) {
          font-size: 14px;
          font-weight: 500;
        }

        p {
          margin: 8px 0;
          color: #606266;
          line-height: 1.6;
        }
      }

      .contact-content {
        p {
          margin: 12px 0;
          color: #606266;
          line-height: 1.8;

          strong {
            color: #262626;
          }
        }
      }
    }
  }
}
</style>
