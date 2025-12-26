<template>
  <div class="drafts-page">
    <div class="page-container">
      <!-- 筛选区域 -->
      <div class="filter-container">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="名称">
            <el-input
              v-model="filterForm.title"
              placeholder="搜索名称"
              clearable
              :prefix-icon="Search"
              style="width: 200px"
            />
          </el-form-item>

          <el-form-item label="级别">
            <el-select
              v-model="filterForm.level"
              placeholder="全部"
              clearable
              style="width: 140px"
            >
              <el-option v-for="item in levelOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item label="类别">
            <el-select
              v-model="filterForm.category"
              placeholder="全部"
              clearable
              style="width: 160px"
            >
              <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch" :icon="Search">查询</el-button>
            <el-button @click="handleReset" :icon="RefreshLeft">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 表格区域 -->
      <div class="table-container">
        <div class="status-tabs-wrapper">
             <div class="table-header-title">
                <span class="title-text">我的草稿</span>
                <el-tag type="info" size="small" effect="plain" round class="count-tag">{{ pagination.total }}</el-tag>
             </div>
             <div class="header-actions">
                <el-button type="primary" @click="$router.push('/establishment/apply')">
                   <el-icon class="el-icon--left"><Plus /></el-icon> 新建草稿
                </el-button>
             </div>
        </div>

        <el-table
          v-loading="loading"
          :data="tableData"
          style="width: 100%"
          :header-cell-style="{ background: '#f8fafc', color: '#475569', fontWeight: '600', fontSize: '13px', height: '48px' }"
          :cell-style="{ color: '#334155', fontSize: '14px', padding: '8px 0' }"
          border
        >
          <el-table-column prop="title" label="项目名称" min-width="180" show-overflow-tooltip fixed="left">
             <template #default="{ row }">
               <span class="link-text" @click="handleEdit(row)">{{ row.title || '未命名草稿' }}</span>
             </template>
          </el-table-column>

          <el-table-column prop="level" label="项目级别" width="100" align="center">
            <template #default="{ row }">
               <el-tag v-if="row.level" :type="getLevelType(row.level)" effect="plain" size="small">{{ row.level_display || getLabel(levelOptions, row.level) }}</el-tag>
               <span v-else>-</span>
            </template>
          </el-table-column>

          <el-table-column prop="category" label="项目类别" width="120" align="center">
             <template #default="{ row }">
                 {{ row.category_display || getLabel(categoryOptions, row.category) || '-' }}
             </template>
          </el-table-column>

          <el-table-column prop="is_key_field" label="重点领域项目" width="140" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_key_field" type="success" size="small" effect="light">重点领域项目</el-tag>
              <el-tag v-else type="info" size="small" effect="plain">一般项目</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="budget" label="经费" width="100" align="right">
             <template #default="{ row }">
                {{ row.budget }}
             </template>
          </el-table-column>

          <el-table-column label="操作" width="140" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
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
            size="small"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, RefreshLeft, Plus } from "@element-plus/icons-vue";
import { getMyDrafts, deleteProject } from "@/api/projects";
import { useRouter } from "vue-router";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";

const router = useRouter();
const { loadDictionaries, getOptions } = useDictionary();

// Dict Options
const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));

const filterForm = reactive({
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

onMounted(async () => {
    await loadDictionaries([
        DICT_CODES.PROJECT_LEVEL, 
        DICT_CODES.PROJECT_CATEGORY, 
        DICT_CODES.COLLEGE
    ]);
    fetchDrafts();
});

const fetchDrafts = async () => {
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

    const response: any = await getMyDrafts(params);
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || response.data?.length || 0;
    } else {
      ElMessage.error(response.message || "获取草稿列表失败");
    }
  } catch (error: any) {
    ElMessage.error(error.message || "获取草稿列表失败");
  } finally {
    loading.value = false;
  }
};

const getLabel = (options: any[], value: string) => {
    const found = options.find(opt => opt.value === value);
    return found ? found.label : value;
};

const handleSearch = () => {
  pagination.page = 1;
  fetchDrafts();
};

const handleReset = () => {
  filterForm.title = "";
  filterForm.level = "";
  filterForm.category = "";
  pagination.page = 1;
  fetchDrafts();
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchDrafts();
};

const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchDrafts();
};

const getLevelType = (level: string) => {
    if (level === 'NATIONAL') return 'danger';
    if (level === 'PROVINCIAL') return 'warning';
    return 'info';
};

const handleEdit = (row: any) => {
  router.push(`/establishment/apply?id=${row.id}`);
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定要删除该草稿吗？删除后无法恢复。", "提示", { 
        type: "warning",
        confirmButtonText: "确定",
        cancelButtonText: "取消"
    });
    const response: any = await deleteProject(row.id);
    if (response.code === 200 || response.status === 204) {
      ElMessage.success("删除成功");
      fetchDrafts();
    }
  } catch {}
};
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.filter-container {
  background: white;
  padding: 24px;
  padding-bottom: 0;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;
  margin-bottom: 24px;
  border: 1px solid $color-border-light;
}

.filter-form {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    
    :deep(.el-form-item) {
      margin-bottom: 24px;
      margin-right: 0;
    }
}

.table-container {
  background: white;
  padding: 24px;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;
  border: 1px solid $color-border-light;
  min-height: 500px;
}

.status-tabs-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid $slate-100;
  margin-bottom: 16px;
}

.table-header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .title-text {
      font-size: 16px;
      font-weight: 600;
      color: $slate-800;
      position: relative;
      padding-left: 14px;
      
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

.count-tag {
    font-weight: normal;
    color: $slate-500;
}

.link-text {
  color: $primary-600;
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
  
  &:hover {
      text-decoration: underline;
  }
}

.pagination-container {
  padding-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
