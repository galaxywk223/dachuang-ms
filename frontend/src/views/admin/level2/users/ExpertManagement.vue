<template>
  <div>
    <div class="page-container">
      <el-card class="main-card" shadow="never">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <span class="header-title">院级专家库管理</span>
              <el-tag type="info" size="small" effect="plain" round class="ml-2">
                共 {{ total }} 项
              </el-tag>
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
                style="width: 200px"
              >
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-form-item>

            <el-form-item label="学院">
              <el-select
                v-model="filters.college"
                placeholder="本院"
                disabled
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

            <el-form-item label="专家">
              <el-select v-model="filters.is_expert" placeholder="全部" style="width: 160px">
                <el-option
                  v-for="item in expertStatusOptions"
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

        <el-table v-loading="loading" :data="tableData" style="width: 100%" stripe border>
          <el-table-column prop="employee_id" label="工号" width="120" sortable />
          <el-table-column prop="real_name" label="姓名" width="120" />
          <el-table-column prop="title" label="职称" width="120">
            <template #default="{ row }">
              {{ getLabel(DICT_CODES.ADVISOR_TITLE, row.title) }}
            </template>
          </el-table-column>
          <el-table-column prop="is_expert" label="专家" width="120">
            <template #default="{ row }">
              <el-switch
                :model-value="row.is_expert"
                @change="(value) => handleToggleExpert(row, value)"
              />
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
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { Search } from "@element-plus/icons-vue";
import { getUsers, toggleExpertStatus } from "@/api/users/admin";
import { ElMessage } from "element-plus";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";
import { useUserStore } from "@/stores/user";

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

type ExpertFilters = {
  search: string;
  college: string;
  is_expert: string;
  role: string;
};

type ApiListResponse = {
  code: number;
  data?: {
    results?: ExpertRow[];
    count?: number;
    total?: number;
  };
  message?: string;
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

const userStore = useUserStore();
const loading = ref(false);
const tableData = ref<ExpertRow[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const { loadDictionaries, getOptions, getLabel } = useDictionary();

const currentCollege = computed(() => userStore.user?.college || '');

const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
const expertStatusOptions = [
  { value: "", label: "全部" },
  { value: "true", label: "是" },
  { value: "false", label: "否" },
];

const filters = reactive<ExpertFilters>({
  search: "",
  college: "",
  is_expert: "",
  role: "TEACHER",
});

const syncCollege = () => {
  filters.college = currentCollege.value || "";
};

const loadData = async () => {
  loading.value = true;
  try {
    const params: Record<string, string | number> = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: filters.search,
      college: filters.college,
      is_expert: filters.is_expert,
      role: filters.role,
    };
    if (!filters.search) delete params.search;
    if (!filters.college) delete params.college;
    if (!filters.is_expert) delete params.is_expert;

    const res = (await getUsers(params)) as ApiListResponse;
    if (isRecord(res) && res.code === 200 && res.data) {
      tableData.value = res.data.results || [];
      const resultCount =
        res.data.count ?? res.data.total ?? tableData.value.length;
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
  syncCollege();
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

onMounted(async () => {
  if (!userStore.user) {
    await userStore.fetchProfile();
  }
  loadDictionaries([DICT_CODES.COLLEGE, DICT_CODES.ADVISOR_TITLE]);
  syncCollege();
  loadData();
});
</script>

<style scoped lang="scss" src="../../level1/users/TeacherManagement.scss"></style>
