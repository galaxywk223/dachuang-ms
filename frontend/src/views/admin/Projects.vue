<template>
  <div class="projects-page">
    <div class="page-header">
      <h2>项目管理</h2>
      <div class="filter-bar">
        <el-input
          v-model="filters.search"
          placeholder="搜索项目名称"
          style="width: 200px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select
          v-model="filters.level"
          placeholder="项目级别"
          clearable
          style="width: 150px"
        >
          <el-option
            v-for="item in levelOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-select
          v-model="filters.category"
          placeholder="项目类别"
          clearable
          style="width: 150px"
        >
          <el-option
            v-for="item in categoryOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-select
          v-model="filters.status"
          placeholder="项目状态"
          clearable
          style="width: 150px"
        >
          <el-option
            v-for="item in statusOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="projects" style="width: 100%">
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="project_no" label="项目编号" width="120" />
      <el-table-column
        prop="title"
        label="项目名称"
        min-width="200"
        show-overflow-tooltip
      />
      <el-table-column prop="category_display" label="类别" width="120" />
      <el-table-column prop="level_display" label="级别" width="100" />
      <el-table-column prop="leader_name" label="负责人" width="100" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{
            row.status_display
          }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="申请时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click="handleView(row)">
            查看
          </el-button>
          <el-button text type="warning" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button text type="danger" size="small" @click="handleDelete(row)">
            删除
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";

const { loadDictionaries, getOptions } = useDictionary();

const loading = ref(false);
const projects = ref<any[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const filters = reactive({
  search: "",
  level: "",
  category: "",
  status: "",
});

// 从字典获取下拉选项
const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
const statusOptions = computed(() => getOptions(DICT_CODES.PROJECT_STATUS));

const fetchProjects = async () => {
  loading.value = true;
  try {
    // TODO: 调用后端API
    // const response = await getAllProjects({
    //   page: currentPage.value,
    //   page_size: pageSize.value,
    //   ...filters,
    // });

    // 模拟数据
    projects.value = [
      {
        id: 1,
        project_no: "2024001",
        title: "基于人工智能的智能问答系统",
        category_display: "创新训练",
        level_display: "国家级",
        leader_name: "张三",
        status: "IN_PROGRESS",
        status_display: "进行中",
        created_at: "2024-10-15 10:30:00",
      },
      {
        id: 2,
        project_no: "2024002",
        title: "校园共享单车管理系统",
        category_display: "创业训练",
        level_display: "省级",
        leader_name: "李四",
        status: "SUBMITTED",
        status_display: "待审核",
        created_at: "2024-10-20 14:20:00",
      },
      {
        id: 3,
        project_no: "2024003",
        title: "智慧农业物联网平台",
        category_display: "创新训练",
        level_display: "校级",
        leader_name: "王五",
        status: "COMPLETED",
        status_display: "已完成",
        created_at: "2024-09-10 09:00:00",
      },
    ];
    total.value = 3;
  } catch (error) {
    ElMessage.error("获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    DRAFT: "info",
    SUBMITTED: "warning",
    IN_PROGRESS: "primary",
    COMPLETED: "success",
    CLOSED: "danger",
  };
  return typeMap[status] || "info";
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchProjects();
};

const handleReset = () => {
  filters.search = "";
  filters.level = "";
  filters.category = "";
  filters.status = "";
  currentPage.value = 1;
  fetchProjects();
};

const handlePageChange = () => {
  fetchProjects();
};

const handleSizeChange = () => {
  currentPage.value = 1;
  fetchProjects();
};

const handleView = (row: any) => {
  ElMessage.info(`查看项目: ${row.title}`);
};

const handleEdit = (row: any) => {
  ElMessage.info(`编辑项目: ${row.title}`);
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${row.title}"吗？此操作不可恢复！`,
      "警告",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    // TODO: 调用删除API
    ElMessage.success("删除成功");
    fetchProjects();
  } catch {
    // 用户取消
  }
};

onMounted(async () => {
  // 加载需要的字典数据
  await loadDictionaries([
    DICT_CODES.PROJECT_LEVEL,
    DICT_CODES.PROJECT_CATEGORY,
    DICT_CODES.PROJECT_STATUS,
  ]);
  fetchProjects();
});
</script>

<style scoped lang="scss">
.projects-page {
  .page-header {
    margin-bottom: 20px;

    h2 {
      margin: 0 0 15px 0;
      font-size: 20px;
      font-weight: 500;
    }

    .filter-bar {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
