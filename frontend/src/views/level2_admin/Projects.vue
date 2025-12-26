<template>
  <div class="projects-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
              <span class="header-title">项目管理</span>
              <el-tag type="info" size="small" effect="plain" round class="count-tag ml-3">共 {{ total }} 项</el-tag>
           </div>
           
           <div class="header-actions">
              <el-button
                type="success"
                plain
                :icon="Download"
                @click="handleBatchExport"
              >
                导出数据
              </el-button>
              <el-button
                type="warning"
                plain
                :icon="Download"
                @click="handleBatchDownload"
              >
                下载附件
              </el-button>
              <el-dropdown @command="handleBatchCommand">
                <el-button type="primary" plain>
                  批量操作
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="status">批量状态变更</el-dropdown-item>
                    <el-dropdown-item command="docs">批量导出申报书</el-dropdown-item>
                    <el-dropdown-item command="notices">批量生成立项通知书</el-dropdown-item>
                    <el-dropdown-item command="certs">批量生成结题证书</el-dropdown-item>
                    <el-dropdown-item command="notify">批量通知</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button type="primary" :icon="Plus" @click="handleCreate">
                申报项目
              </el-button>
           </div>
        </div>
      </template>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="名称/编号">
          <el-input
            v-model="filters.search"
            placeholder="项目名称或编号"
            clearable
            :prefix-icon="Search"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="级别">
          <el-select
            v-model="filters.level"
            placeholder="全部级别"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="item in levelOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="类别">
          <el-select
            v-model="filters.category"
            placeholder="全部类别"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="item in categoryOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="全部状态"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search"
            >查询</el-button
          >
          <el-button @click="handleReset" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格区域 -->
    <div class="table-section">
      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        :header-cell-style="{
          background: '#f8fafc',
          color: '#475569',
          fontWeight: '600',
          height: '48px',
        }"
        :cell-style="{ color: '#334155', height: '48px' }"
        @selection-change="handleSelectionChange"
        stripe
      >
        <el-table-column type="selection" width="55" align="center" />

        <el-table-column
          prop="title"
          label="项目名称"
          min-width="200"
          show-overflow-tooltip
          fixed="left"
        >
          <template #default="{ row }">
            <span class="project-title">{{ row.title }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="level"
          label="项目级别"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <el-tag
              :type="getLevelType(row.level)"
              effect="plain"
              size="small"
              >{{ row.level_display || getLabel(levelOptions, row.level) }}</el-tag
            >
          </template>
        </el-table-column>

        <el-table-column
          prop="category"
          label="项目类别"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-tag effect="light" size="small" type="info">{{
              row.category_display || getLabel(categoryOptions, row.category)
            }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="重点领域项目" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_key_field" type="success" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="重点领域代码" width="110" align="center">
          <template #default="{ row }">
             <span>{{ row.key_domain_code || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="leader_name"
          label="负责人姓名"
          width="100"
          align="center"
        >
          <template #default="{ row }">
             {{ row.leader_name || '-' }}
          </template>
        </el-table-column>

        <el-table-column
          prop="leader_student_id"
          label="负责人学号"
          width="120"
          align="center"
        >
           <template #default="{ row }">
               {{ row.leader_student_id || '-' }}
           </template>
        </el-table-column>

        <el-table-column
          prop="college"
          label="学院"
          width="140"
          show-overflow-tooltip
          align="center"
        >
            <template #default="{ row }">
                {{ row.college || '-' }}
            </template>
        </el-table-column>

        <el-table-column
          prop="leader_contact"
          label="联系电话"
          width="120"
          align="center"
        >
            <template #default="{ row }">
                {{ row.leader_contact || '-' }}
            </template>
        </el-table-column>

        <el-table-column
          prop="leader_email"
          label="邮箱"
          width="180"
          show-overflow-tooltip
          align="center"
        >
            <template #default="{ row }">
                {{ row.leader_email || '-' }}
            </template>
        </el-table-column>

        <el-table-column
          prop="budget"
          label="项目经费"
          width="100"
          align="center"
        >
           <template #default="{ row }">
              {{ row.budget }}
           </template>
        </el-table-column>

        <el-table-column label="审核节点" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <div class="status-dot">
              <span class="dot" :class="getStatusClass(row.status)"></span>
              <span>{{ row.status_display }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)"
              >查看</el-button
            >
            <el-button link type="primary" @click="handleEdit(row)"
              >编辑</el-button
            >
            <el-button link type="danger" @click="handleDelete(row)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-footer">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          background
          size="small"
          class="custom-pagination"
        />
      </div>
    </div>
    </el-card>

    <el-dialog v-model="batchStatusDialogVisible" title="批量状态变更" width="480px">
      <el-form label-position="top">
        <el-form-item label="目标状态">
          <el-select v-model="batchStatusForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchStatusDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="batchStatusLoading" @click="submitBatchStatus">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="batchNotifyDialogVisible" title="批量通知" width="520px">
      <el-form label-position="top">
        <el-form-item label="通知标题">
          <el-input v-model="batchNotifyForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="通知内容">
          <el-input v-model="batchNotifyForm.content" type="textarea" :rows="4" placeholder="请输入内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchNotifyDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="batchNotifyLoading" @click="submitBatchNotify">发送</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, Plus, RefreshLeft, Download, ArrowDown } from "@element-plus/icons-vue";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import { getProjects, deleteProject } from "@/api/project";
import {
  exportProjects,
  batchDownloadAttachments,
  batchExportDocs,
  batchExportNotices,
  batchExportCertificates,
  batchUpdateProjectStatus,
} from "@/api/admin";
import { batchSendNotifications } from "@/api/notifications";

const { loadDictionaries, getOptions } = useDictionary();

const loading = ref(false);
const projects = ref<any[]>([]);
const selectedRows = ref<any[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const batchStatusDialogVisible = ref(false);
const batchNotifyDialogVisible = ref(false);
const batchStatusLoading = ref(false);
const batchNotifyLoading = ref(false);
const batchStatusForm = reactive({ status: "" });
const batchNotifyForm = reactive({
  title: "",
  content: "",
});

const filters = reactive({
  search: "",
  level: "",
  category: "",
  status: "",
});

const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
const statusOptions = computed(() => getOptions(DICT_CODES.PROJECT_STATUS));

const fetchProjects = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: filters.search,
      level: filters.level,
      category: filters.category,
      status: filters.status,
    };

    const res: any = await getProjects(params);
    if (res.results) {
      projects.value = res.results;
      total.value = res.count;
    } else if (res.data && res.data.results) {
      projects.value = res.data.results;
      total.value = res.data.count;
    } else {
      projects.value = Array.isArray(res) ? res : [];
      total.value = projects.value.length;
    }
  } catch (error) {
    ElMessage.error("获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchProjects();
};

const handleReset = () => {
  filters.search = "";
  filters.level = "";
  filters.category = "";
  filters.status = "";
  currentPage.value = 1;
  fetchProjects();
};

const handlePageChange = () => fetchProjects();
const handleSizeChange = () => {
  currentPage.value = 1;
  fetchProjects();
};

const handleCreate = () => {
  ElMessage.info("申报功能请在学生端进行或开发管理员代申请功能");
};

const handleView = (row: any) =>
  ElMessage.success(`正在查看项目: ${row.title}`);
const handleEdit = (row: any) => ElMessage.warning(`编辑项目: ${row.title}`);
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${row.title}"吗？此操作不可恢复！`,
      "警告",
      {
        confirmButtonText: "确定删除",
        cancelButtonText: "取消",
        type: "warning",
      }
    );
    await deleteProject(row.id);
    ElMessage.success("删除成功");
    fetchProjects();
  } catch (error) {
    if (error !== "cancel") ElMessage.error("删除失败");
  }
};

const handleSelectionChange = (val: any[]) => {
  selectedRows.value = val;
};

const ensureSelection = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning("请先勾选项目");
    return false;
  }
  return true;
};

