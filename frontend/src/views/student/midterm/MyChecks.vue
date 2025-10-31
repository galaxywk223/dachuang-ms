<template>
  <div class="midterm-my-checks">
    <h2>我的中期检查</h2>
    <el-table :data="checks" style="width: 100%">
      <el-table-column prop="projectName" label="项目名称" />
      <el-table-column prop="submitTime" label="提交时间" width="180" />
      <el-table-column label="审核状态" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="完成进度" width="100">
        <template #default="{ row }">{{ row.progress }}%</template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="viewDetail(row)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ElMessage } from "element-plus";

const checks = ref([
  {
    id: 1,
    projectName: "基于AI的智能问答系统",
    submitTime: "2024-06-15 14:30",
    status: "审核中",
    progress: 50,
  },
]);

const getStatusType = (status: string) => {
  const map: any = {
    审核中: "warning",
    已通过: "success",
    未通过: "danger",
  };
  return map[status] || "info";
};

const viewDetail = (row: any) => {
  ElMessage.info("查看详情：" + row.projectName);
};
</script>

<style scoped lang="scss">
.midterm-my-checks {
  h2 {
    margin: 0 0 20px 0;
    font-size: 20px;
    font-weight: 500;
  }
}
</style>
