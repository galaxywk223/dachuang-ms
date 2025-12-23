<template>
  <div class="statistics-page">
    <el-card class="summary-card">
      <template #header>
        <div class="card-header">
          <span class="title">统计概览</span>
          <el-button type="primary" plain @click="refreshAll">刷新数据</el-button>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="8">
          <StatCard
            :icon="Folder"
            icon-bg="linear-gradient(135deg, #60a5fa 0%, #2563eb 100%)"
            :value="stats.total_projects"
            label="项目总数"
          />
        </el-col>
        <el-col :span="8">
          <StatCard
            :icon="Check"
            icon-bg="linear-gradient(135deg, #34d399 0%, #059669 100%)"
            :value="stats.approved_projects"
            label="已立项/完成"
          />
        </el-col>
        <el-col :span="8">
          <StatCard
            :icon="Clock"
            icon-bg="linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
            :value="stats.pending_review"
            label="待审核"
          />
        </el-col>
      </el-row>
    </el-card>

    <el-tabs v-model="activeTab" class="mt-4">
      <el-tab-pane label="导入与归档" name="import">
        <el-card class="tool-card">
          <template #header>
            <span class="title">历史项目导入</span>
          </template>
          <div class="tool-row">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :limit="1"
              accept=".xlsx"
            >
              <el-button type="primary">选择Excel文件</el-button>
              <template #tip>
                <div class="el-upload__tip">仅支持xlsx格式</div>
              </template>
            </el-upload>
            <el-button type="success" :loading="importing" @click="submitImport">开始导入</el-button>
          </div>
          <el-alert v-if="importResult" :title="importResult" type="info" show-icon class="mt-2" />
          <el-table v-if="importErrors.length > 0" :data="importErrorRows" border stripe class="mt-2">
            <el-table-column prop="message" label="导入错误提示" />
          </el-table>
        </el-card>

        <el-card class="tool-card mt-4">
          <template #header>
            <div class="card-header">
              <span class="title">结题归档</span>
              <el-button type="primary" plain :loading="archiving" @click="archiveClosed">归档已结题项目</el-button>
            </div>
          </template>
          <el-table :data="archiveRecords" border stripe>
            <el-table-column prop="project_no" label="项目编号" width="140" />
            <el-table-column prop="project_title" label="项目名称" min-width="200" show-overflow-tooltip />
            <el-table-column prop="archived_at" label="归档时间" width="180">
              <template #default="{ row }">{{ formatDate(row.archived_at) }}</template>
            </el-table-column>
            <el-table-column label="附件数" width="100" align="center">
              <template #default="{ row }">{{ row.attachments?.length || 0 }}</template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card class="tool-card mt-4">
          <template #header>
            <div class="card-header">
              <span class="title">项目编号工具</span>
              <div class="actions">
                <el-button type="primary" plain @click="exportProjectNos">导出编号清单</el-button>
                <el-button type="warning" plain @click="fetchDuplicateNos">编号查重</el-button>
              </div>
            </div>
          </template>
          <el-table :data="duplicateNos" border stripe>
            <el-table-column prop="project_no" label="重复编号" width="200" />
            <el-table-column prop="cnt" label="重复数量" width="100" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="外部推送" name="push">
        <el-card class="tool-card">
          <template #header>
            <span class="title">项目数据推送</span>
          </template>
          <el-form label-width="120px" label-position="top">
            <el-form-item label="项目ID列表">
              <el-input
                v-model="pushForm.projectIds"
                type="textarea"
                :rows="3"
                placeholder="请输入项目ID，用英文逗号分隔"
              />
            </el-form-item>
            <el-form-item label="目标平台">
              <el-select v-model="pushForm.target" placeholder="请选择平台" style="width: 260px">
                <el-option label="安徽省大创平台" value="ANHUI_INNOVATION_PLATFORM" />
                <el-option label="国家大创平台" value="NATIONAL_INNOVATION_PLATFORM" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="pushForm.simulate">模拟推送</el-checkbox>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="pushing" @click="submitPush">创建推送任务</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="tool-card mt-4">
          <template #header>
            <div class="card-header">
              <span class="title">推送记录</span>
              <el-button type="primary" plain @click="fetchPushRecords">刷新记录</el-button>
            </div>
          </template>
          <el-table :data="pushRecords" border stripe>
            <el-table-column prop="project_no" label="项目编号" width="140" />
            <el-table-column prop="project_title" label="项目名称" min-width="200" show-overflow-tooltip />
            <el-table-column prop="target" label="目标平台" width="180" />
            <el-table-column prop="status_display" label="状态" width="120" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column prop="response_message" label="响应信息" min-width="200" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Folder, Check, Clock } from "@element-plus/icons-vue";
