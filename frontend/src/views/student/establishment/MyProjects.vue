<template>
  <div class="my-projects-page">
    <!-- 筛选区域 -->
    <el-card class="filter-section" shadow="never">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="名称">
          <el-input
            v-model="filterForm.title"
            placeholder="搜索名称"
            clearable
            :prefix-icon="SearchIcon"
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
          <el-button type="primary" @click="handleSearch" :icon="SearchIcon">查询</el-button>
          <el-button @click="handleReset" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区域 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
           <span class="title">我的项目列表</span>
           <el-button type="primary" @click="$router.push('/establishment/apply')">
              <el-icon><Plus /></el-icon> 申请新项目
           </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#1e293b', fontWeight: '600', fontSize: '13px' }"
        :cell-style="{ color: '#334155', fontSize: '13px' }"
        border
      >
        <el-table-column type="expand" label="展开" width="60">
          <template #default="{ row }">
            <div class="expand-content">
               <el-descriptions title="详细信息" :column="3" size="small" border>
                  <el-descriptions-item label="项目简介" :span="3">{{ row.description || "暂无" }}</el-descriptions-item>
                  <el-descriptions-item label="预期成果" :span="3">{{ row.expected_results || "暂无" }}</el-descriptions-item>
                  <el-descriptions-item label="创建时间">{{ formatDate(row.created_at) }}</el-descriptions-item>
                  <el-descriptions-item label="更新时间">{{ formatDate(row.updated_at) }}</el-descriptions-item>
               </el-descriptions>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="title" label="项目名称" min-width="180" show-overflow-tooltip fixed="left">
           <template #default="{ row }">
             <span class="link-text" @click="handleEdit(row)">{{ row.title }}</span>
           </template>
        </el-table-column>

        <el-table-column prop="level" label="项目级别" width="100" align="center">
          <template #default="{ row }">
             <el-tag :type="getLevelType(row.level)" effect="plain" size="small">{{ getLabel(levelOptions, row.level) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="category" label="项目类别" width="120" align="center">
           <template #default="{ row }">
               {{ getLabel(categoryOptions, row.category) }}
           </template>
        </el-table-column>

        <el-table-column prop="is_key_field" label="是否重点领域项目" width="130" align="center">
           <template #default="{ row }">
              {{ row.is_key_field ? '是' : '否' }}
           </template>
        </el-table-column>

        <el-table-column prop="special_project_type" label="重点领域项目代码" width="130" align="center">
           <template #default="{ row }">
              {{ row.special_project_type || '-' }}
           </template>
        </el-table-column>

        <el-table-column label="负责人姓名" width="100" align="center">
          <template #default="{ row }">
             {{ row.creator?.real_name || row.creator?.username || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="负责人学号" width="120" align="center">
          <template #default="{ row }">
             {{ row.creator?.employee_id || row.creator?.username || '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="college" label="学院" width="140" show-overflow-tooltip>
           <template #default="{ row }">
              {{ getLabel(collegeOptions, row.college) }}
           </template>
        </el-table-column>

        <el-table-column prop="leader_contact" label="联系电话" width="120" show-overflow-tooltip />
        <el-table-column prop="leader_email" label="邮箱" width="160" show-overflow-tooltip />
        
        <el-table-column prop="budget" label="项目经费" width="100" align="right">
           <template #default="{ row }">
              {{ row.budget }}
           </template>
        </el-table-column>

        <el-table-column label="审核节点" width="120" align="center" fixed="right">
          <template #default="{ row }">
             <el-tag :type="getStatusColor(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="{ row }">
            <!-- Draft Action -->
            <template v-if="row.status === 'DRAFT'">
                <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
            </template>
            <!-- View Action -->
            <template v-else>
                <el-button type="primary" link size="small" @click="handleEdit(row)">查看</el-button>
                <el-button type="warning" link size="small" @click="handleWithdraw(row)" v-if="canWithdraw(row)">撤回</el-button>
            </template>
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
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search as SearchIcon, RefreshLeft, Plus } from "@element-plus/icons-vue";
import { getMyProjects, deleteProject } from "@/api/project";
import { useRouter } from "vue-router";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";

const router = useRouter();
const { loadDictionaries, getOptions } = useDictionary();

// Dict Options
const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
// Add status mapping if needed, or hardcode common statuses
const statusMap: Record<string, string> = {
    'DRAFT': '草稿',
    'SUBMITTED': '已提交',
    'LEVEL1_REVIEWING': '学院审核中',
    'LEVEL1_APPROVED': '学院审核通过',
    'LEVEL1_REJECTED': '学院驳回',
    'LEVEL2_REVIEWING': '学校审核中',
    'LEVEL2_APPROVED': '立项成功',
    'LEVEL2_REJECTED': '学校驳回'
};

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
    fetchProjects();
});

const fetchProjects = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filterForm
    };
    if (!params.title) delete params.title;
    if (!params.level) delete params.level;
    if (!params.category) delete params.category;

    const response: any = await getMyProjects(params);
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || response.data?.length || 0;
    } else {
      ElMessage.error(response.message || "获取列表失败");
    }
  } catch (error: any) {
    ElMessage.error(error.message || "获取列表失败");
  } finally {
    loading.value = false;
  }
};

const formatDate = (date: string) => {
  if (!date) return "-";
  return new Date(date).toLocaleDateString();
};

const getLabel = (options: any[], value: string) => {
    const found = options.find(opt => opt.value === value);
    return found ? found.label : value;
};

const getStatusLabel = (status: string) => {
    return statusMap[status] || status;
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
    if (status.includes('APPROVED')) return 'success';
    if (status.includes('REJECTED')) return 'danger';
    if (status.includes('REVIEWING') || status === 'SUBMITTED') return 'warning';
    return 'info';
};

const handleEdit = (row: any) => {
  router.push(`/establishment/apply?id=${row.id}`);
};

const canWithdraw = (row: any) => {
    // Only allow withdraw if submitted and not fully approved/rejected yet (logic varies by requirement)
    return row.status === 'SUBMITTED'; 
};

const handleWithdraw = (_row: any) => {
    ElMessage.info("撤回功能开发中");
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定删除吗？", "提示", { type: "warning" });
    const response: any = await deleteProject(row.id);
    if (response.code === 200 || response.status === 204) {
      ElMessage.success("删除成功");
      fetchProjects();
    }
  } catch {}
};
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;



.filter-section {
  border: none;
  background: white;
  margin-bottom: 16px;
  border-radius: 4px; /* Flatter look */
  
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

.link-text {
  color: $primary-600;
  cursor: pointer;
  text-decoration: none;
  
  &:hover {
      text-decoration: underline;
  }
}

.expand-content {
  padding: 16px;
  background: $slate-50;
  border-radius: 4px;
}

.pagination-container {
  padding-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
