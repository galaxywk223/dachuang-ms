<template>
  <div class="user-management-page">
    <el-tabs
      v-model="activeTab"
      class="custom-tabs user-tabs"
      @tab-change="handleTabChange"
    >
      <el-tab-pane
        v-for="tab in userTabs"
        :key="tab.name"
        :label="tab.label"
        :name="tab.name"
      />
    </el-tabs>
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">{{ activeTabLabel }}</span>
            <el-tag type="info" size="small" effect="plain"
              >共 {{ total }} 项</el-tag
            >
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="openCreateDialog">
              <el-icon><Plus /></el-icon>
              添加用户
            </el-button>
            <el-button @click="openImportDialog">
              <el-icon><Upload /></el-icon>
              批量导入
            </el-button>
          </div>
        </div>
      </template>

      <div class="filter-section">
        <el-form :model="filters" class="filter-form" :inline="true">
          <el-form-item label="搜索">
            <el-input
              v-model="filters.search"
              placeholder="姓名 / 学号 / 工号"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix
                ><el-icon><Search /></el-icon
              ></template>
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

          <el-form-item label="状态">
            <el-select
              v-model="filters.is_active"
              placeholder="全部"
              clearable
              style="width: 120px"
            >
              <el-option label="正常" value="true" />
              <el-option label="禁用" value="false" />
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
        stripe
        style="width: 100%"
      >
        <el-table-column prop="employee_id" label="学号/工号" width="140" />
        <el-table-column prop="real_name" label="姓名" width="120" />
        <el-table-column label="角色" width="160">
          <template #default="{ row }">
            {{ row.role_info?.name || getRoleName(row.role) }}
          </template>
        </el-table-column>
        <el-table-column prop="college" label="学院" width="180">
          <template #default="{ row }">
            {{ getLabel(DICT_CODES.COLLEGE, row.college) }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? "正常" : "禁用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" min-width="200">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              size="small"
              @click="openEditDialog(row)"
              >编辑</el-button
            >
            <el-button
              link
              type="warning"
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.is_active ? "禁用" : "激活" }}
            </el-button>
            <el-button
              link
              type="danger"
              size="small"
              @click="handleDelete(row)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-footer">
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

    <el-dialog
      v-model="formDialogVisible"
      :title="isEditMode ? '编辑用户' : '添加用户'"
      width="760px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="90px"
        class="admin-form"
      >
        <el-row :gutter="16">
          <!-- 角色选择 - 放在第一位 -->
          <el-col :span="12">
            <el-form-item label="角色" prop="role">
              <el-select
                v-model="formData.role"
                placeholder="请先选择角色"
                filterable
                :disabled="isEditMode && isStudentRole"
              >
                <el-option
                  v-for="role in roleOptions"
                  :key="role.code"
                  :label="role.name"
                  :value="role.code"
                  :disabled="isEditMode && role.code === 'STUDENT'"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 密码 - 仅新建时 -->
          <el-col :span="12" v-if="!isEditMode">
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="formData.password"
                show-password
                placeholder="默认 123456"
              />
            </el-form-item>
          </el-col>

          <!-- 学生专属字段 -->
          <template v-if="isStudentRole">
            <el-col :span="12">
              <el-form-item label="学号" prop="employee_id">
                <el-input
                  v-model="formData.employee_id"
                  :disabled="isEditMode"
                  placeholder="请输入学号"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="姓名" prop="real_name">
                <el-input
                  v-model="formData.real_name"
                  placeholder="请输入姓名"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="性别" prop="gender">
                <el-select v-model="formData.gender" placeholder="请选择性别">
                  <el-option label="男" value="男" />
                  <el-option label="女" value="女" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="部门" prop="department">
                <el-select
                  v-model="formData.department"
                  placeholder="选择部门"
                  clearable
                  filterable
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
              <el-form-item label="专业名称" prop="major">
                <el-input
                  v-model="formData.major"
                  placeholder="请输入专业名称"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="当前年级" prop="grade">
                <el-input v-model="formData.grade" placeholder="如：2023" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="班级" prop="class_name">
                <el-input
                  v-model="formData.class_name"
                  placeholder="如：软231"
                />
              </el-form-item>
            </el-col>
          </template>

          <!-- 教师/管理员共同字段 -->
          <template v-if="isTeacherOrAdmin">
            <el-col :span="12">
              <el-form-item label="工号" prop="employee_id">
                <el-input
                  v-model="formData.employee_id"
                  :disabled="isEditMode"
                  placeholder="请输入工号"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="姓名" prop="real_name">
                <el-input
                  v-model="formData.real_name"
                  placeholder="请输入姓名"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职称" prop="title">
                <el-select
                  v-model="formData.title"
                  placeholder="选择职称"
                  clearable
                  filterable
                >
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
              <el-form-item label="部门" prop="department">
                <el-select
                  v-model="formData.department"
                  placeholder="选择部门"
                  clearable
                  filterable
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
          </template>

          <!-- 管理员额外字段 - 管理范围 -->
          <el-col :span="12" v-if="isAdminRole && selectedRoleScopeDimension">
            <el-form-item label="管理范围" prop="managed_scope_value">
              <el-select
                v-model="formData.managed_scope_value"
                placeholder="请选择管理范围"
                clearable
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="item in scopeValueOptions"
                  :key="item.id"
                  :label="item.label"
                  :value="item.id"
                />
              </el-select>
              <div class="form-hint">
                根据角色的数据范围维度选择具体负责的维度值
              </div>
            </el-form-item>
          </el-col>

          <!-- 联系方式 - 所有角色通用 -->
          <el-col :span="12" v-if="formData.role">
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="formData.phone"
                maxlength="11"
                placeholder="请输入手机号"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="formData.role">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="请输入邮箱" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="formDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="submitLoading"
            @click="handleSubmit"
          >
            {{ isEditMode ? "保存修改" : "确认添加" }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="importDialogVisible"
      title="批量导入用户"
      width="520px"
      :close-on-click-modal="false"
      @closed="resetImport"
    >
      <el-form :model="importForm" label-width="90px">
        <el-form-item label="角色">
          <el-select
            v-model="importForm.role"
            placeholder="选择角色"
            filterable
          >
            <el-option
              v-for="role in roleOptions"
              :key="role.code"
              :label="role.name"
              :value="role.code"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="专家级别" v-if="importForm.role === 'EXPERT'">
          <el-select
            v-model="importForm.expert_scope"
            placeholder="选择专家级别"
          >
            <el-option label="院级专家" value="COLLEGE" />
            <el-option label="校级专家" value="SCHOOL" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件">
          <el-upload
            class="file-upload"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".xlsx,.xls"
          >
            <el-icon><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="upload-tip">只能上传 xlsx/xls 文件，且不超过 5MB</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="importLoading"
            @click="handleImport"
          >
            开始导入
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Search, Plus, Upload, UploadFilled } from "@element-plus/icons-vue";
import {
  getUsers,
  createUser,
  updateUser,
  deleteUser,
  toggleUserStatus,
  importUsers,
} from "@/api/users/admin";
import { getRoleSimpleList } from "@/api/users/roles";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
  type UploadFile,
} from "element-plus";
import { useDictionary } from "@/composables/useDictionary";
import type { DictionaryItem } from "@/api/dictionaries";
import { DICT_CODES } from "@/api/dictionaries";

