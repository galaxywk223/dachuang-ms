<template>
  <div class="users-page">
    <div class="page-header">
      <h2>用户管理</h2>
      <div class="actions">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          添加用户
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-input
        v-model="filters.search"
        placeholder="搜索用户名/学号/工号"
        style="width: 250px"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="filters.role"
        placeholder="用户角色"
        clearable
        style="width: 150px"
      >
        <el-option label="学生" value="STUDENT" />
        <el-option label="二级管理员" value="LEVEL2_ADMIN" />
        <el-option label="一级管理员" value="LEVEL1_ADMIN" />
      </el-select>
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>

    <el-table v-loading="loading" :data="users" style="width: 100%">
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="employee_id" label="学号/工号" width="150" />
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="real_name" label="真实姓名" width="120" />
      <el-table-column label="角色" width="120">
        <template #default="{ row }">
          <el-tag :type="getRoleType(row.role)">{{ row.role_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column
        prop="college"
        label="学院/部门"
        min-width="180"
        show-overflow-tooltip
      />
      <el-table-column prop="phone" label="联系电话" width="130" />
      <el-table-column
        prop="email"
        label="邮箱"
        min-width="200"
        show-overflow-tooltip
      />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'">
            {{ row.is_active ? "正常" : "禁用" }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button
            text
            :type="row.is_active ? 'warning' : 'success'"
            size="small"
            @click="handleToggleStatus(row)"
          >
            {{ row.is_active ? "禁用" : "启用" }}
          </el-button>
          <el-button
            text
            type="info"
            size="small"
            @click="handleResetPassword(row)"
          >
            重置密码
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 添加/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加用户' : '编辑用户'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="学号/工号" prop="employee_id">
          <el-input
            v-model="form.employee_id"
            :disabled="dialogType === 'edit'"
          />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="学生" value="STUDENT" />
            <el-option label="二级管理员" value="LEVEL2_ADMIN" />
            <el-option label="一级管理员" value="LEVEL1_ADMIN" />
          </el-select>
        </el-form-item>
        <el-form-item label="学院/部门" prop="college">
          <el-input v-model="form.college" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item
          v-if="dialogType === 'add'"
          label="初始密码"
          prop="password"
        >
          <el-input
            v-model="form.password"
            type="password"
            placeholder="默认: 123456"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, Plus } from "@element-plus/icons-vue";
import { getUsers, createUser, updateUser, toggleUserStatus, resetUserPassword } from "@/api/user-admin";

const loading = ref(false);
const users = ref<any[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const filters = reactive({
  search: "",
  role: "",
});

const dialogVisible = ref(false);
const dialogType = ref<"add" | "edit">("add");
const formRef = ref();
const form = reactive({
  id: 0,
  employee_id: "",
  username: "",
  real_name: "",
  role: "STUDENT",
  college: "",
  phone: "",
  email: "",
  password: "123456",
});

const rules = {
  employee_id: [
    { required: true, message: "请输入学号/工号", trigger: "blur" },
  ],
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  real_name: [{ required: true, message: "请输入真实姓名", trigger: "blur" }],
  role: [{ required: true, message: "请选择角色", trigger: "change" }],
};

const fetchUsers = async () => {
  loading.value = true;
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: filters.search,
      role: filters.role,
    };
    const res: any = await getUsers(params);
    if (res.data && res.data.results) {
        users.value = res.data.results;
        total.value = res.data.total;
    } else {
        users.value = [];
        total.value = 0;
    }
  } catch (error) {
    ElMessage.error("获取用户列表失败");
  } finally {
    loading.value = false;
  }
};

const getRoleType = (role: string) => {
  const typeMap: Record<string, string> = {
    STUDENT: "",
    LEVEL2_ADMIN: "warning",
    LEVEL1_ADMIN: "danger",
  };
  return typeMap[role] || "";
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchUsers();
};

const handleReset = () => {
  filters.search = "";
  filters.role = "";
  currentPage.value = 1;
  fetchUsers();
};

const handlePageChange = () => {
  fetchUsers();
};

const handleSizeChange = () => {
  currentPage.value = 1;
  fetchUsers();
};

const handleAdd = () => {
  dialogType.value = "add";
  resetForm();
  dialogVisible.value = true;
};

const handleEdit = (row: any) => {
  dialogType.value = "edit";
  Object.assign(form, row);
  dialogVisible.value = true;
};

const handleToggleStatus = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要${row.is_active ? "禁用" : "启用"}用户"${row.real_name}"吗？`,
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await toggleUserStatus(row.id);
    ElMessage.success(`${row.is_active ? "禁用" : "启用"}成功`);
    fetchUsers();
  } catch (e: any) {
     if(e !== 'cancel') ElMessage.error("操作失败");
  }
};

const handleResetPassword = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要重置用户"${row.real_name}"的密码吗？密码将重置为: 123456`,
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await resetUserPassword(row.id);
    ElMessage.success("密码重置成功，新密码为: 123456");
  } catch (e: any) {
     if(e !== 'cancel') ElMessage.error("操作失败");
  }
};

const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    
    if (dialogType.value === "add") {
        await createUser(form);
        ElMessage.success("添加成功");
    } else {
        await updateUser(form.id, form);
        ElMessage.success("更新成功");
    }

    dialogVisible.value = false;
    fetchUsers();
  } catch {
    // 验证失败 or api fail
  }
};

const resetForm = () => {
  form.id = 0;
  form.employee_id = "";
  form.username = "";
  form.real_name = "";
  form.role = "STUDENT";
  form.college = "";
  form.phone = "";
  form.email = "";
  form.password = "123456";
};

onMounted(() => {
  fetchUsers();
});
</script>

<style scoped lang="scss">
.users-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 500;
    }
  }

  .filter-bar {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
