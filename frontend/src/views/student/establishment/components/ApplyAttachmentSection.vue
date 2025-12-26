<template>
  <div class="form-section no-border">
    <div class="section-header">
      <span class="section-title">附件上传</span>
    </div>
    <el-form-item label="申请书" prop="attachment_file">
      <div class="attachment-container">
        <div class="actions-row">
          <el-upload
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :limit="1"
            v-model:file-list="localFileList"
            accept=".pdf"
            class="upload-demo"
          >
            <el-button type="primary" plain>
              <el-icon class="mr-1"><Upload /></el-icon> 上传申请书 (PDF)
            </el-button>
          </el-upload>

          <div class="download-section">
            <el-button v-if="currentTemplateUrl" link type="primary" @click="handleDownloadTemplate">
              <el-icon class="mr-1"><Download /></el-icon> 下载申请书模板
            </el-button>
            <el-tag v-else type="info" size="small" effect="plain">
              暂无申请书模板
            </el-tag>
          </div>
        </div>

        <div class="form-tip">只能上传pdf文件，且不超过2MB</div>
      </div>
    </el-form-item>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { Download, Upload } from "@element-plus/icons-vue";
import type { UploadUserFile } from "element-plus";

const props = defineProps<{
  fileList: UploadUserFile[];
  currentTemplateUrl: string | null;
  handleDownloadTemplate: () => void;
  handleFileChange: (file: any) => void;
  handleFileRemove: () => void;
}>();

const emit = defineEmits<{
  (event: "update:fileList", value: UploadUserFile[]): void;
}>();

const localFileList = computed({
  get: () => props.fileList,
  set: (value: UploadUserFile[]) => emit("update:fileList", value),
});
</script>
