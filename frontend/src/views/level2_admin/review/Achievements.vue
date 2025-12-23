<template>
  <div class="achievements-page">


    <!-- Filter/Search -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目年份">
           <el-input v-model="searchForm.year" placeholder="如: 2024" clearable />
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="项目名称/成果名称" clearable />
        </el-form-item>
         <el-form-item label="学院">
           <el-input v-model="searchForm.college" placeholder="学院名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
          <el-button type="success" plain @click="handleExport">导出表格</el-button>
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
        
        <el-table-column prop="title" label="成果名称" min-width="200" show-overflow-tooltip />

        <el-table-column prop="achievement_type_display" label="类型" width="120" align="center">
            <template #default="{ row }">
                <el-tag effect="light">{{ row.achievement_type_display }}</el-tag>
            </template>
        </el-table-column>

        <el-table-column label="项目信息" min-width="200">
             <template #default="{ row }">
                 <div class="text-sm">
                     <div class="font-medium">{{ row.project_title || '-' }}</div>
                     <div class="text-xs text-gray-500">{{ row.project_no }} | {{ row.leader_name }}</div>
                 </div>
             </template>
        </el-table-column>
        
        <el-table-column label="发表/获奖时间" width="150" align="center">
            <template #default="{ row }">
                {{ row.publication_date || row.award_date || '-' }}
            </template>
        </el-table-column>
        
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
import { getAchievements, exportAchievements } from '@/api/admin';

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

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
        page: pagination.page,
        page_size: pagination.pageSize,
        search: searchForm.keyword,
        year: searchForm.year,
        college: searchForm.college
    };
    const res: any = await getAchievements(params);
    if (res.results) {
        tableData.value = res.results.map((item: any) => ({
            ...item,
            // Map flat fields if needed, but serializer provides project, title, etc.
            project_title: item.project?.title || item.project_title, // Depends on serializer (ProjectAchievementSerializer has project: id)
            // Wait, ProjectAchievementSerializer (nested) usually returns project ID.
            // I need to update Serializer to return Project Details or use source='project.title'
            // Let's check serializer again.
            // ProjectAchievementSerializer (Step 160) fields: "project" (default PK). 
            // It does NOT include project title/leader name by default unless I add them.
            // I should update ProjectAchievementSerializer to include project info.
        }));
        pagination.total = res.count;
    } else if (res.data) {
        // Handle standard response wrapper
        tableData.value = res.data.results;
        pagination.total = res.data.total;
    }
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

const handleExport = async () => {
    try {
        ElMessage.info("正在生成导出文件...");
        const params = {
            search: searchForm.keyword,
            year: searchForm.year,
            college: searchForm.college
        };
        const res: any = await exportAchievements(params);
        downloadFile(res, "成果列表.xlsx");
        ElMessage.success("导出成功");
    } catch (e) {
        ElMessage.error("导出失败");
    }
};

const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(new Blob([blob]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
   // Show details dialog (Can implement later)
   // For now just show alert with full info
   ElMessage.info(`查看成果: ${row.title}`);
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