const handleBatchExport = async () => {
  try {
    ElMessage.info("正在生成导出文件，请稍候...");
    const params: any = {};

    if (selectedRows.value.length > 0) {
      params.ids = selectedRows.value.map((row) => row.id).join(",");
    } else {
      params.search = filters.search;
      params.level = filters.level;
      params.category = filters.category;
      params.status = filters.status;
    }

    const res: any = await exportProjects(params);
    downloadFile(res, "项目数据.xlsx");
    ElMessage.success("导出成功");
  } catch (error) {
    ElMessage.error("导出失败");
  }
};

const handleBatchExportDocs = async () => {
  if (!ensureSelection()) return;
  try {
    ElMessage.info("正在生成申报书，请稍候...");
    const ids = selectedRows.value.map((row) => row.id).join(",");
    const res: any = await batchExportDocs({ ids });
    downloadFile(res, "项目申报书.zip");
    ElMessage.success("导出成功");
  } catch {
    ElMessage.error("导出失败");
  }
};

const handleBatchExportNotices = async () => {
  if (!ensureSelection()) return;
  try {
    ElMessage.info("正在生成立项通知书，请稍候...");
    const ids = selectedRows.value.map((row) => row.id).join(",");
    const res: any = await batchExportNotices({ ids });
    downloadFile(res, "立项通知书.zip");
    ElMessage.success("生成成功");
  } catch {
    ElMessage.error("生成失败");
  }
};

