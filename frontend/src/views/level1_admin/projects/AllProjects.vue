<template>
  <div class="projects-page">
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
    <div class="table-container">
      <div class="table-header">
        <div class="title-bar">
          <span class="title">系统项目管理</span>
          <el-tag
            type="info"
            size="small"
            effect="plain"
            round
            class="count-tag"
            >共 {{ total }} 项</el-tag
          >
        </div>
        <div class="actions">
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
        </div>
      </div>

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
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" label="序号" width="60" align="center" />

        <el-table-column
          prop="project_no"
          label="项目编号"
          width="130"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="font-mono">{{ row.project_no || "-" }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="title"
          label="项目名称"
          min-width="220"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="project-title">{{ row.title }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="category_display"
          label="类别"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-tag effect="light" size="small" type="info">{{
              row.category_display
            }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column
          prop="level_display"
          label="级别"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <el-tag
              :type="getLevelType(row.level)"
              effect="plain"
              size="small"
              >{{ row.level_display }}</el-tag
            >
          </template>
        </el-table-column>

        <el-table-column
          prop="leader_name"
          label="负责人"
          width="100"
          align="center"
        />
        
        <el-table-column
          prop="college"
          label="所属学院"
          width="150"
          align="center"
        />

        <el-table-column label="状态" width="140" align="center">
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, RefreshLeft, Download } from "@element-plus/icons-vue";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import { getAllProjects, deleteProjectById, exportProjects, batchDownloadAttachments } from "@/api/admin";

const { loadDictionaries, getOptions } = useDictionary();

const loading = ref(false);
const projects = ref<any[]>([]);
const selectedRows = ref<any[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

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

    const res: any = await getAllProjects(params);
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

const handleView = (row: any) =>
  ElMessage.success(`正在查看项目: ${row.title}`);

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
    await deleteProjectById(row.id);
    ElMessage.success("删除成功");
    fetchProjects();
  } catch (error) {
    if (error !== "cancel") ElMessage.error("删除失败");
  }
};

const handleSelectionChange = (val: any[]) => {
  selectedRows.value = val;
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

const getStatusClass = (status: string) => {
  if (status.includes("APPROVED")) return "dot-success";
  if (status.includes("REJECTED")) return "dot-danger";
  if (status.includes("REVIEWING") || status === "SUBMITTED")
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

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.filter-section {
  background: white;
  padding: 20px 24px 0 24px;
  border-radius: $radius-lg;
  margin-bottom: 16px;
  box-shadow: $shadow-sm;
  border: 1px solid $color-border-light;

  .filter-form {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;

    :deep(.el-form-item) {
      margin-bottom: 18px;
      margin-right: 0;
    }
  }
}

.table-container {
  background: white;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  border: 1px solid $color-border-light;
  overflow: hidden;

  .table-header {
    padding: 16px 24px;
    border-bottom: 1px solid $slate-100;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .title-bar {
      display: flex;
      align-items: center;
      gap: 12px;

      .title {
        font-size: 16px;
        font-weight: 600;
        color: $slate-800;
        position: relative;
        padding-left: 14px;

        &::before {
          content: "";
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 4px;
          height: 16px;
          background: $primary-600;
          border-radius: 2px;
        }
      }
    }
  }
}

.pagination-footer {
  padding: 16px 24px;
  border-top: 1px solid $slate-100;
  display: flex;
  justify-content: flex-end;
}

.project-title {
  font-weight: 500;
  color: $slate-800;
  font-size: 14px;
}

.font-mono {
  font-family: "JetBrains Mono", monospace;
  font-size: 13px;
  color: $slate-600;
}

.status-dot {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;

    &.dot-success {
      background: $success;
      box-shadow: 0 0 0 2px rgba($success, 0.2);
    }
    &.dot-warning {
      background: $warning;
      box-shadow: 0 0 0 2px rgba($warning, 0.2);
    }
    &.dot-danger {
      background: $danger;
      box-shadow: 0 0 0 2px rgba($danger, 0.2);
    }
    &.dot-info {
      background: $slate-400;
    }
  }
}
</style>
