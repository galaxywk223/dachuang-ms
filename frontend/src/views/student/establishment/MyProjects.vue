<template>
  <div class="my-projects-page">
    <el-card class="page-header" shadow="hover">
      <div class="header-content">
        <div>
          <h2>我的项目</h2>
          <p>查看和管理我申请的所有项目</p>
        </div>
        <el-button type="primary" size="large" @click="$router.push('/establishment/apply')">
            发起新项目
        </el-button>
      </div>
    </el-card>

    <div class="page-content">
      <!-- 筛选区域 -->
      <el-card class="filter-section" shadow="never">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="名称">
            <el-input
              v-model="filterForm.title"
              placeholder="搜索项目名称"
              clearable
              :prefix-icon="Search"
              style="width: 200px"
              class="modern-input"
            />
          </el-form-item>

          <el-form-item label="级别">
            <el-select
              v-model="filterForm.level"
              placeholder="全部级别"
              clearable
              style="width: 140px"
              class="modern-select"
            >
              <el-option label="全部" value="" />
              <el-option label="国家级" value="NATIONAL" />
              <el-option label="省级" value="PROVINCIAL" />
              <el-option label="校级" value="SCHOOL" />
            </el-select>
          </el-form-item>

          <el-form-item label="类别">
            <el-select
              v-model="filterForm.category"
              placeholder="全部类别"
              clearable
              style="width: 160px"
              class="modern-select"
            >
              <el-option label="全部" value="" />
              <el-option label="创新训练" value="INNOVATION_TRAINING" />
              <el-option label="创业训练" value="ENTREPRENEURSHIP_TRAINING" />
              <el-option label="创业实践" value="ENTREPRENEURSHIP_PRACTICE" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch" :icon="Search">搜索</el-button>
            <el-button @click="handleReset" :icon="RefreshLeft">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 表格区域 -->
      <el-card class="table-card" shadow="never">
        <el-table
          v-loading="loading"
          :data="tableData"
          style="width: 100%"
          :header-cell-style="{ background: '#f8fafc', color: '#475569', fontWeight: '600' }"
          class="modern-table"
        >
          <el-table-column type="expand" width="50">
            <template #default="{ row }">
              <div class="expand-content">
                <p><strong>项目简介：</strong>{{ row.description || "暂无" }}</p>
                <p><strong>类别描述：</strong>{{ row.category_description || "暂无" }}</p>
                <p v-if="row.created_at"><strong>创建时间：</strong>{{ formatDate(row.created_at) }}</p>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="title" label="项目名称" min-width="200" show-overflow-tooltip>
             <template #default="{ row }">
               <span class="project-title-link" @click="handleView(row)">{{ row.title }}</span>
             </template>
          </el-table-column>

          <el-table-column prop="level_display" label="级别" width="100" align="center">
            <template #default="{ row }">
               <el-tag :type="getLevelType(row.level)" effect="plain" size="small">{{ row.level_display }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="category_display" label="类别" width="140" align="center" />

          <el-table-column label="负责人信息" width="180">
            <template #default="{ row }">
               <div class="user-cell">
                  <div class="user-name">{{ row.leader_name }}</div>
                  <div class="user-id">{{ row.leader_student_id }}</div>
               </div>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="120" align="center">
            <template #default="{ row }">
              <div class="status-indicator">
                <span class="status-dot" :class="getStatusColor(row.status)"></span>
                <span>{{ row.status_display }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="操作" width="180" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleView(row)">详情</el-button>
              <el-divider direction="vertical" v-if="row.status === 'DRAFT'" />
              <el-button v-if="row.status === 'DRAFT'" type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
              <el-divider direction="vertical" v-if="row.status === 'DRAFT'" />
              <el-button v-if="row.status === 'DRAFT'" type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            background
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, RefreshLeft } from "@element-plus/icons-vue";
import { getMyProjects, deleteProject } from "@/api/project";
import { useRouter } from "vue-router";

const router = useRouter();

const filterForm = reactive({
  expanded: false,
  title: "",
  level: "",
  category: "",
});

const tableData = ref<any[]>([]);
const loading = ref(false);

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const fetchProjects = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filterForm
    };
    // Clean empty params
    if (!params.title) delete params.title;
    if (!params.level) delete params.level;
    if (!params.category) delete params.category;

    const response: any = await getMyProjects(params);
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || response.data?.length || 0;
    } else {
      ElMessage.error(response.message || "获取项目列表失败");
    }
  } catch (error: any) {
    ElMessage.error(error.message || "获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

const formatDate = (date: string) => {
  if (!date) return "-";
  return new Date(date).toLocaleString();
};

const handleSearch = () => {
  pagination.page = 1;
  fetchProjects();
};

const handleReset = () => {
  filterForm.title = "";
  filterForm.level = "";
  filterForm.category = "";
  pagination.page = 1;
  fetchProjects();
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchProjects();
};

const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchProjects();
};

const getLevelType = (level: string) => {
    if (level === 'NATIONAL') return 'danger';
    if (level === 'PROVINCIAL') return 'warning';
    return 'info';
};

const getStatusColor = (status: string) => {
    if (['COMPLETED', 'LEVEL1_APPROVED', 'LEVEL2_APPROVED'].includes(status)) return 'bg-success';
    if (['LEVEL1_REJECTED', 'LEVEL2_REJECTED'].includes(status)) return 'bg-danger';
    if (['SUBMITTED', 'LEVEL1_REVIEWING'].includes(status)) return 'bg-warning';
    return 'bg-info'; // Draft or default
};

const handleView = (_row: any) => {
  ElMessage.info("查看项目详情功能待开发");
};

const handleEdit = (row: any) => {
  router.push(`/establishment/apply?id=${row.id}`);
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定要删除该项目吗？删除后无法恢复。", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    const response: any = await deleteProject(row.id);
    if (response.code === 200 || response.status === 204) {
      ElMessage.success("删除成功");
      fetchProjects();
    }
  } catch (e) {
      // ignore cancel
  }
};

