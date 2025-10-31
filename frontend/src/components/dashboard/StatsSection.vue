<template>
  <el-row :gutter="24" class="stats-row">
    <el-col :span="6" v-for="stat in stats" :key="stat.label">
      <StatCard
        :icon="stat.icon"
        :icon-bg="stat.iconBg"
        :value="stat.value"
        :label="stat.label"
        :change-text="stat.changeText"
      />
    </el-col>
  </el-row>
</template>

<script setup>
import { computed } from "vue";
import { Folder, Clock, Loading, Bell } from "@element-plus/icons-vue";
import StatCard from "@/components/common/StatCard.vue";

const props = defineProps({
  statistics: {
    type: Object,
    required: true,
  },
});

const stats = computed(() => [
  {
    icon: Folder,
    iconBg: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    value: props.statistics.myProjects,
    label: "我的项目",
    changeText: "较上月 +12%",
  },
  {
    icon: Clock,
    iconBg: "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    value: props.statistics.pending,
    label: "待审核",
    changeText: "较上周 -8%",
  },
  {
    icon: Loading,
    iconBg: "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
    value: props.statistics.inProgress,
    label: "进行中",
    changeText: "较上月 +5%",
  },
  {
    icon: Bell,
    iconBg: "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
    value: props.statistics.unreadNotifications,
    label: "未读通知",
    changeText: "今日新增 3条",
  },
]);
</script>

<style scoped lang="scss">
.stats-row {
  margin-bottom: 24px;
}
</style>
