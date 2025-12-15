<template>
  <div class="achievements-page">
    <div class="page-header">
      <h2>结题成果查看</h2>
      <p>查看已结题项目的成果展示</p>
    </div>

    <!-- Filter/Search -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目年份">
           <el-input v-model="searchForm.year" placeholder="如: 2024" clearable />
        </el-form-item>
        <el-form-item label="项目名称">
          <el-input v-model="searchForm.keyword" placeholder="输入项目名称搜索" clearable />
        </el-form-item>
         <el-form-item label="学院">
           <el-select v-model="searchForm.college" placeholder="选择学院" clearable>
             <el-option label="计算机学院" value="CS" />
             <!-- Add more colleges or load dynamically -->
           </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div class="page-content">
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#1f2937' }"
      >
        <el-table-column prop="project_no" label="项目编号" width="120" align="center" />
        
        <el-table-column prop="title" label="项目名称" min-width="200" show-overflow-tooltip />

        <el-table-column prop="leader_name" label="负责人" width="100" align="center" />
        
        <el-table-column prop="college" label="学院" width="150" align="center" />
        
        <el-table-column label="成果形式" width="150" show-overflow-tooltip>
             <template #default="{ row }">
                 {{ row.achievement_types || '-' }}
             </template>
        </el-table-column>

        <el-table-column label="成果简介" min-width="200" show-overflow-tooltip>
             <template #default="{ row }">
                 {{ row.achievement_summary || '-' }}
             </template>
        </el-table-column>

        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
// import { getProjects } from '@/api/project'; // Reuse project list api with filters

const loading = ref(false);
const tableData = ref([]);

const searchForm = reactive({
  keyword: '',
  year: '',
  college: ''
});

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
});

// Mock data or fetch real data
const fetchData = async () => {
  loading.value = true;
  try {
    // Ideally user filtered API for 'COMPLETED' projects
    // const res = await getProjects({ ...searchForm, status: 'COMPLETED', page: pagination.page, page_size: pagination.pageSize });
    // For now mock
    await new Promise(r => setTimeout(r, 500));
    tableData.value = []; 
  } catch(e) {
    ElMessage.error('获取成果列表失败');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  pagination.page = 1;
  fetchData();
};

const resetSearch = () => {
  searchForm.keyword = '';
  searchForm.year = '';
  searchForm.college = '';
  handleSearch();
};

const handleSizeChange = (val: number) => {
  pagination.pageSize = val;
  fetchData();
};

const handleCurrentChange = (val: number) => {
  pagination.page = val;
  fetchData();
};

const handleView = (row: any) => {
   ElMessage.info('查看详情功能待开发');
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.achievements-page {
  .page-header {
      background: #ffffff;
      padding: 24px;
      border-radius: 8px;
      margin-bottom: 24px;
      box-shadow: 0 1px 4px rgba(0,21,41,0.08);

      h2 {
        margin: 0 0 8px 0;
        font-size: 20px;
        color: #1f2937;
      }

      p {
        margin: 0;
        color: #6b7280;
        font-size: 14px;
      }
  }

  .search-card {
      margin-bottom: 24px;
      border: none;
      box-shadow: 0 1px 4px rgba(0,21,41,0.08) !important;
      
      :deep(.el-card__body) {
          padding: 24px 24px 0 24px;
      }
  }

  .page-content {
      background: #ffffff;
      padding: 24px;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,21,41,0.08);
      
      .pagination-container {
         margin-top: 20px;
         display: flex;
         justify-content: flex-end;
      }
  }
}
</style>
