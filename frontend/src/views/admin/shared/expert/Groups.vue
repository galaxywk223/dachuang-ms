<template>
  <div class="expert-groups-container">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">{{ pageTitle }}</span>
           </div>
           <div class="header-actions">
             <el-button type="primary" @click="handleAdd">新建专家组</el-button>
           </div>
        </div>
      </template>

      <!-- Search/Filter could go here -->

      <el-table v-loading="loading" :data="groups" style="width: 100%" stripe border>
        <el-table-column prop="name" label="专家组名称" min-width="150" />
        <el-table-column label="成员数量" width="100" align="center">
          <template #default="scope">
            <el-tag>{{ scope.row.members.length }} 人</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="成员列表" min-width="300">
           <template #default="scope">
              <div class="members-tags">
                 <el-tag 
                   v-for="member in scope.row.members_info" 
                   :key="member.id" 
                   size="small" 
                   class="mr-1 mb-1"
                 >
                   {{ member.real_name }}
                 </el-tag>
              </div>
           </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
            </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="scope">
             <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
             <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Dialog -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="handleClose"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入专家组名称" />
        </el-form-item>
        
        <el-form-item label="专家成员" prop="members">
           <el-select
              v-model="form.members"
              multiple
              filterable
              placeholder="请选择专家"
              style="width: 100%"
           >
              <el-option
                v-for="expert in expertList"
                :key="expert.id"
                :label="expert.real_name + ' (' + expert.employee_id + ')'"
                :value="expert.id"
              />
           </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import request from "@/utils/request";
import dayjs from "dayjs";
import { useUserStore } from "@/stores/user";

defineOptions({
  name: "ExpertGroupsView",
});

// interfaces
interface Expert {
    id: number;
    real_name: string;
    employee_id: string;
}

interface Group {
    id: number;
    name: string;
    members: number[];
    members_info: Expert[];
    created_at: string;
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveList = <T,>(payload: unknown): T[] => {
  if (Array.isArray(payload)) return payload as T[];
  if (isRecord(payload) && Array.isArray(payload.results)) {
    return payload.results as T[];
  }
  if (
    isRecord(payload) &&
    isRecord(payload.data) &&
    Array.isArray(payload.data.results)
  ) {
    return payload.data.results as T[];
  }
  if (isRecord(payload) && Array.isArray(payload.data)) {
    return payload.data as T[];
  }
  return [];
};

const getErrorMessage = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    return error.message || fallback;
  }
  if (typeof error === "string") {
    return error || fallback;
  }
  return fallback;
};

const loading = ref(false);
const submitting = ref(false);
const groups = ref<Group[]>([]);
const expertList = ref<Expert[]>([]); // All experts
const route = useRoute();
const userStore = useUserStore();

const dialogVisible = ref(false);
const isEdit = ref(false);
const formRef = ref<FormInstance>();
const form = reactive({
    id: null as number | null,
    name: "",
    members: [] as number[],
});

const rules = reactive<FormRules>({
    name: [{ required: true, message: "请输入专家组名称", trigger: "blur" }],
    members: [{ required: true, message: "请选择专家", trigger: "change" }],
});

const dialogTitle = computed(() => isEdit.value ? "编辑专家组" : "新建专家组");
const pageTitle = computed(() => (route.meta.title as string) || "专家组管理");

const fetchGroups = async () => {
    loading.value = true;
    try {
        const res = await request.get("/reviews/groups/");
        groups.value = resolveList<Group>(res);
    } catch (error: unknown) {
        console.error(error);
        ElMessage.error("获取专家组列表失败");
    } finally {
        loading.value = false;
    }
};

const fetchExperts = async () => {
    try {
        const res = await request.get("/auth/users/", {
          params: { role: "TEACHER", is_expert: "true" },
        });
        expertList.value = resolveList<Expert>(res);
    } catch (error: unknown) {
        console.error(error);
        ElMessage.error("获取专家列表失败");
    }
};

// Actions
const handleAdd = () => {
    isEdit.value = false;
    form.id = null;
    form.name = "";
    form.members = [];
    dialogVisible.value = true;
    if (expertList.value.length === 0) fetchExperts();
};

const handleEdit = (group: Group) => {
    isEdit.value = true;
    form.id = group.id;
    form.name = group.name;
    form.members = group.members;
    dialogVisible.value = true;
    if (expertList.value.length === 0) fetchExperts();
};

const handleDelete = (group: Group) => {
    ElMessageBox.confirm(
        `确定要删除专家组 "${group.name}" 吗？`,
        "警告",
        { confirmButtonText: "删除", cancelButtonText: "取消", type: "warning" }
    ).then(async () => {
        try {
            await request.delete(`/reviews/groups/${group.id}/`);
            ElMessage.success("删除成功");
            fetchGroups();
        } catch (error) {
            console.error(error);
            ElMessage.error("删除失败");
        }
    });
};

const handleClose = () => {
    dialogVisible.value = false;
    formRef.value?.resetFields();
};

const handleSubmit = async () => {
    if (!formRef.value) return;
    await formRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true;
            try {
                if (isEdit.value && form.id) {
                    await request.put(`/reviews/groups/${form.id}/`, form);
                    ElMessage.success("更新成功");
                } else {
                    await request.post('/reviews/groups/', form);
                    ElMessage.success("创建成功");
                }
                dialogVisible.value = false;
                fetchGroups();
            } catch (error: unknown) {
                console.error(error);
                ElMessage.error(getErrorMessage(error, "操作失败"));
            } finally {
                submitting.value = false;
            }
        }
    });
};

const formatDate = (date: string) => {
    return dayjs(date).format("YYYY-MM-DD HH:mm");
};

onMounted(async () => {
    if (!userStore.user) {
        await userStore.fetchProfile();
    }
    fetchGroups();
});

</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.expert-groups-container {
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
    
.members-tags {
    display: flex;
    flex-wrap: wrap;
}
.mr-1 { margin-right: 4px; }
.mb-1 { margin-bottom: 4px; }
</style>
