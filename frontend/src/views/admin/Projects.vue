<template>
  <div class="projects-page">
    <!-- 筛选区域 -->
    <el-card class="filter-section" shadow="never">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="名称/编号">
          <el-input
            v-model="filters.search"
            placeholder="搜索项目名称或编号"
            clearable
            :prefix-icon="Search"
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="级别">
          <el-select
            v-model="filters.level"
            placeholder="全部"
            clearable
            style="width: 140px"
          >
           <el-option v-for="item in levelOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="类别">
          <el-select
            v-model="filters.category"
            placeholder="全部"
            clearable
            style="width: 140px"
          >
            <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="全部"
            clearable
            style="width: 140px"
          >
           <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">查询</el-button>
          <el-button @click="handleReset" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
           <span class="title">项目列表</span>
           <el-button type="primary" :icon="Plus" @click="handleCreate"> 申报项目 </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#1e293b', fontWeight: '600', fontSize: '13px' }"
        :cell-style="{ color: '#334155', fontSize: '13px' }"
        border
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        
        <el-table-column prop="project_no" label="项目编号" width="130" show-overflow-tooltip>
           <template #default="{ row }">
             <span class="font-mono">{{ row.project_no || '-' }}</span>
           </template>
        </el-table-column>

        <el-table-column prop="title" label="项目名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="project-title">{{ row.title }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="category_display" label="类别" width="120" align="center" />
        
        <el-table-column prop="level_display" label="级别" width="100" align="center">
           <template #default="{ row }">
              <el-tag :type="getLevelType(row.level)" effect="plain" size="small">{{ row.level_display }}</el-tag>
           </template>
        </el-table-column>

        <el-table-column prop="leader_name" label="负责人" width="100" align="center" />

        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
              <el-tag :type="getStatusColor(row.status)" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          background
          size="small"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, Plus, RefreshLeft } from "@element-plus/icons-vue";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import { getProjects, deleteProject } from "@/api/project";

const { loadDictionaries, getOptions } = useDictionary();

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
    await deleteProject(row.id);
    ElMessage.success("删除成功");
    fetchProjects();
  } catch (error) {
    if (error !== 'cancel') ElMessage.error("删除失败");
  }
};

const getLevelType = (level: string) => {
    if (level === 'NATIONAL') return 'danger';
    if (level === 'PROVINCIAL') return 'warning';
    return 'info';
};

const getStatusColor = (status: string) => {
    if (status.includes('APPROVED')) return 'success';
    if (status.includes('REJECTED')) return 'danger';
    if (status.includes('REVIEWING') || status === 'SUBMITTED') return 'warning';
    return 'info';
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
  border: none;
  background: white;
  margin-bottom: 16px;
  border-radius: 4px;
  
  :deep(.el-card__body) {
    padding: 18px 24px;
    padding-bottom: 0;
  }
  
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

.table-card {
  border: none;
  border-radius: 4px;
  
  .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title {
          font-size: 16px;
          font-weight: 600;
          color: $slate-800;
          position: relative;
          padding-left: 12px;
          
          &::before {
              content: '';
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

  :deep(.el-card__header) {
      padding: 16px 24px;
      border-bottom: 1px solid $slate-100;
  }
  
  :deep(.el-card__body) {
    padding: 24px;
  }
}

.pagination-container {
  padding-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.project-title {
    font-weight: 500;
    color: $slate-800;
}

.font-mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: $slate-600;
}
</style>
