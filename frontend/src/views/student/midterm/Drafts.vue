<template>
  <div class="midterm-drafts">
    <h2>草稿箱</h2>
    <el-table :data="drafts" style="width: 100%">
      <el-table-column prop="projectName" label="项目名称" />
      <el-table-column prop="saveTime" label="保存时间" width="180" />
      <el-table-column prop="progress" label="完成进度" width="100">
        <template #default="{ row }">{{ row.progress }}%</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="editDraft(row)">
            继续编辑
          </el-button>
          <el-button type="danger" link size="small" @click="deleteDraft(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

const drafts = ref([
  {
    id: 1,
    projectName: "基于AI的智能问答系统",
    saveTime: "2024-06-10 16:20",
    progress: 50,
  },
]);

const editDraft = (row: any) => {
  ElMessage.info("编辑草稿：" + row.projectName);
};

const deleteDraft = (_row: any) => {
  ElMessageBox.confirm("确定要删除该草稿吗？", "提示", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  }).then(() => {
    ElMessage.success("删除成功");
  });
};
</script>

<style scoped lang="scss">
.midterm-drafts {
  h2 {
    margin: 0 0 20px 0;
    font-size: 20px;
    font-weight: 500;
  }
}
</style>