import StatCard from "@/components/common/StatCard.vue";
import {
  getProjectStatistics,
  importHistoryProjects,
  archiveClosedProjects,
  pushProjectsExternal,
  getPushRecords,
  getArchives,
  exportProjectNumbers,
  getDuplicateProjectNumbers,
} from "@/api/admin";
import dayjs from "dayjs";

const activeTab = ref("import");
const stats = reactive({
  total_projects: 0,
  approved_projects: 0,
  pending_review: 0,
});

const importing = ref(false);
const importFile = ref<File | null>(null);
const importResult = ref("");
const importErrors = ref<string[]>([]);
const importErrorRows = ref<{ message: string }[]>([]);
const uploadRef = ref();

const archiving = ref(false);
const archiveRecords = ref<any[]>([]);

const pushing = ref(false);
const pushRecords = ref<any[]>([]);
const pushForm = reactive({
  projectIds: "",
  target: "ANHUI_INNOVATION_PLATFORM",
  simulate: true,
});
const duplicateNos = ref<any[]>([]);

const formatDate = (date?: string) => {
  if (!date) return "-";
  return dayjs(date).format("YYYY-MM-DD HH:mm");
};

const fetchStatistics = async () => {
  try {
    const res: any = await getProjectStatistics();
    if (res.code === 200) {
      Object.assign(stats, res.data);
    }
  } catch {
    ElMessage.error("获取统计数据失败");
  }
};

const fetchArchives = async () => {
  try {
    const res: any = await getArchives();
    if (res.code === 200) {
      archiveRecords.value = res.data || [];
    }
  } catch {
    ElMessage.error("获取归档记录失败");
  }
};

const fetchPushRecords = async () => {
  try {
    const res: any = await getPushRecords();
    if (res.code === 200) {
      pushRecords.value = res.data || [];
    }
  } catch {
    ElMessage.error("获取推送记录失败");
  }
};

const handleFileChange = (file: any) => {
  importFile.value = file.raw || null;
};

const handleFileRemove = () => {
  importFile.value = null;
};

const submitImport = async () => {
  if (!importFile.value) {
    ElMessage.warning("请先选择文件");
    return;
  }
  importing.value = true;
  try {
    const formData = new FormData();
    formData.append("file", importFile.value);
    const res: any = await importHistoryProjects(formData);
    if (res.code === 200) {
      importResult.value = `导入完成：新增 ${res.data?.created || 0} 条`;
      importErrors.value = res.data?.errors || [];
      importErrorRows.value = importErrors.value.map((message) => ({ message }));
      fetchStatistics();
    }
  } catch (error: any) {
    importResult.value = "导入失败";
    importErrors.value = [];
    importErrorRows.value = [];
    ElMessage.error(error.response?.data?.message || "导入失败");
  } finally {
    importing.value = false;
    if (uploadRef.value) {
      uploadRef.value.clearFiles();
    }
    importFile.value = null;
  }
};

const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(new Blob([blob]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const archiveClosed = async () => {
  archiving.value = true;
  try {
    const res: any = await archiveClosedProjects();
    if (res.code === 200) {
      ElMessage.success(`归档完成：新增 ${res.data?.created || 0} 条`);
      fetchArchives();
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "归档失败");
  } finally {
    archiving.value = false;
  }
};

const exportProjectNos = async () => {
  try {
    const res: any = await exportProjectNumbers();
    downloadFile(res, "项目编号清单.xlsx");
    ElMessage.success("导出成功");
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "导出失败");
  }
};

const fetchDuplicateNos = async () => {
  try {
    const res: any = await getDuplicateProjectNumbers();
    if (res.code === 200) {
      duplicateNos.value = res.data || [];
    }
  } catch {
    ElMessage.error("查重失败");
  }
};

const submitPush = async () => {
  const ids = pushForm.projectIds
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => Number(item))
    .filter((id) => !Number.isNaN(id));

  if (ids.length === 0) {
    ElMessage.warning("请输入有效的项目ID");
    return;
  }

  pushing.value = true;
  try {
    const res: any = await pushProjectsExternal({
      project_ids: ids,
      target: pushForm.target,
      simulate: pushForm.simulate,
    });
    if (res.code === 200) {
      ElMessage.success("推送任务已创建");
      fetchPushRecords();
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "推送失败");
  } finally {
    pushing.value = false;
  }
};

const refreshAll = () => {
  fetchStatistics();
  fetchArchives();
  fetchPushRecords();
  fetchDuplicateNos();
};

onMounted(() => {
  refreshAll();
});
</script>

<style scoped lang="scss">
.statistics-page {
  padding: 20px;

  .summary-card {
    margin-bottom: 24px;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .title {
    font-weight: 600;
  }

  .tool-card {
    margin-top: 12px;
  }

  .tool-row {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .actions {
    display: flex;
    gap: 12px;
  }

  .mt-2 {
    margin-top: 8px;
  }

  .mt-4 {
    margin-top: 16px;
  }
}
</style>
