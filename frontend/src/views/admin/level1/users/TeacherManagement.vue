<template>
  <div class="teacher-management-page">
      <!-- Main Card -->
      <el-card class="main-card" shadow="never">
        <template #header>
           <div class="card-header">
              <div class="header-left">
                  <span class="header-title">指导教师管理</span>
                  <el-tag type="info" size="small" effect="plain" round class="count-tag ml-3">共 {{ total }} 项</el-tag>
              </div>
              <div class="header-actions">
                <el-button type="primary" @click="openCreateDialog">
                  <el-icon class="mr-1"><Plus /></el-icon>添加教师
                </el-button>
                <el-button @click="handleImportClick">
                    <el-icon class="mr-1"><Upload /></el-icon>批量导入
                </el-button>
              </div>
           </div>
        </template>

        <!-- Filter Section -->
        <div class="filter-section">
            <el-form :inline="true" :model="filters" class="filter-form">
              <el-form-item label="搜索">
                <el-input 
                  v-model="filters.search" 
                  placeholder="姓名 / 工号" 
                  clearable
                  :prefix-icon="Search"
                  style="width: 200px"
                  @keyup.enter="handleSearch"
                />
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

        <!-- Table Section -->
        <div class="table-section">
            <el-table
              v-loading="loading"
              :data="tableData"
              style="width: 100%"
              stripe
              header-cell-class-name="table-header-cell"
            >
              <el-table-column prop="employee_id" label="工号" width="120" sortable />
              <el-table-column prop="real_name" label="姓名" width="120" />
              <el-table-column prop="title" label="职称" width="120">
                 <template #default="{ row }">
                     {{ getLabel(DICT_CODES.ADVISOR_TITLE, row.title) }}
                 </template>
              </el-table-column>
              <el-table-column prop="college" label="所属学院" width="180">
                  <template #default="{ row }">
                      {{ getLabel(DICT_CODES.COLLEGE, row.college) }}
                  </template>
              </el-table-column>
              <el-table-column prop="phone" label="手机号" width="130" />
              <el-table-column prop="email" label="邮箱" min-width="180" />
              <el-table-column label="状态" width="100">
                 <template #default="scope">
                    <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
                       {{ scope.row.is_active ? '正常' : '禁用' }}
                    </el-tag>
                 </template>
              </el-table-column>
              <el-table-column label="操作" fixed="right" width="180">
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
    
            <!-- Pagination -->
            <div class="pagination-footer">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                :total="total"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                background
                size="small"
              />
            </div>
        </div>
      </el-card>

    <el-dialog
      v-model="addDialogVisible"
      :title="isEditMode ? '编辑教师' : '添加教师'"
      width="720px"
      :close-on-click-modal="false"
      @closed="resetFormState"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="90px"
        class="admin-form"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_id">
              <el-input v-model="formData.employee_id" placeholder="请输入工号" :disabled="isEditMode" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="real_name">
              <el-input v-model="formData.real_name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="!isEditMode">
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="formData.password"
                placeholder="默认 123456"
                show-password
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="title">
                <el-select v-model="formData.title" placeholder="请选择职称" style="width: 100%">
                    <el-option
                        v-for="item in titleOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                    />
                </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="formData.phone"
                placeholder="可选，11位数字"
                maxlength="11"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="可选，学校邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学院" prop="college">
              <el-select
                v-model="formData.college"
                placeholder="选择学院"
                filterable
                clearable
                allow-create
                default-first-option
                style="width: 100%"
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
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
            {{ isEditMode ? '保存修改' : '确认添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>


    <!-- Import Dialog -->
    <el-dialog
       v-model="importDialogVisible"
       title="批量导入教师"
       width="500px"
    >
       <div style="text-align: center; margin-bottom: 20px;">
          <el-upload
             class="upload-demo"
             drag
             action="#"
             :auto-upload="false"
             :limit="1"
             :on-change="handleFileChange"
             accept=".xlsx, .xls"
          >
             <el-icon class="el-icon--upload"><upload-filled /></el-icon>
             <div class="el-upload__text">
                将文件拖到此处，或 <em>点击上传</em>
             </div>
             <template #tip>
                <div class="el-upload__tip">
                   只能上传 xlsx/xls 文件，且不超过 5MB
                </div>
             </template>
          </el-upload>
       </div>
       <template #footer>
          <span class="dialog-footer">
             <el-button @click="importDialogVisible = false">取消</el-button>
             <el-button type="primary" :loading="importLoading" @click="handleImportSubmit">
                开始导入
             </el-button>
          </span>
       </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { Search, Plus, Upload, UploadFilled } from '@element-plus/icons-vue';
import { getUsers, toggleUserStatus, createUser, updateUser, deleteUser } from '@/api/users/admin';
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadFile } from 'element-plus';
import { useDictionary } from '@/composables/useDictionary';
import { DICT_CODES } from '@/api/dictionaries';

type TeacherRow = {
  id: number;
  employee_id: string;
  real_name: string;
  phone?: string;
  email?: string;
  college?: string;
  title?: string;
  is_active?: boolean;
};

type UserListResponse = {
  code?: number;
  data?: {
    results?: TeacherRow[];
    count?: number;
    total?: number;
  };
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
const tableData = ref<TeacherRow[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const addDialogVisible = ref(false);
const submitLoading = ref(false);
const isEditMode = ref(false);
const currentId = ref<number | null>(null);

const formRef = ref<FormInstance>();
const { loadDictionaries, getOptions, getLabel } = useDictionary();

const formData = reactive({
  employee_id: '',
  real_name: '',
  password: '123456',
  phone: '',
  email: '',
  college: '',
  title: ''
});

const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
const titleOptions = computed(() => getOptions(DICT_CODES.ADVISOR_TITLE));

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
  college: [{ required: true, message: '请选择学院', trigger: 'change' }],
  title: [{ required: true, message: '请选择职称', trigger: 'change' }]
};

const filters = reactive({
  search: '',
  college: '',
  role: 'TEACHER' // Filter specifically for Teachers
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

const handleEdit = (row: TeacherRow) => {
    isEditMode.value = true;
    currentId.value = row.id;
    Object.assign(formData, {
        employee_id: row.employee_id,
        real_name: row.real_name,
        phone: row.phone,
        email: row.email,
        college: row.college,
        title: row.title,
        password: '' // Don't show password
    });
    addDialogVisible.value = true;
};

const handleToggleStatus = async (row: TeacherRow) => {
   try {
     const action = row.is_active ? '禁用' : '激活';
     await ElMessageBox.confirm(`确定要${action}该教师吗？`, '提示', {
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

const handleDelete = async (row: TeacherRow) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除教师 "${row.real_name}" 吗？此操作不可恢复。`,
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

const resetFormState = () => {
  addDialogVisible.value = false;
  isEditMode.value = false;
  currentId.value = null;
  Object.assign(formData, {
    employee_id: '',
    real_name: '',
    password: '123456',
    phone: '',
    email: '',
    college: '',
    title: ''
  });
  formRef.value?.clearValidate();
};

const openCreateDialog = () => {
  resetFormState(); // Ensure clean state
  addDialogVisible.value = true;
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;

  submitLoading.value = true;
  try {
    const sanitizedId = formData.employee_id.replace(/[^a-zA-Z0-9]/g, '');
    const payload = { ...formData, employee_id: sanitizedId, role: 'TEACHER' };
    
    let res;
    if (isEditMode.value && currentId.value) {
        res = await updateUser(currentId.value, payload);
    } else {
        res = await createUser(payload);
    }

    if (isRecord(res) && res.code === 200) {
      ElMessage.success(isEditMode.value ? '修改成功' : '添加成功');
      addDialogVisible.value = false;
      loadData();
    }
  } catch (error) {
    console.error(error);
  } finally {
    submitLoading.value = false;
  }
};


// Import Logic
const importDialogVisible = ref(false);
const importFile = ref<File | null>(null);
const importLoading = ref(false);

const handleImportClick = () => {
    importDialogVisible.value = true;
    importFile.value = null;
};

const handleFileChange = (file: UploadFile) => {
    importFile.value = file.raw ?? null;
};

const handleImportSubmit = async () => {
    if (!importFile.value) {
        ElMessage.warning("请选择文件");
        return;
    }
    
    importLoading.value = true;
    try {
        const formData = new FormData();
        formData.append('file', importFile.value);
        formData.append('role', 'TEACHER'); 
        
        const { importUsers } = await import('@/api/users/admin');
        const res = await importUsers(formData);
        
        if (isRecord(res) && res.code === 200) {
            ElMessage.success((typeof res.message === "string" && res.message) || "导入成功");
            importDialogVisible.value = false;
            loadData();
        }
    } catch (error) {
        console.error(error);
        ElMessage.error(getErrorMessage(error, "导入失败"));
    } finally {
        importLoading.value = false;
    }
};

onMounted(() => {
    loadDictionaries([DICT_CODES.COLLEGE, DICT_CODES.ADVISOR_TITLE]);
    loadData();
});
</script>

<style scoped lang="scss" src="./TeacherManagement.scss"></style>
