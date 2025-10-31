<template>
  <div class="settings-page">
    <h2 class="page-title">系统设置</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="基本设置" name="basic">
        <el-form
          :model="basicSettings"
          label-width="120px"
          style="max-width: 600px"
        >
          <el-form-item label="系统名称">
            <el-input v-model="basicSettings.systemName" />
          </el-form-item>
          <el-form-item label="项目申报开始时间">
            <el-date-picker
              v-model="basicSettings.applicationStartDate"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="项目申报结束时间">
            <el-date-picker
              v-model="basicSettings.applicationEndDate"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="系统公告">
            <el-input
              v-model="basicSettings.systemAnnouncement"
              type="textarea"
              :rows="4"
              placeholder="请输入系统公告"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSaveBasic"
              >保存设置</el-button
            >
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="审核设置" name="review">
        <el-form
          :model="reviewSettings"
          label-width="120px"
          style="max-width: 600px"
        >
          <el-form-item label="自动审核">
            <el-switch v-model="reviewSettings.autoReview" />
            <span style="margin-left: 10px; color: #909399">
              开启后符合条件的项目将自动通过审核
            </span>
          </el-form-item>
          <el-form-item label="审核超时提醒">
            <el-switch v-model="reviewSettings.timeoutReminder" />
            <span style="margin-left: 10px; color: #909399">
              开启后超过指定天数未审核将发送提醒
            </span>
          </el-form-item>
          <el-form-item label="超时天数">
            <el-input-number
              v-model="reviewSettings.timeoutDays"
              :min="1"
              :max="30"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSaveReview"
              >保存设置</el-button
            >
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="通知设置" name="notification">
        <el-form
          :model="notificationSettings"
          label-width="120px"
          style="max-width: 600px"
        >
          <el-form-item label="邮件通知">
            <el-switch v-model="notificationSettings.emailNotification" />
          </el-form-item>
          <el-form-item label="短信通知">
            <el-switch v-model="notificationSettings.smsNotification" />
          </el-form-item>
          <el-form-item label="站内信通知">
            <el-switch v-model="notificationSettings.systemNotification" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSaveNotification"
              >保存设置</el-button
            >
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <el-divider />

    <el-alert
      title="系统设置功能"
      type="info"
      description="当前为演示版本，设置功能正在开发中。保存的设置仅作为示例展示。"
      :closable="false"
      show-icon
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";

const activeTab = ref("basic");

const basicSettings = reactive({
  systemName: "大创项目管理平台",
  applicationStartDate: new Date("2024-09-01"),
  applicationEndDate: new Date("2024-12-31"),
  systemAnnouncement: "欢迎使用大创项目管理平台！",
});

const reviewSettings = reactive({
  autoReview: false,
  timeoutReminder: true,
  timeoutDays: 7,
});

const notificationSettings = reactive({
  emailNotification: true,
  smsNotification: false,
  systemNotification: true,
});

const handleSaveBasic = () => {
  // TODO: 调用API保存设置
  ElMessage.success("基本设置已保存");
};

const handleSaveReview = () => {
  // TODO: 调用API保存设置
  ElMessage.success("审核设置已保存");
};

const handleSaveNotification = () => {
  // TODO: 调用API保存设置
  ElMessage.success("通知设置已保存");
};
</script>

<style scoped lang="scss">
.settings-page {
  .page-title {
    margin: 0 0 20px 0;
    font-size: 20px;
    font-weight: 500;
  }
}
</style>