const route = useRoute();
const router = useRouter();

const userTabs = [
  { label: "学生管理", name: "STUDENT" },
  { label: "教师管理", name: "TEACHER" },
  { label: "管理员管理", name: "ADMIN" }, // 改为 ADMIN 表示所有管理员
] as const;

type UserTabName = (typeof userTabs)[number]["name"];

const normalizeTab = (value?: string): UserTabName => {
  if (!value) return userTabs[0].name;
  const hit = userTabs.find((tab) => tab.name === value);
  return hit?.name || userTabs[0].name;
};

type RoleOption = {
  id: number;
  code: string;
  name: string;
  default_route?: string;
  scope_dimension?: string;
};

type UserRow = {
  id: number;
  employee_id: string;
  real_name: string;
  role?: string;
  gender?: string;
  grade?: string;
  role_info?: {
    id: number;
    code: string;
    name: string;
    default_route?: string;
  };
  college?: string;
  department?: string;
  title?: string;
  major?: string;
  class_name?: string;
  phone?: string;
  email?: string;
  is_active?: boolean;
  expert_scope?: string;
  managed_scope_value?: number | null;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const normalizeList = (res: unknown) => {
  if (!isRecord(res)) return { results: [], total: 0 };
  if (res.code === 200 && isRecord(res.data)) {
    const data = res.data as Record<string, unknown>;
    const results = (data.results as UserRow[]) || [];
    const total =
      (data.count as number) ?? (data.total as number) ?? results.length;
    return { results, total };
  }
  if (Array.isArray(res.results)) {
    return {
      results: res.results as UserRow[],
      total: (res.count as number) ?? res.results.length,
    };
  }
  return { results: [], total: 0 };
};

const loading = ref(false);
const tableData = ref<UserRow[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const activeTab = ref<UserTabName>(userTabs[0].name);
const activeTabLabel = computed(
  () =>
    userTabs.find((tab) => tab.name === activeTab.value)?.label || "用户管理"
);

const formDialogVisible = ref(false);
const importDialogVisible = ref(false);
const submitLoading = ref(false);
const importLoading = ref(false);
const isEditMode = ref(false);
const currentId = ref<number | null>(null);

const roleOptions = ref<RoleOption[]>([]);
const roleMap = computed(() => {
  const map = new Map<string, string>();
  roleOptions.value.forEach((role) => map.set(role.code, role.name));
  return map;
});

const scopeValueOptions = ref<{ id: number; label: string; value: string }[]>(
  []
);

const { loadDictionaries, getOptions, getLabel } = useDictionary();
const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
const titleOptions = computed(() => getOptions(DICT_CODES.TITLE));

// 角色判断
const isStudentRole = computed(() => formData.role === "STUDENT");
const isTeacherOrAdmin = computed(
  () => formData.role && formData.role !== "STUDENT"
);
const selectedRoleScopeDimension = computed(() => {
  const role = roleOptions.value.find((r) => r.code === formData.role);
  return role?.scope_dimension || "";
});
// 判断是否为管理员角色：有scope_dimension的角色需要选择管理范围
const isAdminRole = computed(() => {
  return !!selectedRoleScopeDimension.value;
});
const isExpertRole = computed(() => formData.role === "EXPERT");

const filters = reactive<{
  search: string;
  role: UserTabName;
  college: string;
  is_active: string;
}>({
  search: "",
  role: activeTab.value,
  college: "",
  is_active: "",
});

const formRef = ref<FormInstance>();
const formData = reactive({
  employee_id: "",
  real_name: "",
  role: "",
  password: "123456",
  gender: "",
  grade: "",
  expert_scope: "COLLEGE",
  managed_scope_value: null as number | null,
  department: "",
  title: "",
  major: "",
  class_name: "",
  phone: "",
  email: "",
});

const importForm = reactive({
  role: "",
  expert_scope: "COLLEGE",
  file: null as UploadFile | null,
});

// 监听角色变化，加载对应的管理范围选项
watch(
  () => formData.role,
  async (newRole) => {
    if (!newRole || !isAdminRole.value) {
      scopeValueOptions.value = [];
      formData.managed_scope_value = null;
      return;
    }

    try {
      // 获取角色详情以获取 scope_dimension
      const roleDetail = roleOptions.value.find((r) => r.code === newRole);
      if (!roleDetail || !roleDetail.scope_dimension) {
        scopeValueOptions.value = [];
        formData.managed_scope_value = null;
        return;
      }

      const scopeDimension = roleDetail.scope_dimension;

      // 根据 scope_dimension 加载对应的字典项
      let dictCode = "";
      if (scopeDimension === "COLLEGE") {
        dictCode = DICT_CODES.COLLEGE;
      } else if (scopeDimension === "PROJECT_CATEGORY") {
        dictCode = DICT_CODES.PROJECT_CATEGORY;
      } else if (scopeDimension === "PROJECT_LEVEL") {
        dictCode = DICT_CODES.PROJECT_LEVEL;
      } else if (scopeDimension === "KEY_FIELD") {
        dictCode = DICT_CODES.KEY_FIELD_CODE;
      } else if (scopeDimension === "PROJECT_SOURCE") {
        dictCode = DICT_CODES.PROJECT_SOURCE;
      }

      if (dictCode) {
        // 先加载字典数据
        await loadDictionaries([dictCode]);
        const options = getOptions(dictCode) as DictionaryItem[];
        scopeValueOptions.value = options
          .map((opt) => {
            const id =
              typeof opt.id === "number" ? opt.id : Number(opt.value);
            if (!Number.isFinite(id)) return null;
            return {
              id,
              label: opt.label,
              value: opt.value,
            };
          })
          .filter(
            (
              opt
            ): opt is {
              id: number;
              label: string;
              value: string;
            } => Boolean(opt)
          );
      }
    } catch (error) {
      console.error("加载管理范围选项失败:", error);
      scopeValueOptions.value = [];
    }
  }
);

const formRules: FormRules = {
  employee_id: [
    { required: true, message: "请输入学号/工号", trigger: "blur" },
    { min: 4, max: 20, message: "长度应在 4-20 个字符内", trigger: "blur" },
  ],
  real_name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
  role: [{ required: true, message: "请选择角色", trigger: "change" }],
  password: [
    {
      validator: (_rule, value, callback) => {
        if (isEditMode.value) return callback();
        if (!value) return callback(new Error("请输入密码"));
        if (String(value).length < 6)
          return callback(new Error("密码至少 6 位"));
        return callback();
      },
      trigger: "blur",
    },
  ],
  email: [{ type: "email", message: "邮箱格式不正确", trigger: "blur" }],
  phone: [
    {
      validator: (_rule, value, callback) => {
        if (!value) return callback();
        if (!/^\d{11}$/.test(String(value))) {
          return callback(new Error("手机号需为 11 位数字"));
        }
        return callback();
      },
      trigger: "blur",
    },
  ],
  expert_scope: [
    {
      validator: (_rule, value, callback) => {
        if (!isExpertRole.value) return callback();
        if (!value) return callback(new Error("请选择专家级别"));
        return callback();
      },
      trigger: "change",
    },
  ],
};

const getRoleName = (code?: string) => {
  if (!code) return "-";
  return roleMap.value.get(code) || code;
};

const loadRoles = async () => {
  const res = await getRoleSimpleList();
  if (Array.isArray(res)) {
    roleOptions.value = (res as RoleOption[]).filter(
      (role) => role.code !== "EXPERT"
    );
    return;
  }
  if (isRecord(res) && Array.isArray(res.results)) {
    roleOptions.value = (res.results as RoleOption[]).filter(
      (role) => role.code !== "EXPERT"
    );
  }
};

const loadData = async () => {
  loading.value = true;
  try {
    const params: Record<string, string | number | boolean> = {
      page: currentPage.value,
      page_size: pageSize.value,
    };
    if (filters.search) params.search = filters.search;
    // 如果是管理员标签页，传递 is_admin=true 而不是具体角色
    if (filters.role === "ADMIN") {
      params.is_admin = true;
    } else if (filters.role) {
      params.role = filters.role;
    }
    if (filters.college) params.college = filters.college;
    if (filters.is_active) params.is_active = filters.is_active === "true";

    const res = await getUsers(params);
    const { results, total: totalCount } = normalizeList(res);
    tableData.value = results;
    total.value = Number.isFinite(totalCount) ? totalCount : results.length;
  } catch {
    ElMessage.error("获取用户列表失败");
    tableData.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  loadData();
};

const resetFilters = () => {
  filters.search = "";
  filters.role = activeTab.value;
  filters.college = "";
  filters.is_active = "";
  handleSearch();
};

const handleSizeChange = () => {
  currentPage.value = 1;
  loadData();
};

const handleCurrentChange = () => {
  loadData();
};

const openCreateDialog = () => {
  isEditMode.value = false;
  formData.role = filters.role || activeTab.value;
  formDialogVisible.value = true;
};

const openEditDialog = (row: UserRow) => {
  isEditMode.value = true;
  currentId.value = row.id;
  formDialogVisible.value = true;
  formData.employee_id = row.employee_id || "";
  formData.real_name = row.real_name || "";
  formData.role = row.role_info?.code || row.role || "";
  formData.gender = row.gender || "";
  formData.grade = row.grade || "";
  formData.expert_scope = row.expert_scope || "COLLEGE";
  formData.managed_scope_value = row.managed_scope_value || null;
  formData.department = row.college || "";
  formData.title = row.title || "";
  formData.major = row.major || "";
  formData.class_name = row.class_name || "";
  formData.phone = row.phone || "";
  formData.email = row.email || "";
};

const resetForm = () => {
  formRef.value?.clearValidate();
  currentId.value = null;
  formData.employee_id = "";
  formData.real_name = "";
  formData.role = "";
  formData.password = "123456";
  formData.gender = "";
  formData.grade = "";
  formData.expert_scope = "COLLEGE";
  formData.managed_scope_value = null;
  formData.department = "";
  formData.title = "";
  formData.major = "";
  formData.class_name = "";
  formData.phone = "";
  formData.email = "";
};

const handleSubmit = async () => {
  const valid = await formRef.value?.validate();
  if (!valid) return;

  submitLoading.value = true;
  try {
    const payload: Record<string, unknown> = {
      employee_id: formData.employee_id,
      real_name: formData.real_name,
      role: formData.role,
      gender: formData.gender,
      grade: formData.grade,
      expert_scope: formData.expert_scope,
      managed_scope_value: formData.managed_scope_value,
      college: formData.department,
      title: formData.title,
      major: formData.major,
      class_name: formData.class_name,
      phone: formData.phone,
      email: formData.email,
    };

    if (!isEditMode.value) {
      payload.password = formData.password || "123456";
      await createUser(payload);
      ElMessage.success("用户创建成功");
    } else if (currentId.value) {
      await updateUser(currentId.value, payload);
      ElMessage.success("用户更新成功");
    }
    formDialogVisible.value = false;
    loadData();
  } catch {
    ElMessage.error("操作失败，请检查输入");
  } finally {
    submitLoading.value = false;
  }
};

const handleToggleStatus = async (row: UserRow) => {
  try {
    await ElMessageBox.confirm(
      `确认${row.is_active ? "禁用" : "激活"}该用户？`,
      "提示",
      { type: "warning" }
    );
    await toggleUserStatus(row.id);
    ElMessage.success("操作成功");
    loadData();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("操作失败");
    }
  }
};

const handleDelete = async (row: UserRow) => {
  try {
    await ElMessageBox.confirm("确认删除该用户？", "提示", { type: "warning" });
    await deleteUser(row.id);
    ElMessage.success("删除成功");
    loadData();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
};

const openImportDialog = () => {
  importDialogVisible.value = true;
  importForm.role = filters.role || "";
};

const handleFileChange = (file: UploadFile) => {
  importForm.file = file;
};

const handleFileRemove = () => {
  importForm.file = null;
};

const resetImport = () => {
  importForm.role = "";
  importForm.expert_scope = "COLLEGE";
  importForm.file = null;
};

const handleImport = async () => {
  if (!importForm.role) {
    ElMessage.warning("请选择角色");
    return;
  }
  if (!importForm.file?.raw) {
    ElMessage.warning("请上传文件");
    return;
  }

  importLoading.value = true;
  try {
    const formDataPayload = new FormData();
    formDataPayload.append("file", importForm.file.raw);
    formDataPayload.append("role", importForm.role);
    if (importForm.role === "EXPERT") {
      formDataPayload.append("expert_scope", importForm.expert_scope);
    }
    await importUsers(formDataPayload);
    ElMessage.success("导入成功");
    importDialogVisible.value = false;
    loadData();
  } catch {
    ElMessage.error("导入失败");
  } finally {
    importLoading.value = false;
  }
};

const syncRoleFromRoute = (roleQuery?: string) => {
  const tab = normalizeTab(roleQuery);
  activeTab.value = tab;
  filters.role = tab;
  currentPage.value = 1;
  loadData();
};

const handleTabChange = (tabName: string) => {
  if (tabName === route.query.role) return;
  void router.replace({
    query: {
      ...route.query,
      role: tabName,
    },
  });
};

watch(
  () => route.query.role,
  (role) => {
    if (typeof role === "string") {
      syncRoleFromRoute(role);
    } else if (!role) {
      syncRoleFromRoute();
    }
  }
);

onMounted(async () => {
  loadDictionaries([DICT_CODES.COLLEGE, DICT_CODES.TITLE]);
  await loadRoles();
  syncRoleFromRoute(
    typeof route.query.role === "string" ? route.query.role : undefined
  );
});
</script>

<style scoped lang="scss" src="./UserManagement.scss"></style>
