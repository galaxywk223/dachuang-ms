<template>
  <div class="applied-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">已申请结题项目</span>
            <el-tag
              type="info"
              size="small"
              effect="plain"
              round
              class="ml-2"
              >{{ pagination.total }}</el-tag
            >
          </div>
          <div class="header-actions"></div>
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

        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="
                ['CLOSURE_LEVEL2_REJECTED', 'CLOSURE_LEVEL1_REJECTED'].includes(
                  row.status
                )
              "
              type="danger"
              size="small"
              link
              @click="handleReapply(row)"
            >
              重新提交
            </el-button>
            <el-button
              v-if="row.status === 'CLOSURE_SUBMITTED'"
              type="warning"
              size="small"
              link
              @click="handleRevoke(row)"
            >
              撤回申请
            </el-button>
            <el-button
              v-if="canDeleteSubmission(row)"
              type="danger"
              size="small"
              link
              @click="handleDeleteSubmission(row)"
            >
              删除提交
            </el-button>
            <el-button
              v-if="row.status === 'CLOSED'"
              type="success"
              size="small"
              link
              @click="handleCertificate(row)"
            >
              下载证书
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
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRouter } from "vue-router";
import {
  getAppliedClosureProjects,
  getProjectCertificate,
  revokeClosureApplication,
  deleteClosureSubmission,
} from "@/api/projects";

defineOptions({
  name: "StudentClosureAppliedView",
});

type AchievementInfo = {
  achievement_type_display?: string;
};

type ProjectRow = {
  id: number;
  project_no?: string;
  title?: string;
  level_display?: string;
  category_display?: string;
  leader_name?: string;
  leader_student_id?: string;
  college?: string;
  leader_contact?: string;
  budget?: number;
  advisors_info?: Array<{ name?: string }>;
  achievements?: AchievementInfo[];
  achievement_summary?: string;
  status?: string;
};

type AppliedListResponse = {
  code: number;
  data?: ProjectRow[];
  total?: number;
  message?: string;
};

type ApiResponse = {
  code?: number;
  message?: string;
};

const getErrorMessage = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    return error.message || fallback;
  }
  if (typeof error === "string") {
    return error || fallback;
  }
  return fallback;
};

const router = useRouter();

// 表格数据
const tableData = ref<ProjectRow[]>([]);
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
const getAchievementTypes = (row: ProjectRow) => {
  // 根据项目的成果信息拼接成果形式
  if (row.achievements && row.achievements.length > 0) {
    const types = row.achievements.map((a) => a.achievement_type_display);
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

    const response = (await getAppliedClosureProjects(
      params
    )) as AppliedListResponse;
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || 0;
    } else {
      ElMessage.error(response.message || "获取项目列表失败");
    }
  } catch (error: unknown) {
    console.error("获取已申请结题项目失败:", error);
    ElMessage.error(getErrorMessage(error, "获取项目列表失败"));
  } finally {
    loading.value = false;
  }
};

const canDeleteSubmission = (row: ProjectRow) => {
  return [
    "CLOSURE_SUBMITTED",
    "CLOSURE_LEVEL2_REVIEWING",
    "CLOSURE_LEVEL2_REJECTED",
    "CLOSURE_LEVEL1_REVIEWING",
    "CLOSURE_LEVEL1_REJECTED",
    "CLOSURE_RETURNED",
  ].includes(row.status ?? "");
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

const handleReapply = (row: ProjectRow) => {
  if (!row?.id) return;
  router.push({ path: "/closure/apply", query: { projectId: row.id } });
};

const handleRevoke = async (row: ProjectRow) => {
  try {
    await ElMessageBox.confirm("确认撤回结题申请吗？", "提示", {
      type: "warning",
      confirmButtonText: "确认撤回",
      cancelButtonText: "取消",
    });
    const response = (await revokeClosureApplication(row.id)) as ApiResponse;
    if (response.code === 200) {
      ElMessage.success("已撤回结题申请");
      fetchAppliedProjects();
    }
  } catch {
    // cancel
  }
};

const handleDeleteSubmission = async (row: ProjectRow) => {
  try {
    await ElMessageBox.confirm(
      "确定删除该结题提交吗？删除后可在回收站恢复。",
      "提示",
      {
        type: "warning",
      }
    );
    const res = (await deleteClosureSubmission(row.id)) as ApiResponse;
    if (res?.code === 200) {
      ElMessage.success("已移入回收站");
      fetchAppliedProjects();
    } else {
      ElMessage.error(res?.message || "删除失败");
    }
  } catch {
    // cancel
  }
};

const handleCertificate = async (row: ProjectRow) => {
  try {
    const res = await getProjectCertificate(row.id);
    const blob =
      res instanceof Blob
        ? res
        : new Blob(
            [typeof res === "string" ? res : JSON.stringify(res ?? "")],
            {
              type: "text/html",
            }
          );
    const url = window.URL.createObjectURL(blob);
    window.open(url, "_blank");
    window.setTimeout(() => URL.revokeObjectURL(url), 10000);
  } catch (error: unknown) {
    console.error("获取结题证书失败:", error);
    ElMessage.error(getErrorMessage(error, "获取结题证书失败"));
  }
};

// 页面加载时获取数据
onMounted(() => {
  fetchAppliedProjects();
});
</script>

<style scoped lang="scss">
@use "./Applied.scss";
</style>
```
