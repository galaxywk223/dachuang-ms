<template>
  <div class="drafts-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">草稿箱</span>
             <el-tag type="info" size="small" effect="plain" round class="ml-2">{{ pagination.total }}</el-tag>
           </div>
           <div class="header-actions">
           </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
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

        <el-table-column label="专业代码" width="120" align="center">
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

        <el-table-column label="项目经费" width="100" align="center">
          <template #default="{ row }">
            {{ row.budget || 0 }}
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
        description="暂无结题草稿"
        :image-size="200"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRouter } from "vue-router";
import {
  getClosureDrafts,
  updateClosureApplication,
  deleteClosureDraft,
} from "@/api/project";

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

// 获取项目年份
const getProjectYear = (projectNo: string) => {
  if (!projectNo) return "-";
  const match = projectNo.match(/DC(\d{4})/);
  return match ? match[1] : "-";
};

// 获取结题草稿列表
const fetchClosureDrafts = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };

    const response: any = await getClosureDrafts(params);
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || 0;
    } else {
      ElMessage.error(response.message || "获取草稿列表失败");
    }
  } catch (error: any) {
    console.error("获取结题草稿失败:", error);
    ElMessage.error(error.message || "获取草稿列表失败");
  } finally {
    loading.value = false;
  }
};

// 分页大小改变
const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchClosureDrafts();
};

// 页码改变
const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchClosureDrafts();
};

// 继续编辑
const handleEdit = (row: any) => {
  router.push(`/closure/apply?projectId=${row.id}`);
};

// 提交草稿
const handleSubmit = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      "确定要提交该结题申请吗？提交后将进入审核流程。",
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    // 调用API提交结题申请
    const response: any = await updateClosureApplication(row.id, {
      is_draft: false,
      research_content: row.research_content,
      expected_results: row.expected_results,
      achievements: row.achievements || [],
    });

    if (response.code === 200) {
      ElMessage.success("提交成功");
      fetchClosureDrafts();
    } else {
      ElMessage.error(response.message || "提交失败");
    }
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("提交结题申请失败:", error);
      ElMessage.error(error.message || "提交失败");
    }
  }
};

// 删除草稿
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      "确定要删除该结题草稿吗？删除后无法恢复。",
      "提示",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    // 调用API删除草稿
    const response: any = await deleteClosureDraft(row.id);
    if (response.code === 200) {
      ElMessage.success("删除成功");
      fetchClosureDrafts();
    } else {
      ElMessage.error(response.message || "删除失败");
    }
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("删除结题草稿失败:", error);
      ElMessage.error(error.message || "删除失败");
    }
  }
};

// 页面加载时获取数据
onMounted(() => {
  fetchClosureDrafts();
});
</script>

<style scoped lang="scss">
@use "./Drafts.scss";
</style>
