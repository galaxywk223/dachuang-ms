<template>
  <div class="admin-dashboard">
    <h2 class="page-title">数据统计</h2>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409eff">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalProjects }}</div>
              <div class="stat-label">项目总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67c23a">
              <el-icon :size="30"><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.approvedProjects }}</div>
              <div class="stat-label">已通过项目</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6a23c">
              <el-icon :size="30"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingReview }}</div>
              <div class="stat-label">待审核</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f56c6c">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalUsers }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待处理事项 -->
    <el-row :gutter="20" class="content-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>待审核项目</span>
              <el-button
                text
                type="primary"
                @click="$router.push('/admin/review/establishment')"
              >
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="pendingProjects" style="width: 100%">
            <el-table-column prop="title" label="项目名称" />
            <el-table-column prop="type" label="类型" width="120" />
            <el-table-column label="状态" width="100">
              <template #default>
                <el-tag type="warning">待审核</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最新项目</span>
              <el-button
                text
                type="primary"
                @click="$router.push('/admin/projects')"
              >
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="recentProjects" style="width: 100%">
            <el-table-column prop="title" label="项目名称" />
            <el-table-column prop="leader" label="负责人" width="100" />
            <el-table-column prop="date" label="申请时间" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- 提示信息 -->
    <el-alert
      title="管理员端功能正在开发中"
      type="info"
      description="当前页面为管理员系统演示版本，更多功能敬请期待。"
      :closable="false"
      show-icon
      style="margin-top: 20px"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Document, Check, Clock, User } from "@element-plus/icons-vue";
import { getProjectStatistics } from "@/api/admin";
import { ElMessage } from "element-plus";

const stats = ref({
  totalProjects: 0,
  approvedProjects: 0,
  pendingReview: 0,
  totalUsers: 0,
});

const pendingProjects = ref([
  { title: "暂无待审核项目", type: "-", status: "-" },
]);

const recentProjects = ref([{ title: "暂无最新项目", leader: "-", date: "-" }]);

const fetchStatistics = async () => {
  try {
    const response: any = await getProjectStatistics();
    if (response.code === 200 && response.data) {
      stats.value = {
        totalProjects: response.data.total || 0,
        approvedProjects: response.data.approved || 0,
        pendingReview: response.data.pending || 0,
        totalUsers: response.data.total_users || 4,
      };
    }
  } catch (error) {
    console.error("获取统计数据失败:", error);
    ElMessage.error("获取统计数据失败");
  }
};

onMounted(() => {
  fetchStatistics();
});
</script>

<style scoped lang="scss">
.admin-dashboard {
  .page-title {
    margin: 0 0 20px 0;
    font-size: 24px;
    font-weight: 500;
    color: #303133;
  }

  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      gap: 20px;

      .stat-icon {
        width: 60px;
        height: 60px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
      }

      .stat-info {
        flex: 1;

        .stat-value {
          font-size: 28px;
          font-weight: 600;
          color: #303133;
          margin-bottom: 5px;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }
    }
  }

  .content-row {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 500;
    }
  }
}
</style>
