import { computed, reactive, ref } from "vue";
import { ElMessage } from "element-plus";

import { getUsers, toggleExpertStatus } from "@/api/users/admin";
import { DICT_CODES } from "@/api/dictionaries";
import { useDictionary } from "@/composables/useDictionary";

type ExpertRow = {
  id: number;
  employee_id: string;
  real_name: string;
  phone?: string;
  email?: string;
  college?: string;
  title?: string;
  is_expert?: boolean;
  is_active?: boolean;
};

type UserListResponse = {
  code?: number;
  data?: {
    results?: ExpertRow[];
    count?: number;
    total?: number;
  };
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    return error.message || fallback;
  }
  if (typeof error === "string") {
    return error || fallback;
  }
  return fallback;
};

const expertStatusOptions = [
  { value: "", label: "全部" },
  { value: "true", label: "是" },
  { value: "false", label: "否" },
];

export function useExpertManagement() {
  const loading = ref(false);
  const tableData = ref<ExpertRow[]>([]);
  const total = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(10);

  const { loadDictionaries, getOptions, getLabel } = useDictionary();
  const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));

  const filters = reactive({
    search: "",
    college: "",
    is_expert: "",
    role: "TEACHER",
  });

  const loadData = async () => {
    loading.value = true;
    try {
      const params: Record<string, string | number> = {
        page: currentPage.value,
        page_size: pageSize.value,
        role: filters.role,
      };
      if (filters.search) params.search = filters.search;
      if (filters.college) params.college = filters.college;
      if (filters.is_expert) params.is_expert = filters.is_expert;

      const res = (await getUsers(params)) as UserListResponse;
      if (isRecord(res) && res.code === 200 && res.data) {
        tableData.value = res.data.results ?? [];
        const resultCount = res.data.count ?? res.data.total ?? tableData.value.length;
        total.value = Number.isFinite(resultCount) ? resultCount : 0;
      } else {
        tableData.value = [];
        total.value = 0;
      }
    } catch (error) {
      console.error(error);
      ElMessage.error("获取数据失败");
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
    filters.college = "";
    filters.is_expert = "";
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

  const handleToggleExpert = async (row: ExpertRow, value: string | number | boolean) => {
    const nextValue = Boolean(value);
    const previousValue = row.is_expert;
    row.is_expert = nextValue;
    try {
      const res = await toggleExpertStatus(row.id, nextValue);
      if (isRecord(res) && res.code === 200) {
        ElMessage.success("专家资格已更新");
        return;
      }
      throw new Error("操作失败");
    } catch (error) {
      row.is_expert = previousValue;
      ElMessage.error(getErrorMessage(error, "更新失败"));
    }
  };

  return {
    loading,
    tableData,
    total,
    currentPage,
    pageSize,
    filters,
    collegeOptions,
    expertStatusOptions,
    loadDictionaries,
    getLabel,
    loadData,
    handleSearch,
    resetFilters,
    handleSizeChange,
    handleCurrentChange,
    handleToggleExpert,
  };
}
