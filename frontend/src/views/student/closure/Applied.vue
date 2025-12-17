<template>
  <div class="applied-page">


    <div class="page-content">
      <!-- 表格区域 -->
      <div class="status-tabs-wrapper">
           <div class="table-header-title">
              <span class="title-text">已申请结题项目</span>
              <el-tag type="info" size="small" effect="plain" round class="count-tag">{{ pagination.total }}</el-tag>
           </div>
      </div>

      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
        :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
      >
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

        <el-table-column label="指导教师" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.advisors_info && row.advisors_info.length > 0">
              {{ row.advisors_info[0].name }}
              <span v-if="row.advisors_info.length > 1"
                >等{{ row.advisors_info.length }}人</span
              >
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="成果形式" width="150" align="center">
          <template #default="{ row }">
            {{ getAchievementTypes(row) || "-" }}
          </template>
        </el-table-column>

        <el-table-column label="成果简介" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.achievement_summary || "-" }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleView(row)"
            >
              查看详情
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
        description="暂无已申请结题项目"
        :image-size="200"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { getAppliedClosureProjects } from "@/api/project";

// 表格数据
const tableData = ref<any[]>([]);
const loading = ref(false);

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

// 获取项目年份
const getProjectYear = (projectNo: string) => {
  if (!projectNo) return "-";
  const match = projectNo.match(/DC(\d{4})/);
  return match ? match[1] : "-";
};

// 获取成果形式
const getAchievementTypes = (row: any) => {
  // 根据项目的成果信息拼接成果形式
  if (row.achievements && row.achievements.length > 0) {
    const types = row.achievements.map((a: any) => a.achievement_type_display);
    return Array.from(new Set(types)).join("、");
  }
  return "";
};

// 获取已申请结题项目列表
const fetchAppliedProjects = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };

    const response: any = await getAppliedClosureProjects(params);
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || 0;
    } else {
      ElMessage.error(response.message || "获取项目列表失败");
    }
  } catch (error: any) {
    console.error("获取已申请结题项目失败:", error);
    ElMessage.error(error.message || "获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

// 分页大小改变
const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchAppliedProjects();
};

// 页码改变
const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchAppliedProjects();
};

// 查看详情
const handleView = (_row: any) => {
  ElMessage.info("查看结题详情功能待开发");
};

// 页面加载时获取数据
onMounted(() => {
  fetchAppliedProjects();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.applied-page {
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

    .pagination-container {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }
}

.status-tabs-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid $slate-100;
  margin-bottom: 16px;
}

.table-header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .title-text {
      font-size: 16px;
      font-weight: 600;
      color: $slate-800;
      position: relative;
      padding-left: 14px;
      
      &::before {
          content: '';
          position: absolute;
          left: 0;
          top: 50%;
          transform: translateY(-50%);
          width: 4px;
          height: 16px;
          background: $primary-600;
          border-radius: 2px;
      }
  }
}

.count-tag {
    font-weight: normal;
    color: $slate-500;
}
</style>
