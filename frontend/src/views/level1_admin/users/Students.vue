<template>
  <div class="page-container">
    <div class="page-header">
      <div class="title-area">
        <h1>学生管理</h1>
        <p class="subtitle">管理全校学生账号信息</p>
      </div>
      <div class="action-area">
        <el-button type="primary" disabled>
          <el-icon><Plus /></el-icon>添加学生
        </el-button>
        <el-button type="success" disabled>
          <el-icon><Upload /></el-icon>批量导入
        </el-button>
      </div>
    </div>

    <!-- Filter Bar -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="搜索">
          <el-input 
            v-model="filters.search" 
            placeholder="姓名 / 学号" 
            clearable
            @keyup.enter="handleSearch"
          >
             <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="学院">
          <el-select v-model="filters.college" placeholder="选择学院" clearable style="width: 180px">
            <el-option label="计算机学院" value="计算机学院" />
            <el-option label="电气学院" value="电气学院" />
            <!-- Fetch from dictionary API ideally -->
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Table -->
    <el-card class="table-card" shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        stripe
      >
        <el-table-column prop="employee_id" label="学号" width="120" sortable />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="college" label="学院" width="180" />
        <el-table-column prop="major" label="专业" width="180" />
        <el-table-column prop="class_name" label="班级" width="140" />
        <el-table-column label="状态" width="100">
           <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
                 {{ scope.row.is_active ? '正常' : '禁用' }}
              </el-tag>
           </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="150">
          <template #default="scope">
            <el-button link type="primary" size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button 
                link 
                type="danger" 
                size="small" 
                @click="handleToggleStatus(scope.row)"
            >
                {{ scope.row.is_active ? '禁用' : '激活' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { Search, Plus, Upload } from '@element-plus/icons-vue';
import { getUsers, toggleUserStatus } from '@/api/user-admin';
import { ElMessage, ElMessageBox } from 'element-plus';

const loading = ref(false);
const tableData = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

const filters = reactive({
  search: '',
  college: '',
  role: 'STUDENT' // Fixed filter
});

const loadData = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters
    };
    // Clean empty params
    if (!params.search) delete params.search;
    if (!params.college) delete params.college;

    const res = await getUsers(params);
    if (res.code === 200) {
      tableData.value = res.data.results;
      total.value = res.data.count;
    }
  } catch (error) {
    console.error(error);
    ElMessage.error('获取数据失败');
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
    currentPage.value = 1;
    loadData();
};

const resetFilters = () => {
    filters.search = '';
    filters.college = '';
    handleSearch();
};

const handleSizeChange = (val: number) => {
    pageSize.value = val;
    loadData();
};

const handleCurrentChange = (val: number) => {
    currentPage.value = val;
    loadData();
};

const handleView = (row: any) => {
    ElMessage.info('查看详情: ' + row.real_name);
};

const handleEdit = (row: any) => {
    ElMessage.info('编辑: ' + row.real_name);
};

const handleToggleStatus = async (row: any) => {
   try {
     const action = row.is_active ? '禁用' : '激活';
     await ElMessageBox.confirm(`确定要${action}该用户吗？`, '提示', {
         type: 'warning'
     });
     
     // Mock API or Real API
     // The imported toggleUserStatus function url is /auth/admin/users/${id}/toggle-status/
     // Check if backed supports it.
     
     // Assuming success for demo if api fails or not implemented fully
     ElMessage.success(`${action}成功 (演示)`);
     // await toggleUserStatus(row.id);
     // loadData();
   } catch {
       // cancel
   }
};

onMounted(() => {
    loadData();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.page-container {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h1 {
    font-size: 24px;
    font-weight: 600;
    color: $slate-800;
    margin: 0 0 8px 0;
  }
}

.subtitle {
  color: $slate-500;
  margin: 0;
}

.filter-card {
  margin-bottom: 16px;
  :deep(.el-card__body) {
      padding: 18px 20px;
  }
}

.table-card {
    :deep(.el-card__body) {
        padding: 0;
    }
}

.pagination-container {
    padding: 16px;
    display: flex;
    justify-content: flex-end;
}
</style>
