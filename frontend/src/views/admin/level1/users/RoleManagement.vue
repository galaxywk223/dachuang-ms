<template>
  <div class="role-management-page">
    <el-table
      v-loading="loading"
      :data="tableData"
      stripe
      border
      style="width: 100%"
      :header-cell-style="{
        background: '#f8fafc',
        color: '#475569',
        fontWeight: '600',
      }"
    >
      <el-table-column prop="name" label="角色名称" min-width="200" />
      <el-table-column
        prop="user_count"
        label="用户数"
        width="120"
        align="center"
      />
      <el-table-column label="操作" fixed="right" width="250" align="center">
        <template #default="{ row }">
          <el-button
            link
            type="primary"
            size="small"
            :disabled="row.is_system"
            @click="openEditDialog(row)"
            >编辑</el-button
          >
          <el-button
            link
            type="warning"
            size="small"
            :disabled="row.is_system"
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
        label-width="120px"
        class="role-form"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="如：三级管理员"
            :disabled="formData.is_system"
          />
        </el-form-item>
        <el-form-item label="数据范围维度" prop="scope_dimension">
          <el-select
            v-model="formData.scope_dimension"
            placeholder="请选择"
            clearable
            :disabled="formData.is_system"
          >
            <el-option label="学院" value="COLLEGE" />
            <el-option label="非学院" value="SCHOOL" />
          </el-select>
          <div class="form-hint">
            管理员角色需要选择数据范围维度：学院=本学院，非学院=全校。
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="formDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="submitLoading"
            @click="handleSubmit"
          >
            {{ isEditMode ? "保存修改" : "确认创建" }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import {
  getRoles,
  getRoleDetail,
  createRole,
  updateRole,
  deleteRole,
  toggleRoleStatus,
} from "@/api/users/roles";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
} from "element-plus";

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
    return {
      results: res.results as RoleRow[],
      total: (res.count as number) ?? res.results.length,
    };
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

const formRef = ref<FormInstance>();
const formData = reactive({
  name: "",
  scope_dimension: "",
  is_system: false,
});

const formRules: FormRules = {
  name: [{ required: true, message: "请输入角色名称", trigger: "blur" }],
};

const loadRolesList = async () => {
  loading.value = true;
  try {
    const params: Record<string, string | number | boolean> = {
      page: currentPage.value,
      page_size: pageSize.value,
    };

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
  formData.name = row.name || "";
  formData.is_system = Boolean(row.is_system);
  try {
    const detail = await getRoleDetail(row.id);
    if (isRecord(detail)) {
      formData.scope_dimension = (detail.scope_dimension as string) || "";
    }
  } catch {
    ElMessage.error("获取角色详情失败");
  }
};

const resetForm = () => {
  formRef.value?.clearValidate();
  currentId.value = null;
  formData.name = "";
  formData.scope_dimension = "";
  formData.is_system = false;
};

const handleSubmit = async () => {
  const valid = await formRef.value?.validate();
  if (!valid) return;

  submitLoading.value = true;
  try {
    const payload = {
      name: formData.name,
      scope_dimension: formData.scope_dimension || null,
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

onMounted(() => {
  loadRolesList();
});

defineExpose({
  openCreateDialog,
});
</script>

<style scoped lang="scss" src="./RoleManagement.scss"></style>
