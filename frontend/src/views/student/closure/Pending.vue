<template>
  <div class="pending-page">


    <div class="page-content">
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
              <p><strong>立项时间：</strong>{{ formatDate(row.start_date) }}</p>
              <p><strong>项目状态：</strong>{{ row.status_display }}</p>
            </div>
          </template>
        </el-table-column>

        <el-table-column
          prop="project_no"
          label="立项年份"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            {{ getProjectYear(row.project_no) }}
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

        <el-table-column label="项目经费" width="100" align="center">
          <template #default="{ row }">
            {{ row.budget || 0 }}
          </template>
        </el-table-column>

        <el-table-column label="审核节点" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleApplyClosure(row)"
            >
              申请结题
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
        description="暂无待结题项目"
        :image-size="200"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import { getPendingClosureProjects } from "@/api/project";

const router = useRouter();

// 表格数据
const tableData = ref<any[]>([]);
const loading = ref(false);

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return "-";
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

// 获取项目年份
const getProjectYear = (projectNo: string) => {
  if (!projectNo) return "-";
  // 假设项目编号格式为 DC20240001，提取年份
  const match = projectNo.match(/DC(\d{4})/);
  return match ? match[1] : "-";
};

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    IN_PROGRESS: "primary",
    COMPLETED: "success",
  };
  return typeMap[status] || "info";
};

// 获取待结题项目列表
const fetchPendingProjects = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };

    const response: any = await getPendingClosureProjects(params);
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || 0;
    } else {
      ElMessage.error(response.message || "获取项目列表失败");
    }
  } catch (error: any) {
    console.error("获取待结题项目失败:", error);
    ElMessage.error(error.message || "获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

// 分页大小改变
const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchPendingProjects();
};

// 页码改变
const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchPendingProjects();
};

// 申请结题
const handleApplyClosure = (row: any) => {
  // 跳转到结题申请页面或打开对话框
  router.push(`/closure/apply?projectId=${row.id}`);
  ElMessage.info("跳转到结题申请页面");
};

// 页面加载时获取数据
onMounted(() => {
  fetchPendingProjects();
});
</script>

<style scoped lang="scss">
.pending-page {
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
