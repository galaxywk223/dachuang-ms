<template>
  <div class="projects-page page-container">
    <!-- 头部区域：标题与操作 -->
    <div class="page-header flex-between">
      <div class="header-left">
        <h2>项目管理</h2>
        <p class="subtitle">管理所有大创项目的申报、审核与进度</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" :icon="Plus" class="create-btn">
          申报项目
        </el-button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-card card-panel">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item>
          <el-input
            v-model="filters.search"
            placeholder="搜索项目名称/编号"
            :prefix-icon="Search"
            clearable
            class="search-input"
          />
        </el-form-item>
        <el-form-item>
          <el-select
            v-model="filters.level"
            placeholder="项目级别"
            clearable
            class="filter-select"
          >
            <el-option
              v-for="item in levelOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select
            v-model="filters.category"
            placeholder="项目类别"
            clearable
            class="filter-select"
          >
            <el-option
              v-for="item in categoryOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-select
            v-model="filters.status"
            placeholder="项目状态"
            clearable
            class="filter-select"
          >
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item class="action-group">
          <el-button type="primary" @click="handleSearch"> 查询 </el-button>
          <el-button @click="handleReset" plain> 重置 </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格区域 -->
    <div class="table-card card-panel">
      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
        row-class-name="project-row"
      >
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column
          prop="project_no"
          label="项目编号"
          width="130"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="font-mono text-secondary">{{ row.project_no }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="title"
          label="项目名称"
          min-width="240"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="project-title">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category_display" label="类别" width="120">
          <template #default="{ row }">
            <el-tag effect="light" type="info" class="rounded-tag">
              {{ row.category_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level_display" label="级别" width="100">
          <template #default="{ row }">
            <el-tag
              effect="plain"
              :type="row.level_display === '国家级' ? 'danger' : 'warning'"
              class="rounded-tag"
            >
              {{ row.level_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="leader_name" label="负责人" width="100">
          <template #default="{ row }">
            <div class="leader-info">
              <el-avatar :size="24" class="leader-avatar">{{
                row.leader_name.charAt(0)
              }}</el-avatar>
              <span>{{ row.leader_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <div class="status-dot">
              <span
                class="dot"
                :class="getStatusType(row.status || 'DRAFT')"
              ></span>
              <span class="status-text">{{ row.status_display }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button link type="primary" @click="handleView(row)">
                查看
              </el-button>
              <el-button link type="primary" @click="handleEdit(row)">
                编辑
              </el-button>
              <el-button link type="danger" @click="handleDelete(row)">
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-footer flex-center">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          background
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, Plus } from "@element-plus/icons-vue";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
// import { getStatusType as getStatusTypeUtil } from "@/utils/status"; // Assuming this might exist, but I'll implement inline for now

// Composables
const { loadDictionaries, getOptions } = useDictionary();

// State
const loading = ref(false);
const projects = ref<any[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const filters = reactive({
  search: "",
  level: "",
  category: "",
  status: "",
});

// Dictionary Options
const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
const statusOptions = computed(() => getOptions(DICT_CODES.PROJECT_STATUS));

// Helper for status dots
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    DRAFT: "info",
    SUBMITTED: "warning",
    IN_PROGRESS: "primary",
    COMPLETED: "success",
    CLOSED: "danger",
    LEVEL1_APPROVED: "success",
    LEVEL2_APPROVED: "success",
    LEVEL1_REJECTED: "danger",
    LEVEL2_REJECTED: "danger",
  };
  // Default fallback
  for (const key in map) {
    if (status.includes(key)) return map[key];
  }
  return map[status] || "info";
};

// Actions
const fetchProjects = async () => {
  loading.value = true;
  try {
    // 模拟延迟
    await new Promise((resolve) => setTimeout(resolve, 500));
    
    // 模拟数据
    projects.value = [
      {
        id: 1,
        project_no: "CX2024001",
        title: "基于深度学习的医疗影像辅助诊断系统",
        category_display: "创新训练",
        level_display: "国家级",
        leader_name: "林晓明",
        status: "IN_PROGRESS",
        status_display: "进行中",
        created_at: "2024-10-15 10:30:00",
      },
      {
        id: 2,
        project_no: "CY2024002",
        title: "校园绿色共享单车智能调度平台",
        category_display: "创业训练",
        level_display: "省级",
        leader_name: "陈伟",
        status: "SUBMITTED",
        status_display: "待审核",
        created_at: "2024-10-20 14:20:00",
      },
      {
        id: 3,
        project_no: "SJ2024003",
        title: "乡村振兴视域下的农产品电商直播实践",
        category_display: "创业实践",
        level_display: "校级",
        leader_name: "王芳",
        status: "COMPLETED",
        status_display: "已完成",
        created_at: "2024-09-10 09:00:00",
      },
      {
        id: 4,
        project_no: "CX2024004",
        title: "基于区块链的供应链金融信用评估模型",
        category_display: "创新训练",
        level_display: "省级",
        leader_name: "张建国",
        status: "LEVEL1_REJECTED",
        status_display: "一级审核不通过",
        created_at: "2024-11-05 11:15:00",
      },
      {
        id: 5,
        project_no: "CX2024005",
        title: "面向老年人的智能家居语音交互系统",
        category_display: "创新训练",
        level_display: "校级",
        leader_name: "刘洋",
        status: "DRAFT",
        status_display: "草稿",
        created_at: "2024-12-01 09:45:00",
      }
    ];
    total.value = 5;
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

const handleView = (row: any) => ElMessage.success(`正在查看项目: ${row.title}`);
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
    ElMessage.success("删除成功");
    fetchProjects();
  } catch {
    // canceled
  }
};

// Lifecycle
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

.page-header {
  margin-bottom: $spacing-lg;

  h2 {
    font-size: 24px;
    font-weight: 600;
    color: $color-text-primary;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
  }

  .subtitle {
    font-size: 14px;
    color: $color-text-regular;
    margin: 0;
  }

  .create-btn {
    box-shadow: 0 4px 14px rgba($primary-600, 0.3);
    transition: transform 0.2s;
    
    &:hover {
      transform: translateY(-1px);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
}

.filter-card {
  padding: 24px 24px 0 24px;
  margin-bottom: $spacing-lg;
  border-left: 4px solid $primary-600;

  .search-input {
    width: 240px;
  }

  .filter-select {
    width: 160px;
  }

  .action-group {
    margin-left: auto;
  }
}

.table-card {
  padding: 0; // Table takes full width
  
  :deep(.el-table) {
    // Remove border for cleaner look
    --el-table-border: none;
    
    th.el-table__cell {
      padding: 16px 0;
      font-weight: 600;
    }
    
    td.el-table__cell {
      padding: 16px 0;
    }
  }

  .project-title {
    font-weight: 500;
    color: $color-text-primary;
  }

  .rounded-tag {
    border-radius: 6px;
    border: none;
    padding: 0 10px;
  }

  .font-mono {
    font-family: 'JetBrains Mono', 'Roboto Mono', monospace;
    font-size: 13px;
  }
  
  .text-secondary {
    color: $color-text-regular;
  }

  .leader-info {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .leader-avatar {
      background-color: $color-border;
      color: $color-text-regular;
      font-size: 12px;
    }
  }

  .status-dot {
    display: flex;
    align-items: center;
    gap: 8px;

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      
      &.info { background-color: $info; }
      &.primary { background-color: $primary-600; }
      &.success { background-color: $success; }
      &.warning { background-color: $warning; }
      &.danger { background-color: $danger; }
    }
    
    .status-text {
      font-size: 13px;
    }
  }

  .table-actions {
    display: flex;
    gap: 12px;
    
    .el-button {
      padding: 0;
      height: auto;
      font-weight: 500;
      
      &.is-link {
        &:hover {
          text-decoration: underline;
        }
      }
    }
  }

  .pagination-footer {
    padding: 20px;
    border-top: 1px solid $color-border-light;
    justify-content: flex-end;
  }
}
</style>
