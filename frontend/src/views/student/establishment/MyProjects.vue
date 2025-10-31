<template>
  <div class="my-projects-page">
    <div class="page-header">
      <h2>我的项目</h2>
      <p>查看和管理我申请的所有项目</p>
    </div>

    <div class="page-content">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="展开">
            <el-switch v-model="filterForm.expanded" />
          </el-form-item>

          <el-form-item label="项目名称">
            <el-input
              v-model="filterForm.title"
              placeholder="请输入"
              clearable
              style="width: 200px"
            />
          </el-form-item>

          <el-form-item label="项目级别">
            <el-select
              v-model="filterForm.level"
              placeholder="请选择"
              clearable
              style="width: 150px"
            >
              <el-option label="全部" value="" />
              <el-option label="国家级" value="NATIONAL" />
              <el-option label="省级" value="PROVINCIAL" />
              <el-option label="校级" value="SCHOOL" />
            </el-select>
          </el-form-item>

          <el-form-item label="项目类别">
            <el-select
              v-model="filterForm.category"
              placeholder="请选择"
              clearable
              style="width: 180px"
            >
              <el-option label="全部" value="" />
              <el-option label="创新训练项目" value="INNOVATION_TRAINING" />
              <el-option
                label="创业训练项目"
                value="ENTREPRENEURSHIP_TRAINING"
              />
              <el-option
                label="创业实践项目"
                value="ENTREPRENEURSHIP_PRACTICE"
              />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 表格区域 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
      >
        <el-table-column type="expand" width="50">
          <template #default="{ row }">
            <div class="expand-content">
              <p><strong>项目简介：</strong>{{ row.description || "暂无" }}</p>
              <p>
                <strong>立项类别描述：</strong
                >{{ row.category_description || "暂无" }}
              </p>
              <p><strong>审核状态：</strong>{{ row.status_display }}</p>
              <p v-if="row.created_at">
                <strong>创建时间：</strong>{{ formatDate(row.created_at) }}
              </p>
              <p v-if="row.submitted_at">
                <strong>提交时间：</strong>{{ formatDate(row.submitted_at) }}
              </p>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="title"
          label="项目名称"
          min-width="200"
          show-overflow-tooltip
        />

        <el-table-column
          prop="level_display"
          label="项目级别"
          width="100"
          align="center"
        />

        <el-table-column
          prop="category_display"
          label="项目类别"
          width="150"
          align="center"
        />

        <el-table-column label="是否重点领域项目" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_key_field ? 'success' : 'info'" size="small">
              {{ row.is_key_field ? "是" : "否" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="重点领域项目代码" width="150" align="center">
          <template #default="{ row }">
            {{ row.major_code || "-" }}
          </template>
        </el-table-column>

        <el-table-column
          prop="leader_name"
          label="负责人姓名"
          width="120"
          align="center"
        />

        <el-table-column
          prop="leader_student_id"
          label="负责人学号"
          width="120"
          align="center"
        />

        <el-table-column
          prop="college"
          label="学院"
          width="120"
          align="center"
        />

        <el-table-column
          prop="leader_contact"
          label="联系电话"
          width="120"
          align="center"
        />

        <el-table-column
          prop="leader_email"
          label="邮箱"
          width="180"
          show-overflow-tooltip
        />

        <el-table-column label="项目经费" width="100" align="center">
          <template #default="{ row }">
            {{ row.self_funding || 0 }}
          </template>
        </el-table-column>

        <el-table-column label="审核节点" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              v-if="row.status === 'DRAFT'"
              type="warning"
              size="small"
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'DRAFT'"
              type="danger"
              size="small"
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, RefreshLeft } from "@element-plus/icons-vue";
import { getMyProjects, deleteProject } from "@/api/project";
import { useRouter } from "vue-router";

const router = useRouter();

// 筛选表单
const filterForm = reactive({
  expanded: false,
  title: "",
  level: "",
  category: "",
});

// 表格数据
const tableData = ref<any[]>([]);
const loading = ref(false);

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

// 获取项目列表
const fetchProjects = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };

    if (filterForm.title) {
      params.title = filterForm.title;
    }
    if (filterForm.level) {
      params.level = filterForm.level;
    }
    if (filterForm.category) {
      params.category = filterForm.category;
    }

    const response: any = await getMyProjects(params);
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || response.data?.length || 0;
    } else {
      ElMessage.error(response.message || "获取项目列表失败");
    }
  } catch (error: any) {
    ElMessage.error(error.message || "获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return "-";
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hours = String(d.getHours()).padStart(2, "0");
  const minutes = String(d.getMinutes()).padStart(2, "0");
  const seconds = String(d.getSeconds()).padStart(2, "0");
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};

// 搜索
const handleSearch = () => {
  pagination.page = 1;
  fetchProjects();
};

// 重置
const handleReset = () => {
  filterForm.title = "";
  filterForm.level = "";
  filterForm.category = "";
  pagination.page = 1;
  fetchProjects();
};

// 分页大小改变
const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchProjects();
};

// 页码改变
const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchProjects();
};

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    DRAFT: "info",
    SUBMITTED: "warning",
    LEVEL2_REVIEWING: "warning",
    LEVEL2_APPROVED: "success",
    LEVEL2_REJECTED: "danger",
    LEVEL1_REVIEWING: "warning",
    LEVEL1_APPROVED: "success",
    LEVEL1_REJECTED: "danger",
    IN_PROGRESS: "primary",
    COMPLETED: "success",
  };
  return typeMap[status] || "info";
};

// 查看详情
const handleView = (row: any) => {
  // TODO: 跳转到项目详情页
  ElMessage.info("查看项目详情功能待开发");
};

// 编辑项目
const handleEdit = (row: any) => {
  // TODO: 跳转到编辑页面
  router.push(`/establishment/apply?id=${row.id}`);
};

// 删除项目
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定要删除该项目吗？删除后无法恢复。", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    const response: any = await deleteProject(row.id);
    if (response.code === 200 || response.status === 204) {
      ElMessage.success("删除成功");
      fetchProjects();
    } else {
      ElMessage.error(response.message || "删除失败");
    }
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(error.message || "删除失败");
    }
  }
};

// 页面加载时获取数据
onMounted(() => {
  fetchProjects();
});
</script>

<style scoped lang="scss">
.my-projects-page {
  .page-header {
    background: #ffffff;
    padding: 24px;
    border-radius: 8px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

    h2 {
      margin: 0 0 8px 0;
      font-size: 24px;
      color: #262626;
    }

    p {
      margin: 0;
      color: #8c8c8c;
      font-size: 14px;
    }
  }

  .page-content {
    background: #ffffff;
    padding: 24px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

    .filter-section {
      margin-bottom: 20px;
      padding: 16px;
      background: #fafafa;
      border-radius: 4px;

      .filter-form {
        margin-bottom: 0;

        :deep(.el-form-item) {
          margin-bottom: 0;
        }
      }
    }

    .expand-content {
      padding: 16px;
      background: #fafafa;

      p {
        margin: 8px 0;
        line-height: 1.6;
        color: #606266;

        strong {
          color: #303133;
          margin-right: 8px;
        }
      }
    }

    .pagination-container {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }
}
</style>