const handleBatchExportCertificates = async () => {
  if (!ensureSelection()) return;
  try {
    ElMessage.info("正在生成结题证书，请稍候...");
    const ids = selectedRows.value.map((row) => row.id).join(",");
    const res: any = await batchExportCertificates({ ids });
    downloadFile(res, "结题证书.zip");
    ElMessage.success("生成成功");
  } catch {
    ElMessage.error("生成失败");
  }
};

const handleBatchDownload = async () => {
  try {
    ElMessage.info("正在打包附件，请稍候...");
    const params: any = {};

    if (selectedRows.value.length > 0) {
      params.ids = selectedRows.value.map((row) => row.id).join(",");
    } else {
      params.search = filters.search;
      params.level = filters.level;
      params.category = filters.category;
      params.status = filters.status;
    }

    const res: any = await batchDownloadAttachments(params);
    if (res.type === "application/json") {
      const text = await res.text();
      const json = JSON.parse(text);
      ElMessage.error(json.message || "下载失败");
      return;
    }
    downloadFile(res, "项目附件.zip");
    ElMessage.success("下载成功");
  } catch (error) {
    ElMessage.error("下载失败，可能没有可下载的附件");
  }
};

const openBatchStatusDialog = () => {
  if (!ensureSelection()) return;
  batchStatusForm.status = "";
  batchStatusDialogVisible.value = true;
};

const submitBatchStatus = async () => {
  if (!batchStatusForm.status) {
    ElMessage.warning("请选择目标状态");
    return;
  }
  batchStatusLoading.value = true;
  try {
    const payload = {
      project_ids: selectedRows.value.map((row) => row.id),
      status: batchStatusForm.status,
    };
    const res: any = await batchUpdateProjectStatus(payload);
    if (res.code === 200) {
      ElMessage.success("状态更新成功");
      batchStatusDialogVisible.value = false;
      fetchProjects();
    }
  } catch {
    ElMessage.error("状态更新失败");
  } finally {
    batchStatusLoading.value = false;
  }
};

const openBatchNotifyDialog = () => {
  if (!ensureSelection()) return;
  batchNotifyForm.title = "";
  batchNotifyForm.content = "";
  batchNotifyDialogVisible.value = true;
};

const submitBatchNotify = async () => {
  if (!batchNotifyForm.title || !batchNotifyForm.content) {
    ElMessage.warning("请填写通知标题和内容");
    return;
  }
  batchNotifyLoading.value = true;
  try {
    const recipients = Array.from(
      new Set(selectedRows.value.map((row) => row.leader).filter(Boolean))
    );
    const res: any = await batchSendNotifications({
      title: batchNotifyForm.title,
      content: batchNotifyForm.content,
      recipients,
    });
    if (res.code === 200) {
      ElMessage.success("通知已发送");
      batchNotifyDialogVisible.value = false;
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "发送失败");
  } finally {
    batchNotifyLoading.value = false;
  }
};

const handleBatchCommand = (command: string) => {
  if (command === "status") openBatchStatusDialog();
  if (command === "docs") handleBatchExportDocs();
  if (command === "notices") handleBatchExportNotices();
  if (command === "certs") handleBatchExportCertificates();
  if (command === "notify") openBatchNotifyDialog();
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

const getLevelType = (level: string) => {
  if (level === "NATIONAL") return "danger";
  if (level === "PROVINCIAL") return "warning";
  return "info";
};

const getLabel = (options: any[], value: string) => {
  const found = options.find((opt) => opt.value === value);
  return found ? found.label : value;
};

const getStatusClass = (status: string) => {
  if (status.includes("APPROVED")) return "dot-success";
  if (status.includes("REJECTED")) return "dot-danger";
  if (status.includes("REVIEWING") || status.includes("AUDITING") || status === "SUBMITTED")
    return "dot-warning";
  return "dot-info";
};

onMounted(() => {
  loadDictionaries([
    DICT_CODES.PROJECT_LEVEL,
    DICT_CODES.PROJECT_CATEGORY,
    DICT_CODES.PROJECT_STATUS,
  ]);
  fetchProjects();
});
</script>

<style scoped lang="scss" src="./Projects.scss"></style>
