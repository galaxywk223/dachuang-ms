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
        <el-form-item label="分数" prop="score" v-if="needsScore">
           <el-input-number v-model="form.score" :min="0" :max="100" />
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

const loading = ref(false);
const submitting = ref(false);
const batchSubmitting = ref(false);
const reviews = ref<any[]>([]);
const activeTab = ref("pending");
const selectedRows = ref<any[]>([]);

const dialogVisible = ref(false);
const dialogMode = ref<"review" | "view" | "edit">("review");
const currentReview = ref<any>(null);
const formRef = ref<FormInstance>();
const form = reactive({
    score: null as number | null,
    comments: "",
    action: "approve"
});

const isMidTerm = computed(() => currentReview.value?.review_type === "MID_TERM");
const needsScore = computed(() => currentReview.value?.review_type !== "MID_TERM");

const rules = reactive<FormRules>({
    score: [
      {
        validator: (_rule: any, value: any, callback: any) => {
          if (!needsScore.value) return callback();
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
        validator: (_rule: any, value: any, callback: any) => {
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
const batchForm = reactive({
  action: "approve",
  score: null as number | null,
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
        const params: any = {};
        if (activeTab.value === 'pending') {
            params.status = 'PENDING';
        } else {
             params.status_in = 'APPROVED,REJECTED';
        }
        
        const res: any = await request.get('/reviews/', { params });
        if (currentToken !== fetchToken.value) return;
        const payload = res.data || res;
        const records = Array.isArray(payload) ? payload : (payload.results || payload.data?.results || payload.data || []);
        reviews.value = (records || []).map((r: any) => ({
            ...r,
            project_no: r.project_info?.project_no,
            project_title: r.project_info?.title,
        }));
        selectedRows.value = [];
    } catch (error) {
        console.error(error);
        ElMessage.error("获取评审任务失败");
    } finally {
        if (currentToken === fetchToken.value) {
          loading.value = false;
        }
    }
};

const handleReview = (review: any) => {
    dialogMode.value = "review";
    currentReview.value = review;
    form.score = null;
    form.comments = "";
    form.action = "approve";
    dialogVisible.value = true;
};

const handleView = (review: any) => {
    dialogMode.value = "view";
    currentReview.value = review;
    dialogVisible.value = true;
};

const handleEdit = (review: any) => {
    dialogMode.value = "edit";
    currentReview.value = review;
    form.score = review.score ?? null;
    form.comments = review.comments || "";
    form.action = review.status === "REJECTED" ? "reject" : "approve";
    dialogVisible.value = true;
};

const handleClose = () => {
    dialogVisible.value = false;
    formRef.value?.resetFields();
};

const handleSubmit = async () => {
    if (!formRef.value) return;
    await formRef.value.validate(async (valid) => {
        if (valid) {
            submitting.value = true;
            try {
                const endpoint =
                  dialogMode.value === "edit"
                    ? `/reviews/${currentReview.value.id}/revise/`
                    : `/reviews/${currentReview.value.id}/review/`;
                const payload: any = {
                  comments: form.comments,
                };
                if (currentReview.value?.review_type === "MID_TERM") {
                  payload.action = form.action;
                } else {
                  payload.action = "approve";
                  payload.score = form.score;
                }
                await request.post(endpoint, payload);
                ElMessage.success(dialogMode.value === "edit" ? "评审已更新" : "评审提交成功");
                dialogVisible.value = false;
                if (dialogMode.value === "review") {
                  activeTab.value = "reviewed";
                }
                fetchReviews();
            } catch (error: any) {
                console.error(error);
                ElMessage.error(error.response?.data?.message || "提交失败");
            } finally {
                submitting.value = false;
            }
        }
    });
};

const handleSelectionChange = (rows: any[]) => {
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
  resetBatchForm();
  batchDialogVisible.value = true;
};

const submitBatchReview = async () => {
  if (selectedRows.value.length === 0) return;
  batchSubmitting.value = true;
  try {
    const payload: any = {
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
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "批量评审失败");
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
}
</style>
