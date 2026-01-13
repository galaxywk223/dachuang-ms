<template>
  <div class="role-management-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="header-title">用户角色管理</span>
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新建角色
          </el-button>
        </div>
      </template>

      <div class="filter-section">
        <el-form :model="filters" class="filter-form" :inline="true">
          <el-form-item label="搜索">
            <el-input
              v-model="filters.search"
              placeholder="角色名称 / 代码"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filters.is_active" placeholder="全部" clearable>
              <el-option label="启用" value="true" />
              <el-option label="禁用" value="false" />
            </el-select>
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="filters.is_system" placeholder="全部" clearable>
              <el-option label="系统内置" value="true" />
              <el-option label="自定义" value="false" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table v-loading="loading" :data="tableData" stripe style="width: 100%">
        <el-table-column prop="code" label="角色代码" width="160" />
        <el-table-column prop="name" label="角色名称" width="140" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="default_route" label="默认路由" min-width="180" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small" effect="plain">
              {{ row.is_system ? "系统内置" : "自定义" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? "启用" : "禁用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permission_count" label="权限数" width="90" />
        <el-table-column prop="user_count" label="用户数" width="90" />
        <el-table-column label="操作" fixed="right" min-width="220">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              link
              type="warning"
              size="small"
              @click="handleToggleStatus(row)"
            >
              {{ row.is_active ? "禁用" : "启用" }}
            </el-button>
            <el-button
              link
              type="danger"
              size="small"
              :disabled="row.is_system"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
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
      :title="isEditMode ? '编辑角色' : '新建角色'"
      width="760px"
      :close-on-click-modal="false"
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="90px"
        class="role-form"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="角色代码" prop="code">
              <el-input v-model="formData.code" :disabled="formData.is_system" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="角色名称" prop="name">
              <el-input v-model="formData.name" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="描述" prop="description">
              <el-input v-model="formData.description" type="textarea" rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认路由" prop="default_route">
              <el-input v-model="formData.default_route" placeholder="如 /level1-admin/statistics" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序" prop="sort_order">
              <el-input-number v-model="formData.sort_order" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="权限" prop="permission_ids">
              <el-select
                v-model="formData.permission_ids"
                multiple
                filterable
                collapse-tags
                collapse-tags-tooltip
                class="permission-select"
                placeholder="选择权限"
              >
                <el-option-group
                  v-for="group in groupedPermissions"
                  :key="group.category"
                  :label="group.category"
                >
                  <el-option
                    v-for="perm in group.items"
                    :key="perm.id"
                    :label="perm.name"
                    :value="perm.id"
                  />
                </el-option-group>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="formDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
            {{ isEditMode ? "保存修改" : "确认创建" }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { Search, Plus } from "@element-plus/icons-vue";
import {
  getRoles,
  getRoleDetail,
  createRole,
  updateRole,
  deleteRole,
  toggleRoleStatus,
  getPermissions,
} from "@/api/users/roles";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";

type RoleRow = {
  id: number;
  code: string;
  name: string;
  description?: string;
  is_system?: boolean;
  is_active?: boolean;
  default_route?: string;
  sort_order?: number;
  permission_count?: number;
  user_count?: number;
};

type Permission = {
  id: number;
  name: string;
  code: string;
  category?: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const normalizeList = (res: unknown) => {
  if (!isRecord(res)) return { results: [], total: 0 };
  if (res.code === 200 && isRecord(res.data)) {
    const data = res.data as Record<string, unknown>;
    const results = (data.results as RoleRow[]) || [];
    const total = (data.count as number) ?? results.length;
    return { results, total };
  }
  if (Array.isArray(res.results)) {
    return { results: res.results as RoleRow[], total: (res.count as number) ?? res.results.length };
  }
  if (Array.isArray(res)) {
    return { results: res as RoleRow[], total: res.length };
  }
  return { results: [], total: 0 };
};

const loading = ref(false);
const tableData = ref<RoleRow[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);

const formDialogVisible = ref(false);
const submitLoading = ref(false);
const isEditMode = ref(false);
const currentId = ref<number | null>(null);

const permissions = ref<Permission[]>([]);

const filters = reactive({
  search: "",
  is_active: "",
  is_system: "",
});

const formRef = ref<FormInstance>();
const formData = reactive({
  code: "",
  name: "",
  description: "",
  default_route: "",
  sort_order: 0,
  permission_ids: [] as number[],
  is_system: false,
});

const groupedPermissions = computed(() => {
  const groups: Record<string, Permission[]> = {};
  permissions.value.forEach((perm) => {
    const category = perm.category || "其他";
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(perm);
  });
  return Object.entries(groups).map(([category, items]) => ({ category, items }));
});

const formRules: FormRules = {
  code: [
    { required: true, message: "请输入角色代码", trigger: "blur" },
    {
      validator: (_rule, value, callback) => {
        if (!value) return callback();
        if (!/^[A-Z0-9_]+$/.test(String(value))) {
          return callback(new Error("角色代码只能包含大写字母、数字和下划线"));
        }
        return callback();
      },
      trigger: "blur",
    },
  ],
  name: [{ required: true, message: "请输入角色名称", trigger: "blur" }],
};

const loadPermissions = async () => {
  const res = await getPermissions({ page_size: 2000 });
  if (Array.isArray(res)) {
    permissions.value = res as Permission[];
    return;
  }
  if (isRecord(res) && Array.isArray(res.results)) {
    permissions.value = res.results as Permission[];
  }
};

const loadRolesList = async () => {
  loading.value = true;
  try {
    const params: Record<string, string | number | boolean> = {
      page: currentPage.value,
      page_size: pageSize.value,
    };
    if (filters.search) params.search = filters.search;
    if (filters.is_active) params.is_active = filters.is_active === "true";
    if (filters.is_system) params.is_system = filters.is_system === "true";

    const res = await getRoles(params);
    const { results, total: totalCount } = normalizeList(res);
    tableData.value = results;
    total.value = Number.isFinite(totalCount) ? totalCount : results.length;
  } catch {
    ElMessage.error("获取角色列表失败");
    tableData.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  loadRolesList();
};

const resetFilters = () => {
  filters.search = "";
  filters.is_active = "";
  filters.is_system = "";
  handleSearch();
};

const handleSizeChange = () => {
  currentPage.value = 1;
  loadRolesList();
};

const handleCurrentChange = () => {
  loadRolesList();
};

const openCreateDialog = () => {
  isEditMode.value = false;
  formDialogVisible.value = true;
};

const openEditDialog = async (row: RoleRow) => {
  isEditMode.value = true;
  currentId.value = row.id;
  formDialogVisible.value = true;
  formData.code = row.code || "";
  formData.name = row.name || "";
  formData.description = row.description || "";
  formData.default_route = row.default_route || "";
  formData.sort_order = row.sort_order ?? 0;
  formData.is_system = Boolean(row.is_system);
  try {
    const detail = await getRoleDetail(row.id);
    if (isRecord(detail)) {
      const permissionsList = detail.permissions as Permission[] | undefined;
      if (permissionsList) {
        formData.permission_ids = permissionsList.map((perm) => perm.id);
      } else if (Array.isArray(detail.permission_ids)) {
        formData.permission_ids = detail.permission_ids as number[];
      }
    }
  } catch {
    ElMessage.error("获取角色详情失败");
  }
};

const resetForm = () => {
  formRef.value?.clearValidate();
  currentId.value = null;
  formData.code = "";
  formData.name = "";
  formData.description = "";
  formData.default_route = "";
  formData.sort_order = 0;
  formData.permission_ids = [];
  formData.is_system = false;
};

const handleSubmit = async () => {
  const valid = await formRef.value?.validate();
  if (!valid) return;

  submitLoading.value = true;
  try {
    const payload = {
      code: formData.code,
      name: formData.name,
      description: formData.description,
      default_route: formData.default_route,
      sort_order: formData.sort_order,
      permission_ids: formData.permission_ids,
    };

    if (isEditMode.value && currentId.value) {
      await updateRole(currentId.value, payload);
      ElMessage.success("角色更新成功");
    } else {
      await createRole(payload);
      ElMessage.success("角色创建成功");
    }
    formDialogVisible.value = false;
    loadRolesList();
  } catch {
    ElMessage.error("操作失败，请检查输入");
  } finally {
    submitLoading.value = false;
  }
};

const handleToggleStatus = async (row: RoleRow) => {
  try {
    await toggleRoleStatus(row.id);
    ElMessage.success("状态已更新");
    loadRolesList();
  } catch {
    ElMessage.error("操作失败");
  }
};

const handleDelete = async (row: RoleRow) => {
  try {
    await ElMessageBox.confirm("确认删除该角色？", "提示", { type: "warning" });
    await deleteRole(row.id);
    ElMessage.success("删除成功");
    loadRolesList();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
};

onMounted(async () => {
  await loadPermissions();
  loadRolesList();
});
</script>

<style scoped lang="scss" src="./RoleManagement.scss"></style>
