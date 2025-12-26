<template>
  <div class="help-page">
    <div class="page-content">
      <el-card class="main-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="header-title">帮助中心</span>
          </div>
        </template>
        
        <div class="help-content">
          <h3 class="section-title">常见问题</h3>
          <el-collapse>
            <el-collapse-item title="如何申报项目？" name="1">
              <div class="faq-content">
                请在"立项申报"菜单中点击"申请立项"按钮，如实填写项目信息并提交。提交后请关注审核状态。
              </div>
            </el-collapse-item>
            <el-collapse-item title="审核流程是怎样的？" name="2">
              <div class="faq-content">
                项目申报提交后，会依次经过指导老师审核、学院(二级)审核、学校(一级)审核。您可以在项目列表中查看当前状态。
              </div>
            </el-collapse-item>
            <el-collapse-item title="经费如何报销？" name="3">
              <div class="faq-content">
                请在"经费管理"中录入支出记录，并上传相关发票凭证。经审核通过后即可报销。
              </div>
            </el-collapse-item>
            <el-collapse-item title="忘记密码怎么办？" name="4">
              <div class="faq-content">
                请联系系统管理员或所在学院的教学秘书重置密码。
              </div>
            </el-collapse-item>
          </el-collapse>

          <el-divider content-position="left">联系我们</el-divider>

          <div class="contact-info">
            <div class="contact-item">
              <el-icon><Message /></el-icon>
              <span>技术支持邮箱：support@example.com</span>
            </div>
            <div class="contact-item">
              <el-icon><Location /></el-icon>
              <span>办公地点：行政楼 305 室</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Message, Location } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.help-page {
  padding: 20px;
  .page-content {
      max-width: 1200px;
      margin: 0 auto;
  }
}

.main-card {
  border-radius: 8px;
  :deep(.el-card__header) {
      padding: 16px 20px;
      font-weight: 600;
      border-bottom: 1px solid $color-border-light;
  }
}

.section-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 20px;
    color: $slate-800;
}

.faq-content {
    color: $slate-600;
    line-height: 1.6;
    padding: 10px 0;
}

.contact-info {
    display: flex;
    gap: 40px;
    margin-top: 20px;
    
    .contact-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: $slate-700;
        font-size: 15px;
        
        .el-icon {
            font-size: 18px;
            color: $primary-color;
        }
    }
}
</style>
