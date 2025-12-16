<template>
  <div class="page-container">
    <div class="page-header">
      <div class="title-area">
        <h1>学生管理</h1>
        <p class="subtitle">管理全校学生账号信息</p>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openCreateDialog">
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

  <el-dialog
    v-model="addDialogVisible"
    title="添加学生"
    width="720px"
    :close-on-click-modal="false"
    @closed="resetStudentForm"
  >
    <el-form
      ref="studentFormRef"
      :model="studentForm"
      :rules="formRules"
      label-width="90px"
      class="student-form"
    >
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="学号" prop="employee_id">
            <el-input v-model="studentForm.employee_id" placeholder="请输入学号" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="姓名" prop="real_name">
            <el-input v-model="studentForm.real_name" placeholder="请输入姓名" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="studentForm.password"
              placeholder="默认 123456"
              show-password
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="手机号" prop="phone">
            <el-input
              v-model="studentForm.phone"
              placeholder="可选，11位数字"
              maxlength="11"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="studentForm.email" placeholder="可选，学校邮箱" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="学院" prop="college">
            <el-input v-model="studentForm.college" placeholder="请输入学院" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="专业" prop="major">
            <el-input v-model="studentForm.major" placeholder="请输入专业" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="年级" prop="grade">
            <el-input v-model="studentForm.grade" placeholder="如 2022" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="班级" prop="class_name">
            <el-input v-model="studentForm.class_name" placeholder="如 计科2201" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="部门" prop="department">
            <el-input
              v-model="studentForm.department"
              placeholder="可填写学院下属系"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="submitLoading"
          @click="handleCreateStudent"
        >
          确认添加
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { Search, Plus, Upload } from '@element-plus/icons-vue';
import { getUsers, toggleUserStatus, createUser } from '@/api/user-admin';
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus';

const loading = ref(false);
const tableData = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const addDialogVisible = ref(false);
const submitLoading = ref(false);
const studentFormRef = ref<FormInstance>();
const studentForm = reactive({
  employee_id: '',
  real_name: '',
  password: '123456',
  phone: '',
  email: '',
  college: '',
  major: '',
  grade: '',
  class_name: '',
  department: ''
});

const formRules: FormRules = {
  employee_id: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { min: 4, max: 20, message: '长度应在 4-20 个字符内', trigger: 'blur' }
  ],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^\d{11}$/, message: '手机号需为 11 位数字', trigger: 'blur' }
  ],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  college: [{ required: true, message: '请输入学院', trigger: 'blur' }]
};

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
    if (res.code === 200 && res.data) {
      tableData.value = res.data.results || [];
      const resultCount = res.data.count ?? res.data.total ?? tableData.value.length;
      total.value = Number.isFinite(resultCount) ? resultCount : 0;
    } else if (res.results) {
      tableData.value = res.results;
      total.value = res.count || res.results.length;
    } else {
      tableData.value = Array.isArray(res) ? res : [];
      total.value = tableData.value.length;
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
     
     const res = await toggleUserStatus(row.id);
     if (res.code === 200) {
        ElMessage.success(`${action}成功`);
        loadData();
     }
   } catch {
       // cancel
   }
};

const resetStudentForm = () => {
  Object.assign(studentForm, {
    employee_id: '',
    real_name: '',
    password: '123456',
    phone: '',
    email: '',
    college: '',
    major: '',
    grade: '',
    class_name: '',
    department: ''
  });
  studentFormRef.value?.clearValidate();
};

const openCreateDialog = () => {
  resetStudentForm();
  addDialogVisible.value = true;
};

const handleCreateStudent = async () => {
  if (!studentFormRef.value) return;
  const valid = await studentFormRef.value.validate().catch(() => false);
  if (!valid) return;

  submitLoading.value = true;
  try {
    const payload = { ...studentForm, role: 'STUDENT' };
    const res = await createUser(payload);
    if (res.code === 200) {
      ElMessage.success('学生添加成功，默认密码为 123456');
      addDialogVisible.value = false;
      resetStudentForm();
      loadData();
    }
  } catch (error) {
    console.error(error);
    ElMessage.error('添加学生失败');
  } finally {
    submitLoading.value = false;
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

.student-form {
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
