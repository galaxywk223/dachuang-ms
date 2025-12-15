<template>
  <div class="admin-dashboard">
    <div class="page-header">
       <h2 class="page-title">数据统计</h2>
       <span class="subtitle">系统运行概览</span>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon bg-primary">
              <el-icon :size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalProjects }}</div>
              <div class="stat-label">项目总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon bg-success">
              <el-icon :size="24"><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.approvedProjects }}</div>
              <div class="stat-label">已通过</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon bg-warning">
              <el-icon :size="24"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingReview }}</div>
              <div class="stat-label">待审核</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon bg-danger">
              <el-icon :size="24"><User /></el-icon>
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
    <el-row :gutter="24" class="content-row">
      <el-col :span="12">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-title">
                 <span>待审核项目</span>
                 <el-tag type="danger" size="small" effect="dark" round v-if="pendingProjects.length > 0">{{ pendingProjects.length }}</el-tag>
              </div>
              <el-button
                link
                type="primary"
                @click="$router.push('/admin/review/establishment')"
              >
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="pendingProjects" style="width: 100%" class="modern-table" :show-header="false">
            <el-table-column prop="title" label="项目名称">
               <template #default="{ row }">
                 <span class="font-medium text-slate-800">{{ row.title }}</span>
               </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="120" align="right">
               <template #default="{ row }">
                 <span class="text-slate-500">{{ row.type }}</span>
               </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="right">
              <template #default>
                <el-tag type="warning" size="small" effect="light">待审核</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="header-title"><span>最新项目</span></div>
              <el-button
                link
                type="primary"
                @click="$router.push('/admin/projects')"
              >
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="recentProjects" style="width: 100%" class="modern-table" :show-header="false">
            <el-table-column prop="title" label="项目名称">
               <template #default="{ row }">
                 <span class="font-medium text-slate-800">{{ row.title }}</span>
               </template>
            </el-table-column>
            <el-table-column prop="leader" label="负责人" width="100" align="right">
                <template #default="{ row }">
                 <span class="text-slate-600">{{ row.leader }}</span>
               </template>
            </el-table-column>
            <el-table-column prop="date" label="申请时间" width="120" align="right">
                <template #default="{ row }">
                 <span class="text-slate-400 text-xs">{{ row.date }}</span>
               </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Document, Check, Clock, User } from "@element-plus/icons-vue";


// State
const stats = ref({
  totalProjects: 0,
  approvedProjects: 0,
  pendingReview: 0,
  totalUsers: 0,
});
const pendingProjects = ref([]);
const recentProjects = ref([]);

import { getProjectStatistics, getReviewProjects, getAllProjects } from "@/api/admin";
import { getUserStatistics } from "@/api/user-admin";

// Fetch Data
const fetchData = async () => {
    try {
        // 1. Stats
        const statsRes: any = await getProjectStatistics();
        const userStatsRes: any = await getUserStatistics();
        if (statsRes.data) {
            stats.value.totalProjects = statsRes.data.total_projects || 0;
            stats.value.approvedProjects = statsRes.data.approved_projects || 0;
            stats.value.pendingReview = statsRes.data.pending_review || 0;
        }
        if (userStatsRes.data) {
            stats.value.totalUsers = userStatsRes.data.total_users || 0;
        }

        // 2. Pending Projects (Review)
        const pendingRes: any = await getReviewProjects({ page: 1, page_size: 5 });
        if (pendingRes.data && pendingRes.data.results) {
             pendingProjects.value = pendingRes.data.results.map((p: any) => ({
                 title: p.title,
                 type: p.category_display || p.category,
                 status: 'PENDING'
             }));
        }

        // 3. Recent Projects (Manage)
        // Backend sorts by -created_at by default
        const recentRes: any = await getAllProjects({ page: 1, page_size: 5 });
        if (recentRes.data && recentRes.data.results) {
            recentProjects.value = recentRes.data.results.map((p: any) => ({
                title: p.title,
                leader: p.leader_name || "未知",
                date: p.created_at ? p.created_at.split('T')[0] : ""
            }));
        }

    } catch (e) {
        console.error("Failed to load dashboard data", e);
    }
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;
@use "sass:color";

.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  .page-title {
    margin: 0;
    font-size: $font-size-2xl;
    font-weight: 700;
    color: $slate-900;
    display: inline-block;
    margin-right: 12px;
  }
  .subtitle {
    color: $slate-500;
  }
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border: none;
  border-radius: $radius-lg;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-2px);
  }

  :deep(.el-card__body) {
    padding: 24px;
  }

  .stat-content {
    display: flex;
    align-items: center;
    gap: 20px;

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: $shadow-sm;
      
      &.bg-primary { background: linear-gradient(135deg, $primary-500, $primary-600); }
      &.bg-success { background: linear-gradient(135deg, $success, color.adjust($success, $lightness: -5%)); }
      &.bg-warning { background: linear-gradient(135deg, $warning, color.adjust($warning, $lightness: -5%)); }
      &.bg-danger  { background: linear-gradient(135deg, $danger, color.adjust($danger, $lightness: -5%)); }
    }

    .stat-info {
      flex: 1;

      .stat-value {
        font-size: 2rem; // Big number
        font-weight: 700;
        color: $slate-900;
        line-height: 1.2;
      }

      .stat-label {
        font-size: $font-size-sm;
        color: $slate-500;
        margin-top: 4px;
      }
    }
  }
}

.panel-card {
  border: none;
  border-radius: $radius-lg;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .header-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        color: $slate-800;
    }
  }
}

.modern-table {
  :deep(.el-table__row) {
    td {
      padding: 16px 0;
    }
  }
}

.font-medium { font-weight: 500; }
.text-slate-800 { color: $slate-800; }
.text-slate-600 { color: $slate-600; }
.text-slate-500 { color: $slate-500; }
.text-slate-400 { color: $slate-400; }
.text-xs { font-size: $font-size-xs; }
</style>
