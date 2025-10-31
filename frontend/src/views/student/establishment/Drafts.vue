<template>
  <div class="drafts-page">
    <div class="page-header">
      <h2>草稿箱</h2>
      <p>管理未提交的项目申请草稿</p>
    </div>

    <div class="page-content">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="项目名称">
            <el-input
              v-model="filterForm.title"
              placeholder="请输入"
              clearable
              style="width: 200px"
            />
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
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="title"
          label="项目名称"
          min-width="200"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ row.title || "未命名草稿" }}
          </template>
        </el-table-column>

        <el-table-column
          prop="level_display"
          label="项目级别"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            {{ row.level_display || "-" }}
          </template>
        </el-table-column>

        <el-table-column
          prop="category_display"
          label="项目类别"
          width="150"
          align="center"
        >
          <template #default="{ row }">
            {{ row.category_display || "-" }}
          </template>
        </el-table-column>

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
        >
          <template #default="{ row }">
            {{ row.leader_name || "-" }}
          </template>
        </el-table-column>

        <el-table-column
          prop="leader_student_id"
          label="负责人学号"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            {{ row.leader_student_id || "-" }}
          </template>
        </el-table-column>

        <el-table-column prop="college" label="学院" width="120" align="center">
          <template #default="{ row }">
            {{ row.college || "-" }}
          </template>
        </el-table-column>

        <el-table-column
          prop="leader_contact"
          label="联系电话"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            {{ row.leader_contact || "-" }}
          </template>
        </el-table-column>

        <el-table-column
          prop="leader_email"
          label="邮箱"
          width="180"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ row.leader_email || "-" }}
          </template>
        </el-table-column>

        <el-table-column label="项目经费" width="100" align="center">
          <template #default="{ row }">
            {{ row.self_funding || 0 }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleEdit(row)"
            >
              继续编辑
            </el-button>
            <el-button
              type="warning"
              size="small"
              link
              @click="handleSubmit(row)"
            >
              提交
            </el-button>
            <el-button
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

      <!-- 空状态 -->
      <el-empty
        v-if="!loading && tableData.length === 0"
        description="暂无草稿数据"
        :image-size="200"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Search, RefreshLeft } from "@element-plus/icons-vue";
import {
  getMyDrafts,
  deleteProject,
  updateProjectApplication,
} from "@/api/project";
import { useRouter } from "vue-router";

const router = useRouter();

// 筛选表单
const filterForm = reactive({
  title: "",
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

// 获取草稿列表
const fetchDrafts = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };

    if (filterForm.title) {
      params.title = filterForm.title;
    }

    const response: any = await getMyDrafts(params);
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || response.data?.length || 0;
    } else {
      ElMessage.error(response.message || "获取草稿列表失败");
    }
  } catch (error: any) {
    ElMessage.error(error.message || "获取草稿列表失败");
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.page = 1;
  fetchDrafts();
};

// 重置
const handleReset = () => {
  filterForm.title = "";
  pagination.page = 1;
  fetchDrafts();
};

// 分页大小改变
const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchDrafts();
};

// 页码改变
const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchDrafts();
};

// 继续编辑
const handleEdit = (row: any) => {
  router.push(`/establishment/apply?id=${row.id}`);
};

// 提交草稿
const handleSubmit = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      "确定要提交该项目吗？提交后将进入审核流程。",
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    const submitData = {
      ...row,
      is_draft: false,
    };

    const response: any = await updateProjectApplication(row.id, submitData);
    if (response.code === 200) {
      ElMessage.success("提交成功");
      fetchDrafts();
    } else {
      ElMessage.error(response.message || "提交失败");
    }
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(error.message || "提交失败");
    }
  }
};

// 删除草稿
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定要删除该草稿吗？删除后无法恢复。", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });

    const response: any = await deleteProject(row.id);
    if (response.code === 200 || response.status === 204) {
      ElMessage.success("删除成功");
      fetchDrafts();
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
  fetchDrafts();
});
</script>

<style scoped lang="scss">
.drafts-page {
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
    min-height: 500px;

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