onMounted(() => {
  fetchProjects();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.my-projects-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  border: none;
  background: linear-gradient(135deg, white 0%, $primary-50 100%);
  border-radius: $radius-lg;
  margin-bottom: 24px;

  :deep(.el-card__body) {
    padding: 24px 32px;
  }

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0 0 8px 0;
      font-size: $font-size-2xl;
      color: $slate-900;
      font-weight: 700;
    }

    p {
      margin: 0;
      color: $slate-500;
      font-size: $font-size-sm;
    }
  }
}

.filter-section {
  border: none;
  background: white;
  margin-bottom: 24px;
  border-radius: $radius-lg;
  
  :deep(.el-card__body) {
    padding: 24px;
  }
  
  .filter-form {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    
    :deep(.el-form-item) {
      margin-bottom: 0;
      margin-right: 0;
    }
  }
}

.table-card {
  border: none;
  border-radius: $radius-lg;
  
  :deep(.el-card__body) {
    padding: 0;
  }
}

.modern-table {
  :deep(.el-table__row) {
    td {
      padding: 16px 0;
    }
  }
}

.expand-content {
  padding: 16px 24px;
  background: $slate-50;
  border-radius: $radius-md;
  
  p {
    margin: 8px 0;
    color: $slate-600;
    font-size: $font-size-sm;
  }
}

.project-title-link {
  color: $slate-900;
  font-weight: 600;
  cursor: pointer;
  transition: color 0.2s;
  
  &:hover {
    color: $primary-600;
  }
}

.user-cell {
  .user-name {
    font-weight: 500;
    color: $slate-800;
  }
  .user-id {
    font-size: $font-size-xs;
    color: $slate-500;
  }
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: $font-size-sm;
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
  
  .bg-success { background: $success; }
  .bg-warning { background: $warning; }
  .bg-danger { background: $danger; }
  .bg-info { background: $slate-400; }
}

.pagination-container {
  padding: 16px 24px;
  border-top: 1px solid $slate-100;
  display: flex;
  justify-content: flex-end;
}

// Override Element Inputs
:deep(.modern-input .el-input__wrapper),
:deep(.modern-select .el-input__wrapper) {
  box-shadow: 0 0 0 1px $slate-200 inset;
  &:hover { box-shadow: 0 0 0 1px $primary-300 inset; }
  &.is-focus { box-shadow: 0 0 0 1px $primary-600 inset; }
}
</style>
