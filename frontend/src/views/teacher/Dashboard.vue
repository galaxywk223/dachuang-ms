<template>
  <div class="teacher-dashboard">
    <WelcomeSection :user="welcomeUser" />
    <StatsSection :statistics="statistics" />
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="title">{{ dashboardTitle }}</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="待审核" name="pending"></el-tab-pane>
        <el-tab-pane label="我指导的项目" name="my_projects"></el-tab-pane>
      </el-tabs>

      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        stripe
        border
      >
        <el-table-column prop="project_no" label="项目编号" width="150" />
        <el-table-column
          prop="title"
          label="项目名称"
          min-width="200"
          show-overflow-tooltip
        />
        <el-table-column prop="leader_name" label="负责人" width="120" />
        <el-table-column prop="level_display" label="级别" width="100" />
        <el-table-column
          prop="review_type_display"
          label="审核类型"
          width="120"
        />
        <el-table-column prop="status_display" label="当前状态" width="150">
          <template #default="scope">
            <el-tag>{{ scope.row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="scope">
            <el-button
              v-if="
                activeTab === 'pending' ||
                scope.row.status === 'TEACHER_AUDITING'
              "
              size="small"
              type="primary"
              @click="handleReview(scope.row)"
            >
              审核
            </el-button>
            <el-button v-else size="small" @click="handleView(scope.row)">
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Review Dialog -->
    <el-dialog
      title="项目审核"
      v-model="dialogVisible"
      width="600px"
      @close="handleClose"
    >
      <el-descriptions title="项目信息" :column="1" border class="mb-4">
        <el-descriptions-item label="项目名称">{{
          currentProject?.title
        }}</el-descriptions-item>
        <el-descriptions-item label="项目编号">{{
          currentProject?.project_no
        }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{
          currentProject?.leader_name
        }}</el-descriptions-item>
        <el-descriptions-item label="材料">
          <a
            v-if="currentProject?.file_url"
            :href="currentProject.file_url"
            target="_blank"
          >
            {{ currentProject.file_label }}
          </a>
          <span v-else>无</span>
        </el-descriptions-item>
      </el-descriptions>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="审核结果" prop="action">
          <el-radio-group v-model="form.action">
            <el-radio label="approve">通过</el-radio>
            <el-radio label="reject">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核意见" prop="comments">
          <el-input
            v-model="form.comments"
            type="textarea"
            :rows="4"
            placeholder="请输入审核意见"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            提交
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import request from "@/utils/request";
import dayjs from "dayjs";
import { useUserStore } from "@/stores/user";
import StatsSection from "@/components/dashboard/StatsSection.vue";
import {
  reviewAction,
  type WorkflowNode,
  type ReviewActionParams,
} from "@/api/reviews";
import {
  getChangeRequests,
  reviewChangeRequest,
} from "@/api/projects/change-requests";

defineOptions({
  name: "TeacherDashboardView",
});

const router = useRouter();
const route = useRoute();

type ProjectInfo = {
  project_no?: string;
  title?: string;
  leader_name?: string;
  level_display?: string;
  status?: string;
  status_display?: string;
  proposal_file_url?: string;
  mid_term_report_url?: string;
  final_report_url?: string;
};

type ReviewRecord = {
  id: number;
  review_type?: string;
  review_type_display?: string;
  created_at?: string;
  project_info?: ProjectInfo;
};

type TeacherProjectRow = ProjectInfo & {
  review_id?: number;
  review_type?: string;
  review_type_display?: string;
  file_url?: string;
  file_label?: string;
  created_at?: string;
  // Change Request fields
  is_change_request?: boolean;
  change_request_id?: number;
  id?: number;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveList = <T>(payload: unknown): T[] => {
  if (Array.isArray(payload)) return payload as T[];
  if (isRecord(payload) && Array.isArray(payload.results)) {
    return payload.results as T[];
  }
  if (
    isRecord(payload) &&
    isRecord(payload.data) &&
    Array.isArray(payload.data.results)
  ) {
    return payload.data.results as T[];
  }
  if (isRecord(payload) && Array.isArray(payload.data)) {
    return payload.data as T[];
  }
  return [];
};

const getCount = (payload: unknown): number => {
  if (!isRecord(payload)) return 0;
  if (typeof payload.count === "number") return payload.count;
  if (isRecord(payload.data) && typeof payload.data.count === "number") {
    return payload.data.count;
  }
  return 0;
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

const loading = ref(false);
const submitting = ref(false);
const projects = ref<TeacherProjectRow[]>([]);
const activeTab = ref(
  route.query.tab === "my_projects" ? "my_projects" : "pending"
);

const userStore = useUserStore();
const dashboardTitle = computed(() =>
  userStore.user?.is_expert ? "评审与指导项目" : "指导项目管理"
);
const welcomeUser = computed(() => userStore.user ?? undefined);

const statistics = reactive({
  myProjects: 0,
  pending: 0,
  inProgress: 0,
  unreadNotifications: 0,
});
const inProgressStatuses = new Set([
  "IN_PROGRESS",
  "MID_TERM_DRAFT",
  "MID_TERM_SUBMITTED",
  "MID_TERM_REVIEWING",
  "MID_TERM_APPROVED",
  "MID_TERM_REJECTED",
  "CLOSURE_DRAFT",
  "CLOSURE_SUBMITTED",
  "CLOSURE_LEVEL2_REVIEWING",
  "CLOSURE_LEVEL2_APPROVED",
  "CLOSURE_LEVEL2_REJECTED",
  "CLOSURE_LEVEL1_REVIEWING",
  "CLOSURE_LEVEL1_APPROVED",
  "CLOSURE_LEVEL1_REJECTED",
]);

const dialogVisible = ref(false);
const currentProject = ref<TeacherProjectRow | null>(null);
const currentReviewId = ref<number | null>(null);
const formRef = ref<FormInstance>();
const form = reactive<{
  action: "approve" | "reject";
  comments: string;
}>({
  action: "approve",
  comments: "",
});

const rules = reactive<FormRules>({
  action: [{ required: true, message: "请选择结果", trigger: "change" }],
  comments: [{ required: true, message: "请输入审核意见", trigger: "blur" }],
});

const parseListResponse = <T>(payload: unknown) => {
  const data =
    isRecord(payload) && isRecord(payload.data) ? payload.data : payload;
  const results = resolveList<T>(data);
  const count = getCount(data) || results.length;
  return { results, count };
};

const fetchPendingReviews = async () => {
  const res = await request.get("/reviews/", {
    params: { status: "PENDING" },
  });
  return parseListResponse<ReviewRecord>(res);
};

const fetchMyProjects = async () => {
  const res = await request.get("/projects/");
  return parseListResponse<ProjectInfo>(res);
};

const refreshStats = async () => {
  try {
    const [pendingRes, projectsRes, unreadRes] = await Promise.all([
      fetchPendingReviews(),
      fetchMyProjects(),
      request.get("/notifications/unread_count/"),
    ]);
    statistics.pending = pendingRes.count;
    statistics.myProjects = projectsRes.count;
    statistics.inProgress = (projectsRes.results || []).filter((item) =>
      inProgressStatuses.has(item.status || "")
    ).length;
    statistics.unreadNotifications =
      unreadRes?.data?.data?.count ?? unreadRes?.data?.count ?? 0;
  } catch (error) {
    console.error(error);
  }
};

const fetchProjects = async () => {
  loading.value = true;
  try {
    if (activeTab.value === "pending") {
      const { results, count } = await fetchPendingReviews();
      const rows = (results || []).map((r) => {
        const fileUrl =
          r.review_type === "MID_TERM"
            ? r.project_info?.mid_term_report_url
            : r.review_type === "CLOSURE"
            ? r.project_info?.final_report_url
            : r.project_info?.proposal_file_url;
        const fileLabel =
          r.review_type === "MID_TERM"
            ? "下载中期报告"
            : r.review_type === "CLOSURE"
            ? "下载结题报告"
            : "下载申报书";
        return {
          ...r.project_info,
          review_id: r.id,
          review_type: r.review_type,
          review_type_display: r.review_type_display,
          file_url: fileUrl,
          file_label: fileLabel,
          created_at: r.created_at,
        } as TeacherProjectRow;
      });

      // Fetch Change Requests
      const changeRes = await getChangeRequests({
        status: "TEACHER_REVIEWING",
      });
      const changeData =
        isRecord(changeRes) && isRecord(changeRes.data)
          ? changeRes.data
          : changeRes;
      const changeList = resolveList<Record<string, unknown>>(changeData);
      const changeRows: TeacherProjectRow[] = changeList.map((c) => ({
        project_no: (c.project_no as string) || "",
        title: (c.project_title as string) || "",
        leader_name: (c.leader_name as string) || "",
        level_display: (c.level as string) || "",
        status: (c.status as string) || "",
        status_display: (c.status_display as string) || "",
        review_type_display: (c.request_type_display as string) || "项目异动",
        created_at: (c.created_at as string) || "",
        file_url: (c.attachment_url as string) || "",
        file_label: "下载附件",
        is_change_request: true,
        change_request_id: (c.id as number) || 0,
      }));

      projects.value = [...rows, ...changeRows];
      statistics.pending = count + changeRows.length;
    } else {
      const { results, count } = await fetchMyProjects();
      projects.value = results || [];
      statistics.myProjects = count;
      statistics.inProgress = (results || []).filter((item) =>
        inProgressStatuses.has(item.status || "")
      ).length;
    }
  } catch (error) {
    console.error(error);
    // ElMessage.error("获取项目列表失败"); // Silencing for dev
  } finally {
    loading.value = false;
  }
};

const handleReview = async (project: TeacherProjectRow) => {
  currentProject.value = project;
  // We need the Review ID.
  // If we loaded from /reviews/, we have it.
  if (project.is_change_request) {
    currentReviewId.value = null;
    form.action = "approve";
    form.comments = "";
    dialogVisible.value = true;
    return;
  }

  if (project.review_id) {
    currentReviewId.value = project.review_id;
    form.action = "approve";
    form.comments = "";
    dialogVisible.value = true;
  } else {
    ElMessage.warning("未找到审核记录ID");
  }
};

const handleView = (row: TeacherProjectRow) => {
  if (row.id) {
    router.push({ name: "teacher-project-detail", params: { id: row.id } });
  } else {
    ElMessage.warning("项目ID缺失");
  }
};

const handleClose = () => {
  dialogVisible.value = false;
  formRef.value?.resetFields();
  rejectTargets.value = [];
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  const reviewId = currentReviewId.value;
  const isChange = currentProject.value?.is_change_request;

  if (reviewId === null && !isChange) return;
  if (isChange && !currentProject.value?.change_request_id) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true;
      try {
        const payload: ReviewActionParams = {
          action: form.action,
          comments: form.comments,
        };

        if (isChange && currentProject.value?.change_request_id) {
          await reviewChangeRequest(currentProject.value.change_request_id, {
            action: form.action,
            comments: form.comments,
          });
        } else if (reviewId !== null) {
          await reviewAction(reviewId, payload);
        }
        ElMessage.success("审核提交成功");
        dialogVisible.value = false;
        activeTab.value = "my_projects";
        fetchProjects();
        refreshStats();
      } catch (error: unknown) {
        console.error(error);
        ElMessage.error(getErrorMessage(error, "提交失败"));
      } finally {
        submitting.value = false;
      }
    }
  });
};

const formatDate = (date: string) => {
  return dayjs(date).format("YYYY-MM-DD HH:mm");
};

onMounted(() => {
  fetchProjects();
  refreshStats();
});

watch(
  () => activeTab.value,
  () => {
    fetchProjects();
    refreshStats();
  }
);

watch(
  () => route.query.tab,
  (tab) => {
    if (tab === "pending" || tab === "my_projects") {
      activeTab.value = tab as "pending" | "my_projects";
    }
  }
);
</script>

<style scoped lang="scss">
.teacher-dashboard {
  padding: 20px;
  .title {
    font-size: 18px;
    font-weight: bold;
  }
}
</style>
