<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">负责人信息</span>
    </div>
    <el-row :gutter="24">
      <el-col :span="12">
        <el-form-item label="负责人姓名">
          <el-input :model-value="currentUser.name" disabled class="is-disabled-soft" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="负责人学号">
          <el-input :model-value="currentUser.student_id" disabled class="is-disabled-soft" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="联系电话" prop="leader_contact">
          <el-input v-model="formData.leader_contact" placeholder="手机号" />
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="电子邮箱" prop="leader_email">
          <el-input v-model="formData.leader_email" placeholder="邮箱" />
        </el-form-item>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  formData: any;
  currentUser: { name: string; student_id: string };
}>();
</script>
