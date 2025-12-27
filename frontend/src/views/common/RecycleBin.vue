<template>
  <div class="recycle-bin-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">回收站</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" plain @click="fetchItems">刷新</el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" class="filter-bar">
        <el-form-item label="项目">
          <el-select
            v-model="filters.project"
            placeholder="全部项目"
            clearable
            filterable
            style="width: 240px"
          >
            <el-option
              v-for="item in projects"
              :key="item.id"
              :label="`${item.project_no || ''} ${item.title}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="filters.resource_type" placeholder="全部" clearable style="width: 200px">
            <el-option v-for="item in resourceTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.is_restored" placeholder="全部" clearable style="width: 160px">
            <el-option label="未恢复" value="false" />
            <el-option label="已恢复" value="true" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table
        v-loading="loading"
        :data="items"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="project_no" label="项目编号" width="160" />
        <el-table-column prop="project_title" label="项目名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="resource_type_display" label="资源类型" width="140" />
        <el-table-column prop="deleted_at" label="删除时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.deleted_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_restored" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_restored ? 'success' : 'warning'" size="small">
              {{ row.is_restored ? '已恢复' : '待恢复' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="附件" min-width="180">
          <template #default="{ row }">
            <div v-if="(row.attachments || []).length">
              <div v-for="(file, index) in row.attachments" :key="index" class="file-item">
                {{ typeof file === 'string' ? file : file.name || '-' }}
              </div>
            </div>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_restored"
              type="primary"
              link
              size="small"
              @click="handleRestore(row)"
            >
              恢复
            </el-button>
            <span v-else class="text-gray-400">-</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
          size="small"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import dayjs from "dayjs";
import { getRecycleBin, restoreRecycleBin, getProjects } from "@/api/projects";

const loading = ref(false);
const items = ref<any[]>([]);
const projects = ref<any[]>([]);

const filters = reactive({
  project: "",
  resource_type: "",
  is_restored: "",
});

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const resourceTypeOptions = [
  { label: "立项申报", value: "APPLICATION" },
  { label: "中期提交", value: "MID_TERM" },
  { label: "结题提交", value: "CLOSURE" },
  { label: "成果", value: "ACHIEVEMENT" },
  { label: "经费支出", value: "EXPENDITURE" },
  { label: "进度记录", value: "PROGRESS" },
];

const formatDate = (value?: string) => {
  if (!value) return "-";
  return dayjs(value).format("YYYY-MM-DD HH:mm");
};

const fetchProjects = async () => {
  try {
    const res: any = await getProjects({ page_size: 200 });
    projects.value = res?.data?.results || res?.data || res || [];
  } catch (error) {
    console.error(error);
  }
};

const fetchItems = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };
    if (filters.project) params.project = filters.project;
    if (filters.resource_type) params.resource_type = filters.resource_type;
    if (filters.is_restored !== "") params.is_restored = filters.is_restored;

    const res: any = await getRecycleBin(params);
    const payload = res?.data || res;
    items.value = payload?.results || payload?.data?.results || payload?.data || [];
    pagination.total =
      payload?.count || payload?.data?.count || payload?.total || payload?.data?.total || 0;
  } catch (error: any) {
    ElMessage.error(error.message || "获取回收站失败");
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  pagination.page = 1;
  fetchItems();
};

const handleReset = () => {
  filters.project = "";
  filters.resource_type = "";
  filters.is_restored = "";
  handleSearch();
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.page = 1;
  fetchItems();
};

const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchItems();
};

const handleRestore = async (row: any) => {
  try {
    await ElMessageBox.confirm("确认恢复该记录吗？", "提示", { type: "warning" });
    const res: any = await restoreRecycleBin(row.id);
    if (res?.code === 200) {
      ElMessage.success("恢复成功");
      fetchItems();
    } else {
      ElMessage.error(res?.message || "恢复失败");
    }
  } catch (error) {
    // cancel
  }
};

onMounted(async () => {
  await fetchProjects();
  fetchItems();
});
</script>

<style scoped lang="scss">
.recycle-bin-page {
  .filter-bar {
    margin-bottom: 16px;
  }
  .file-item {
    font-size: 12px;
    color: #64748b;
  }
}
</style>
