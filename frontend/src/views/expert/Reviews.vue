<template>
  <div class="expert-reviews-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="title">我的评审任务</span>
          <div class="header-actions" v-if="activeTab === 'pending'">
            <el-button type="primary" :disabled="selectedRows.length === 0" @click="openBatchDialog">
              批量评审
            </el-button>
          </div>
        </div>
      </template>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="待评审" name="pending"></el-tab-pane>
        <el-tab-pane label="已评审" name="reviewed"></el-tab-pane>
      </el-tabs>

      <el-table
        v-loading="loading"
        :data="reviews"
        style="width: 100%"
        stripe
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column v-if="activeTab === 'pending'" type="selection" width="55" align="center" />
        <el-table-column prop="project_no" label="项目编号" width="150" />
        <el-table-column prop="project_title" label="项目名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="review_type_display" label="评审类型" width="120" />
        <el-table-column prop="review_level_display" label="评审级别" width="120" />
        <el-table-column prop="status_display" label="状态" width="100">
           <template #default="scope">
              <el-tag :type="scope.row.status === 'PENDING' ? 'warning' : 'success'">
                  {{ scope.row.status_display }}
              </el-tag>
           </template>
        </el-table-column>
        <el-table-column prop="created_at" label="分配时间" width="180">
            <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
            </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="scope">
            <div class="op-cell">
             <el-button 
                v-if="scope.row.status === 'PENDING'"
                size="small" 
                type="primary" 
                @click="handleReview(scope.row)"
             >
                开始评审
             </el-button>
             <template v-else>
               <el-button size="small" @click="handleView(scope.row)">查看详情</el-button>
               <el-button size="small" type="primary" @click="handleEdit(scope.row)">修改评审</el-button>
             </template>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Review Dialog -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="600px" @close="handleClose">
      <el-descriptions title="项目信息" :column="1" border class="mb-4">
          <el-descriptions-item label="项目名称">{{ currentReview?.project_title }}</el-descriptions-item>
          <el-descriptions-item label="项目编号">{{ currentReview?.project_no }}</el-descriptions-item>
          <!-- Could add link to project detail or attachment -->
      </el-descriptions>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" v-if="!isViewMode">
        <el-form-item label="分数" prop="score" v-if="needsScore && !hasTemplate">
           <el-input-number v-model="form.score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item v-if="hasTemplate && currentReview?.template_info?.notice" label="注意事项">
          <el-alert
            :title="currentReview?.template_info?.notice"
            type="info"
            show-icon
            :closable="false"
          />
        </el-form-item>
        <el-form-item v-if="hasTemplate" label="评分项">
          <div class="score-items">
            <div v-for="item in scoreItems" :key="item.item_id" class="score-row">
              <div class="score-title">
                <span>{{ item.title }}</span>
                <span class="score-meta">
                  权重 {{ item.weight }} / 满分 {{ item.max_score }}
                  <span v-if="item.is_required" class="required-flag">必填</span>
                </span>
              </div>
              <el-input-number v-model="item.score" :min="0" :max="item.max_score" />
            </div>
          </div>
        </el-form-item>
        <el-form-item :label="isMidTerm ? '审核意见' : '评审意见'" prop="comments">
           <el-input 
              v-model="form.comments" 
              type="textarea" 
              :rows="4" 
              placeholder="请输入评审意见"
           />
        </el-form-item>
         <el-form-item label="审核结果" prop="action" v-if="isMidTerm">
             <el-radio-group v-model="form.action">
                 <el-radio label="approve">通过</el-radio>
                 <el-radio label="reject">不通过</el-radio>
             </el-radio-group>
        </el-form-item>
      </el-form>
      
      <div v-else>
          <div v-if="currentReview?.score_details?.length" class="score-view">
            <p class="score-title"><strong>评分明细:</strong></p>
            <ul>
              <li v-for="detail in currentReview.score_details" :key="detail.item_id">
                {{ detail.title }}：{{ detail.score }}（权重 {{ detail.weight }}，加权 {{ detail.weighted_score }}）
              </li>
            </ul>
          </div>
          <p v-if="currentReview?.review_type !== 'MID_TERM'"><strong>分数:</strong> {{ currentReview?.score }}</p>
          <p><strong>意见:</strong> {{ currentReview?.comments }}</p>
          <p><strong>状态:</strong> {{ currentReview?.status_display }}</p>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleClose">{{ isViewMode ? '关闭' : '取消' }}</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit" v-if="!isViewMode">
            {{ isEditMode ? '保存修改' : '提交评审' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="batchDialogVisible" title="批量评审" width="520px" @close="resetBatchForm">
      <el-form ref="batchFormRef" :model="batchForm" label-width="100px">
        <el-form-item label="审核结果" v-if="isBatchMidTerm">
          <el-radio-group v-model="batchForm.action">
            <el-radio label="approve">通过</el-radio>
            <el-radio label="reject">不通过</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分数" v-if="!isBatchMidTerm">
          <el-input-number v-model="batchForm.score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="评审意见">
          <el-input v-model="batchForm.comments" type="textarea" :rows="4" placeholder="请输入评审意见" />
        </el-form-item>
        <el-form-item label="结题评价" v-if="isBatchClosure">
          <el-select v-model="batchForm.closure_rating" placeholder="请选择" style="width: 100%">
            <el-option v-for="item in closureRatingOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="batchSubmitting" @click="submitBatchReview">
            提交
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from "vue";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import request from "@/utils/request";
import dayjs from "dayjs";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";

defineOptions({
  name: "ExpertReviewsView",
});

type ScoreItem = {
  item_id: number;
  title: string;
  weight: number;
  max_score: number;
  is_required: boolean;
  score: number | null;
};

type TemplateItem = {
  id: number;
  title: string;
  weight: number;
  max_score: number;
  is_required: boolean;
};

type TemplateInfo = {
  notice?: string;
  items?: TemplateItem[];
};

type ScoreDetail = {
  item_id: number;
  title?: string;
  score: number;
  weight?: number;
  weighted_score?: number;
};

type ReviewRow = {
  id: number;
  review_type?: string;
  status?: string;
  status_display?: string;
  review_type_display?: string;
  review_level_display?: string;
  created_at?: string;
  project_info?: { project_no?: string; title?: string };
  template_info?: TemplateInfo;
  score?: number | null;
  comments?: string;
  score_details?: ScoreDetail[];
  project_no?: string;
  project_title?: string;
  closure_rating?: string;
};

type ReviewForm = {
  score: number | null;
  comments: string;
  action: "approve" | "reject";
};

type ReviewPayload = {
  comments: string;
  action: "approve" | "reject";
  score?: number | null;
  score_details?: { item_id: number; score: number | null }[];
};

type BatchPayload = {
  review_ids: number[];
  action: "approve" | "reject";
  comments: string;
  score?: number;
  closure_rating?: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveList = <T,>(payload: unknown): T[] => {
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
const batchSubmitting = ref(false);
const reviews = ref<ReviewRow[]>([]);
const activeTab = ref("pending");
const selectedRows = ref<ReviewRow[]>([]);

const dialogVisible = ref(false);
const dialogMode = ref<"review" | "view" | "edit">("review");
const currentReview = ref<ReviewRow | null>(null);
const formRef = ref<FormInstance>();
const form = reactive<ReviewForm>({
  score: null,
  comments: "",
  action: "approve",
});
const scoreItems = ref<ScoreItem[]>([]);

const isMidTerm = computed(() => currentReview.value?.review_type === "MID_TERM");
const needsScore = computed(() => currentReview.value?.review_type !== "MID_TERM");
const hasTemplate = computed(() => !!currentReview.value?.template_info?.items?.length);

const rules = reactive<FormRules>({
    score: [
      {
        validator: (_rule, value, callback) => {
          if (!needsScore.value || hasTemplate.value) return callback();
          if (value === null || value === undefined || value === "") {
            return callback(new Error("请输入分数"));
          }
          return callback();
        },
        trigger: "blur",
      },
    ],
    comments: [{ required: true, message: "请输入评审意见", trigger: "blur" }],
    action: [
      {
        validator: (_rule, value, callback) => {
          if (!isMidTerm.value) return callback();
          if (!value) return callback(new Error("请选择结果"));
          return callback();
        },
        trigger: "change",
      },
    ],
});

const { loadDictionaries, getOptions } = useDictionary();
const closureRatingOptions = computed(() => getOptions(DICT_CODES.CLOSURE_RATING));

const isViewMode = computed(() => dialogMode.value === "view");
const isEditMode = computed(() => dialogMode.value === "edit");
const dialogTitle = computed(() => {
  if (dialogMode.value === "view") return "查看评审";
  if (dialogMode.value === "edit") return "修改评审";
  return "执行评审";
});

const batchDialogVisible = ref(false);
const batchFormRef = ref<FormInstance>();
type BatchFormState = {
  action: "approve" | "reject";
  score: number | null;
  comments: string;
  closure_rating: string;
};

const batchForm = reactive<BatchFormState>({
  action: "approve",
  score: null,
  comments: "",
  closure_rating: "",
});
const fetchToken = ref(0);

const isBatchClosure = computed(() => {
  if (selectedRows.value.length === 0) return false;
  return selectedRows.value.every((row) => row.review_type === "CLOSURE");
});

const isBatchMidTerm = computed(() => {
  if (selectedRows.value.length === 0) return false;
  return selectedRows.value.every((row) => row.review_type === "MID_TERM");
});

const fetchReviews = async () => {
    loading.value = true;
    const currentToken = ++fetchToken.value;
    try {
        const params: Record<string, string> = {};
        if (activeTab.value === "pending") {
            params.status = "PENDING";
        } else {
             params.status_in = "APPROVED,REJECTED";
        }
        
        const res = await request.get("/reviews/", { params });
        if (currentToken !== fetchToken.value) return;
        const payload = isRecord(res) && isRecord(res.data) ? res.data : res;
        const records = resolveList<ReviewRow>(payload);
        reviews.value = (records || []).map((r) => ({
            ...r,
            project_no: r.project_info?.project_no,
            project_title: r.project_info?.title,
        }));
        selectedRows.value = [];
    } catch (error: unknown) {
        console.error(error);
        ElMessage.error("获取评审任务失败");
    } finally {
        if (currentToken === fetchToken.value) {
          loading.value = false;
        }
    }
};

const handleReview = (review: ReviewRow) => {
    dialogMode.value = "review";
    currentReview.value = review;
    form.score = null;
    form.comments = "";
    form.action = "approve";
    if (review.template_info?.items?.length) {
        scoreItems.value = review.template_info.items.map((item) => ({
            item_id: item.id,
            title: item.title,
            weight: item.weight,
            max_score: item.max_score,
            is_required: item.is_required,
            score: 0,
        }));
    } else {
        scoreItems.value = [];
    }
    dialogVisible.value = true;
};

const handleView = (review: ReviewRow) => {
    dialogMode.value = "view";
    currentReview.value = review;
    dialogVisible.value = true;
};

const handleEdit = (review: ReviewRow) => {
    dialogMode.value = "edit";
    currentReview.value = review;
    form.score = review.score ?? null;
    form.comments = review.comments || "";
    form.action = review.status === "REJECTED" ? "reject" : "approve";
    if (review.template_info?.items?.length) {
        const detailMap = new Map(
            (review.score_details || []).map((d) => [d.item_id, d.score])
        );
        scoreItems.value = review.template_info.items.map((item) => ({
            item_id: item.id,
            title: item.title,
            weight: item.weight,
            max_score: item.max_score,
            is_required: item.is_required,
            score: detailMap.get(item.id) ?? 0,
        }));
    } else {
        scoreItems.value = [];
    }
    dialogVisible.value = true;
};

const handleClose = () => {
    dialogVisible.value = false;
    formRef.value?.resetFields();
    scoreItems.value = [];
};

const handleSubmit = async () => {
    if (!formRef.value) return;
    const review = currentReview.value;
    if (!review) return;
    await formRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true;
            try {
                const endpoint =
                  dialogMode.value === "edit"
                    ? `/reviews/${review.id}/revise/`
                    : `/reviews/${review.id}/review/`;
                const payload: ReviewPayload = {
                  comments: form.comments,
                  action: "approve",
                };
                if (review.review_type === "MID_TERM") {
                  payload.action = form.action;
                } else {
                  if (!hasTemplate.value) {
                    payload.score = form.score;
                  }
                }
                if (hasTemplate.value) {
                  const missing = scoreItems.value.find(
                    (item) =>
                      item.is_required && (item.score === null || item.score === undefined)
                  );
                  if (missing) {
                    ElMessage.warning(`评分项“${missing.title}”为必填`);
                    submitting.value = false;
                    return;
                  }
                  payload.score_details = scoreItems.value.map((item) => ({
                    item_id: item.item_id,
                    score: item.score,
                  }));
                }
                await request.post(endpoint, payload);
                ElMessage.success(dialogMode.value === "edit" ? "评审已更新" : "评审提交成功");
                dialogVisible.value = false;
                if (dialogMode.value === "review") {
                  activeTab.value = "reviewed";
                }
                fetchReviews();
            } catch (error: unknown) {
                console.error(error);
                ElMessage.error(getErrorMessage(error, "提交失败"));
            } finally {
                submitting.value = false;
            }
        }
    });
};

const handleSelectionChange = (rows: ReviewRow[]) => {
  selectedRows.value = rows;
};

const resetBatchForm = () => {
  batchFormRef.value?.resetFields();
  batchForm.action = "approve";
  batchForm.score = null;
  batchForm.comments = "";
  batchForm.closure_rating = "";
};

const openBatchDialog = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning("请先勾选评审任务");
    return;
  }
  if (selectedRows.value.some((row) => row.template_info?.items?.length)) {
    ElMessage.warning("包含评分模板的任务暂不支持批量评审，请单独评分");
    return;
  }
  resetBatchForm();
  batchDialogVisible.value = true;
};

