```html
<template>
  <div>
    <div class="page-container">
      <!-- Filter Bar -->

      <!-- Filter Bar -->
      <el-card class="filter-card" shadow="never">
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="搜索">
            <el-input 
              v-model="filters.search" 
              placeholder="姓名 / 工号" 
              clearable
              @keyup.enter="handleSearch"
            >
               <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-form-item>
          
          <el-form-item label="学院">
            <el-select
              v-model="filters.college"
              placeholder="选择学院"
              clearable
              filterable
              style="width: 180px"
            >
              <el-option
                v-for="item in collegeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
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
        <div class="table-header">
          <div class="title-bar">
            <span class="title">二级管理员管理</span>
             <el-tag type="info" size="small" effect="plain" round class="count-tag">共 {{ total }} 项</el-tag>
          </div>
          <div class="actions">
            <el-button type="primary" @click="openCreateDialog">
              <el-icon><Plus /></el-icon>添加管理员
            </el-button>
          </div>
        </div>

        <el-table
          v-loading="loading"
          :data="tableData"
          style="width: 100%"
          stripe
        >
          <el-table-column prop="employee_id" label="工号" width="120" sortable />
          <el-table-column prop="real_name" label="姓名" width="120" />
          <el-table-column prop="college" label="所属学院" width="180" />
          <el-table-column prop="department" label="部门" width="140" />
          <el-table-column label="状态" width="100">
             <template #default="scope">
                <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
                   {{ scope.row.is_active ? '正常' : '禁用' }}
                </el-tag>
             </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" min-width="150">
            <template #default="scope">
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
            :page-sizes="[10, 20, 50]"
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
      title="添加二级管理员"
      width="720px"
      :close-on-click-modal="false"
      @closed="resetAdminForm"
    >
      <el-form
        ref="adminFormRef"
        :model="adminForm"
        :rules="formRules"
        label-width="90px"
        class="admin-form"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_id">
              <el-input v-model="adminForm.employee_id" placeholder="请输入工号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="real_name">
              <el-input v-model="adminForm.real_name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="adminForm.password"
                placeholder="默认 123456"
                show-password
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="adminForm.phone"
                placeholder="可选，11位数字"
                maxlength="11"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="adminForm.email" placeholder="可选，学校邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学院" prop="college">
              <el-select
                v-model="adminForm.college"
                placeholder="选择学院"
                filterable
                clearable
                allow-create
                default-first-option
              >
                <el-option
                  v-for="item in collegeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="部门" prop="department">
              <el-input
                v-model="adminForm.department"
                placeholder="可填学院下属部门/科室"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleCreateAdmin">
            确认添加
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { Search, Plus } from '@element-plus/icons-vue';
import { getUsers, toggleUserStatus, createUser } from '@/api/user-admin';
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus';
import { useDictionary } from '@/composables/useDictionary';
import { DICT_CODES } from '@/api/dictionary';

const loading = ref(false);
const tableData = ref<any[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const addDialogVisible = ref(false);
const submitLoading = ref(false);
const adminFormRef = ref<FormInstance>();
const { loadDictionaries, getOptions } = useDictionary();
const adminForm = reactive({
  employee_id: '',
  real_name: '',
  password: '123456',
  phone: '',
  email: '',
  college: '',
  department: ''
});

const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
const formRules: FormRules = {
  employee_id: [
    { required: true, message: '请输入工号', trigger: 'blur' },
    { min: 4, max: 20, message: '长度应在 4-20 个字符内', trigger: 'blur' }
  ],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  phone: [
    {
      validator: (_rule, value, callback) => {
        if (!value) return callback();
        if (!/^\d{11}$/.test(value)) {
          return callback(new Error('手机号需为 11 位数字'));
        }
        return callback();
      },
      trigger: 'blur'
    }
  ],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  college: [{ required: true, message: '请选择学院', trigger: 'change' }]
};

const filters = reactive({
  search: '',
  college: '',
  role: 'LEVEL2_ADMIN' // Filter specifically for Level 2 Admins
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
    if (!params.search) delete (params as any).search;
    if (!params.college) delete (params as any).college;

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

const handleEdit = (row: any) => {
    ElMessage.info('编辑: ' + row.real_name);
};

const handleToggleStatus = async (row: any) => {
   try {
     const action = row.is_active ? '禁用' : '激活';
     await ElMessageBox.confirm(`确定要${action}该管理员吗？`, '提示', {
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

const resetAdminForm = () => {
  Object.assign(adminForm, {
    employee_id: '',
    real_name: '',
    password: '123456',
    phone: '',
    email: '',
    college: '',
    department: ''
  });
  adminFormRef.value?.clearValidate();
};

const openCreateDialog = () => {
  resetAdminForm();
  addDialogVisible.value = true;
};

const handleCreateAdmin = async () => {
  if (!adminFormRef.value) return;
  const valid = await adminFormRef.value.validate().catch(() => false);
  if (!valid) return;

  submitLoading.value = true;
  try {
    const payload = { ...adminForm, role: 'LEVEL2_ADMIN' };
    const res = await createUser(payload);
    if (res.code === 200) {
      ElMessage.success('管理员添加成功，默认密码为 123456');
      addDialogVisible.value = false;
      resetAdminForm();
      loadData();
    }
  } catch (error) {
    console.error(error);
    ElMessage.error('添加管理员失败');
  } finally {
    submitLoading.value = false;
  }
};

onMounted(() => {
    loadDictionaries([DICT_CODES.COLLEGE]);
    loadData();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.page-container {
  padding: 0;
}

.page-header {
  display: none;
}

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

.admin-form {
  margin-top: 4px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
