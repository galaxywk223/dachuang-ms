<template>
  <div class="admins-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">二级管理员管理</span>
             <el-tag type="info" size="small" effect="plain" round class="ml-2">共 {{ total }} 项</el-tag>
           </div>
           <div class="header-actions">
             <el-button type="primary" @click="openCreateDialog">
               <el-icon><Plus /></el-icon>添加管理员
             </el-button>
           </div>
        </div>
      </template>

      <div class="filter-section mb-4">
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
      </div>

      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        stripe
        border
      >
        <el-table-column prop="employee_id" label="工号" width="120" sortable />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column prop="college" label="所属学院" width="180">
            <template #default="{ row }">
                {{ getLabel(DICT_CODES.COLLEGE, row.college) }}
            </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column label="状态" width="100">
            <template #default="scope">
                <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
                    {{ scope.row.is_active ? '正常' : '禁用' }}
                </el-tag>
            </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="150" align="center">
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
                <el-button 
                    link 
                    type="danger" 
                    size="small" 
                    @click="handleDelete(scope.row)"
                >
                    删除
                </el-button>
            </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container mt-4">
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
import { getUsers, toggleUserStatus, createUser, deleteUser } from '@/api/users/admin';
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus';
import { useDictionary } from '@/composables/useDictionary';
import { DICT_CODES } from '@/api/dictionaries';

defineOptions({ name: 'Level1AdminsView' });

type AdminRow = {
  id: number;
  employee_id: string;
  real_name: string;
  phone?: string;
  email?: string;
  college?: string;
  is_active?: boolean;
};

type UserListResponse = {
  code?: number;
  data?: {
    results?: AdminRow[];
    count?: number;
    total?: number;
  };
  results?: AdminRow[];
  count?: number;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (isRecord(response) && isRecord(response.data) && typeof response.data.message === 'string') {
    return response.data.message;
  }
  if (typeof error.message === 'string') return error.message;
  return fallback;
};

const loading = ref(false);
const tableData = ref<AdminRow[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const addDialogVisible = ref(false);
const submitLoading = ref(false);
const adminFormRef = ref<FormInstance>();
const { loadDictionaries, getOptions, getLabel } = useDictionary();
const adminForm = reactive({
  employee_id: '',
  real_name: '',
  password: '123456',
  phone: '',
  email: '',
  college: ''
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
    const params: Record<string, string | number> = {
      page: currentPage.value,
      page_size: pageSize.value,
      role: filters.role
    };
    if (filters.search) params.search = filters.search;
    if (filters.college) params.college = filters.college;

    const res = (await getUsers(params)) as UserListResponse;
    if (res.code === 200 && res.data) {
      tableData.value = res.data.results ?? [];
      const resultCount = res.data.count ?? res.data.total ?? tableData.value.length;
      total.value = Number.isFinite(resultCount) ? resultCount : 0;
    } else if (Array.isArray(res.results)) {
      tableData.value = res.results ?? [];
      total.value = res.count ?? res.results.length;
    } else if (Array.isArray(res as unknown)) {
      tableData.value = res as AdminRow[];
      total.value = tableData.value.length;
    } else {
      tableData.value = [];
      total.value = 0;
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

const handleEdit = (row: AdminRow) => {
    ElMessage.info('编辑: ' + row.real_name);
};

const handleToggleStatus = async (row: AdminRow) => {
   try {
     const action = row.is_active ? '禁用' : '激活';
     await ElMessageBox.confirm(`确定要${action}该管理员吗？`, '提示', {
         type: 'warning'
     });
     const res = await toggleUserStatus(row.id);
     if (isRecord(res) && res.code === 200) {
        ElMessage.success(`${action}成功`);
        loadData();
     }
   } catch {
       // cancel
   }
};

const handleDelete = async (row: AdminRow) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除管理员 "${row.real_name}" 吗？此操作不可恢复。`,
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    const res = await deleteUser(row.id);
    if (isRecord(res) && (res.code === 200 || res.code === 204)) {
      ElMessage.success('删除成功');
      loadData();
    } else {
       ElMessage.success('删除成功');
       loadData();
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error);
      ElMessage.error(getErrorMessage(error, '删除失败'));
    }
  }
};

const resetAdminForm = () => {
  Object.assign(adminForm, {
    employee_id: '',
    real_name: '',
    password: '123456',
    phone: '',
    email: '',
    college: ''
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
    const sanitizedId = adminForm.employee_id.replace(/[^a-zA-Z0-9]/g, '');
    const payload = { ...adminForm, employee_id: sanitizedId, role: 'LEVEL2_ADMIN' };
    const res = await createUser(payload);
    if (isRecord(res) && res.code === 200) {
      ElMessage.success('管理员添加成功，默认密码为 123456');
      addDialogVisible.value = false;
      resetAdminForm();
      loadData();
    }
  } catch (error) {
    console.error(error);
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

.admins-page {
  padding: 20px;
}

.main-card {
  border-radius: 8px;
  :deep(.el-card__header) {
      padding: 16px 20px;
      font-weight: 600;
      border-bottom: 1px solid $color-border-light;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
    display: flex;
    align-items: center;
}

.header-title {
    font-size: 16px;
    color: $slate-800;
}

.header-actions {
    display: flex;
    align-items: center;
}
    
.pagination-container {
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
    
.ml-2 { margin-left: 8px; }
.mb-4 { margin-bottom: 16px; }
.mt-4 { margin-top: 16px; }
</style>