const submitBatchReview = async () => {
  if (selectedRows.value.length === 0) return;
  batchSubmitting.value = true;
  try {
    const payload: BatchPayload = {
      review_ids: selectedRows.value.map((row) => row.id),
      action: isBatchMidTerm.value ? batchForm.action : "approve",
      comments: batchForm.comments,
    };
    if (!isBatchMidTerm.value && batchForm.score !== null && batchForm.score !== undefined) {
      payload.score = batchForm.score;
    }
    if (isBatchClosure.value && batchForm.closure_rating) {
      payload.closure_rating = batchForm.closure_rating;
    }
    await request.post("/reviews/batch-review/", payload);
    ElMessage.success("批量评审完成");
    batchDialogVisible.value = false;
    selectedRows.value = [];
    fetchReviews();
  } catch (error: unknown) {
    ElMessage.error(getErrorMessage(error, "批量评审失败"));
  } finally {
    batchSubmitting.value = false;
  }
};

const formatDate = (date: string) => {
    return dayjs(date).format("YYYY-MM-DD HH:mm");
};

onMounted(() => {
    loadDictionaries([DICT_CODES.CLOSURE_RATING]);
    fetchReviews();
});

watch(
  () => activeTab.value,
  () => {
    fetchReviews();
  }
);
</script>

<style scoped lang="scss">
.expert-reviews-container {
    padding: 20px;
    .card-header {
       font-size: 18px; font-weight: bold;
    }
    .op-cell {
        display: flex;
        justify-content: center;
        gap: 8px;
    }
    .score-items {
        display: flex;
        flex-direction: column;
        gap: 12px;
        width: 100%;
    }
    .score-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 8px 12px;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        background: #f8fafc;
    }
    .score-title {
        display: flex;
        flex-direction: column;
        gap: 4px;
        font-weight: 500;
    }
    .score-meta {
        font-size: 12px;
        color: #64748b;
    }
    .required-flag {
        margin-left: 6px;
        color: #ef4444;
    }
    .score-view {
        margin-bottom: 12px;
        ul {
            margin: 6px 0 0;
            padding-left: 16px;
            color: #475569;
        }
    }
}
</style>
