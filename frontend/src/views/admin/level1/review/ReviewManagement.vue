<template>
  <div class="review-management">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="header-title">审核管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane name="establishment">
          <template #label>
            <el-badge
              :value="counts.establishment"
              :hidden="counts.establishment === 0"
            >
              立项审核
            </el-badge>
          </template>
          <EstablishmentReview
            v-if="activeTab === 'establishment'"
            @review-completed="loadCounts"
          />
        </el-tab-pane>

        <el-tab-pane name="closure">
          <template #label>
            <el-badge :value="counts.closure" :hidden="counts.closure === 0">
              结题审核
            </el-badge>
          </template>
          <ClosureReview
            v-if="activeTab === 'closure'"
            @review-completed="loadCounts"
          />
        </el-tab-pane>

        <el-tab-pane name="change">
          <template #label>
            <el-badge :value="counts.change" :hidden="counts.change === 0">
              异动审核
            </el-badge>
          </template>
          <ChangeReview
            v-if="activeTab === 'change'"
            @review-completed="loadCounts"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useReviewCounts } from "@/composables/useReviewCounts";
import EstablishmentReview from "./Establishment.vue";
import ClosureReview from "./Closure.vue";
import ChangeReview from "../change/Reviews.vue";

const route = useRoute();
const router = useRouter();

// 当前激活的Tab
const activeTab = ref<string>("establishment");

// 使用待审核数量composable
const { counts, loadCounts } = useReviewCounts();

// 处理Tab切换
const handleTabChange = (tabName: string | number) => {
  const tab = String(tabName);
  activeTab.value = tab;

  // 更新URL query参数，保持书签和分享链接可用
  router.push({
    query: { ...route.query, tab },
  });
};

// 从URL query参数初始化Tab
onMounted(() => {
  const tabFromQuery = route.query.tab as string;
  if (
    tabFromQuery &&
    ["establishment", "closure", "change"].includes(tabFromQuery)
  ) {
    activeTab.value = tabFromQuery;
  }
});

// 监听路由变化
watch(
  () => route.query.tab,
  (newTab) => {
    if (newTab && typeof newTab === "string" && activeTab.value !== newTab) {
      activeTab.value = newTab;
    }
  }
);
</script>

<style scoped lang="scss">
.review-management {
  padding: 20px;

  .main-card {
    min-height: calc(100vh - 140px);

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
  }

  :deep(.el-tabs) {
    .el-tabs__header {
      margin-bottom: 20px;
    }

    .el-tabs__item {
      font-size: 15px;
      padding: 0 30px;
      height: 50px;
      line-height: 50px;
    }

    .el-badge {
      .el-badge__content {
        transform: translateY(-50%) translateX(50%);
      }
    }
  }
}
</style>
