import { ref, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import request from "@/utils/request";

export interface ExpertGroup {
  id: number;
  name: string;
  description: string;
  scope: "SCHOOL" | "COLLEGE";
  college?: string;
  experts: number[];
  created_at: string;
  updated_at: string;
}

export interface Expert {
  id: number;
  real_name: string;
  employee_id: string;
  college: string;
  title: string;
  expert_scope: string;
}

/**
 * 使用专家组管理
 * @param scope 专家组范围：SCHOOL（校级）或 COLLEGE（院级）
 * @param reviewLevel 评审级别：LEVEL1（校级）或 LEVEL2（院级）
 */
export function useExpertGroups(scope: "SCHOOL" | "COLLEGE") {
  const groups = ref<ExpertGroup[]>([]);
  const experts = ref<Expert[]>([]);
  const loading = ref(false);
  const dialogVisible = ref(false);
  const isEditMode = ref(false);
  const currentGroup = ref<ExpertGroup | null>(null);

  const formData = ref({
    name: "",
    description: "",
    experts: [] as number[],
  });

  /**
   * 加载专家组列表
   */
  const loadGroups = async () => {
    loading.value = true;
    try {
      const response = await request.get("/reviews/groups/", {
        params: { scope },
      });
      groups.value = response.data?.results || response.data || [];
    } catch (error) {
      console.error("Failed to load expert groups:", error);
      ElMessage.error("加载专家组列表失败");
    } finally {
      loading.value = false;
    }
  };

  /**
   * 加载专家列表
   */
  const loadExperts = async () => {
    try {
      const expertScope = scope === "SCHOOL" ? "SCHOOL" : "COLLEGE";
      const response = await request.get("/auth/admin/users/", {
        params: {
          role: "EXPERT",
          expert_scope: expertScope,
          page_size: 1000,
        },
      });
      experts.value = response.data?.results || [];
    } catch (error) {
      console.error("Failed to load experts:", error);
      ElMessage.error("加载专家列表失败");
    }
  };

  /**
   * 打开新建对话框
   */
  const openCreateDialog = () => {
    isEditMode.value = false;
    currentGroup.value = null;
    formData.value = {
      name: "",
      description: "",
      experts: [],
    };
    dialogVisible.value = true;
  };

  /**
   * 打开编辑对话框
   */
  const openEditDialog = (group: ExpertGroup) => {
    isEditMode.value = true;
    currentGroup.value = group;
    formData.value = {
      name: group.name,
      description: group.description,
      experts: [...group.experts],
    };
    dialogVisible.value = true;
  };

  /**
   * 提交表单
   */
  const submitForm = async () => {
    if (!formData.value.name) {
      ElMessage.warning("请输入专家组名称");
      return;
    }

    loading.value = true;
    try {
      const payload = {
        ...formData.value,
        scope,
      };

      if (isEditMode.value && currentGroup.value) {
        await request.put(`/reviews/groups/${currentGroup.value.id}/`, payload);
        ElMessage.success("更新成功");
      } else {
        await request.post("/reviews/groups/", payload);
        ElMessage.success("创建成功");
      }

      dialogVisible.value = false;
      await loadGroups();
    } catch (error: unknown) {
      console.error("Failed to submit form:", error);
      ElMessage.error(error instanceof Error ? error.message : "操作失败");
    } finally {
      loading.value = false;
    }
  };

  /**
   * 删除专家组
   */
  const deleteGroup = async (group: ExpertGroup) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除专家组"${group.name}"吗？`,
        "删除确认",
        {
          confirmButtonText: "确定",
          cancelButtonText: "取消",
          type: "warning",
        }
      );

      await request.delete(`/reviews/groups/${group.id}/`);
      ElMessage.success("删除成功");
      await loadGroups();
    } catch (error: unknown) {
      if (error !== "cancel") {
        console.error("Failed to delete group:", error);
        ElMessage.error("删除失败");
      }
    }
  };

  onMounted(() => {
    loadGroups();
    loadExperts();
  });

  return {
    groups,
    experts,
    loading,
    dialogVisible,
    isEditMode,
    formData,
    loadGroups,
    loadExperts,
    openCreateDialog,
    openEditDialog,
    submitForm,
    deleteGroup,
  };
}
