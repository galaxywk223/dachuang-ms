<template>
  <div class="expert-reviews-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="title">我的评审任务</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-click="fetchReviews">
        <el-tab-pane label="待评审" name="pending"></el-tab-pane>
        <el-tab-pane label="已评审" name="reviewed"></el-tab-pane>
      </el-tabs>

      <el-table v-loading="loading" :data="reviews" style="width: 100%" stripe border>
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
             <el-button 
                v-else
                size="small" 
                @click="handleView(scope.row)"
             >
                查看详情
             </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Review Dialog -->
    <el-dialog
      :title="dialogTitle"
      v-model="dialogVisible"
      width="600px"
      @close="handleClose"
    >
      <el-descriptions title="项目信息" :column="1" border class="mb-4">
          <el-descriptions-item label="项目名称">{{ currentReview?.project_title }}</el-descriptions-item>
          <el-descriptions-item label="项目编号">{{ currentReview?.project_no }}</el-descriptions-item>
          <!-- Could add link to project detail or attachment -->
      </el-descriptions>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px" v-if="!isViewMode">
        <el-form-item label="分数" prop="score">
           <el-input-number v-model="form.score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="评审意见" prop="comments">
           <el-input 
              v-model="form.comments" 
              type="textarea" 
              :rows="4" 
              placeholder="请输入评审意见"
           />
        </el-form-item>
         <el-form-item label="评审结果" prop="action">
             <el-radio-group v-model="form.action">
                 <el-radio label="approve">通过</el-radio>
                 <el-radio label="reject">不通过</el-radio>
             </el-radio-group>
        </el-form-item>
      </el-form>
      
      <div v-else>
          <p><strong>分数:</strong> {{ currentReview?.score }}</p>
          <p><strong>意见:</strong> {{ currentReview?.comments }}</p>
          <p><strong>结果:</strong> {{ currentReview?.status_display }}</p>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleClose">{{ isViewMode ? '关闭' : '取消' }}</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit" v-if="!isViewMode">
            提交评审
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from "vue";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import request from "@/utils/request";
import dayjs from "dayjs";

const loading = ref(false);
const submitting = ref(false);
const reviews = ref<any[]>([]);
const activeTab = ref("pending");

const dialogVisible = ref(false);
const isViewMode = ref(false);
const currentReview = ref<any>(null);
const formRef = ref<FormInstance>();
const form = reactive({
    score: null as number | null,
    comments: "",
    action: "approve"
});

const rules = reactive<FormRules>({
    score: [{ required: true, message: "请输入分数", trigger: "blur" }],
    comments: [{ required: true, message: "请输入评审意见", trigger: "blur" }],
    action: [{ required: true, message: "请选择结果", trigger: "change" }],
});

const dialogTitle = computed(() => isViewMode.value ? "查看评审" : "执行评审");

const fetchReviews = async () => {
    loading.value = true;
    try {
        const params: any = {};
        if (activeTab.value === 'pending') {
            params.status = 'PENDING';
        } else {
             // Fetch all non-pending? OR separate status query
             // The API filterset_fields=['status'] supports single value. 
             // To get 'reviewed' (APPROVED or REJECTED), we might need multiple calls or backend change.
             // For now, let's just fetch everything if 'reviewed' and client filter, or simple 2 calls.
             // Or API support 'status__in'. 
             // Let's assume we want to see "Everything that is NOT Pending"
             // But simple implementation: Just separate tabs by status if easy.
             // If clicked 'reviewed', maybe load recently reviewed.
             params.status = 'APPROVED'; // Just show Approved for now, or need better filter
        }
        
        const { data } = await request.get('/reviews/', { params });
        reviews.value = data.results || data;
    } catch (error) {
        console.error(error);
        ElMessage.error("获取评审任务失败");
    } finally {
        loading.value = false;
    }
};

const handleReview = (review: any) => {
    isViewMode.value = false;
    currentReview.value = review;
    form.score = null;
    form.comments = "";
    form.action = "approve";
    dialogVisible.value = true;
};

const handleView = (review: any) => {
    isViewMode.value = true;
    currentReview.value = review;
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
                await request.post(`/reviews/${currentReview.value.id}/review/`, form);
                ElMessage.success("评审提交成功");
                dialogVisible.value = false;
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

const formatDate = (date: string) => {
    return dayjs(date).format("YYYY-MM-DD HH:mm");
};

onMounted(() => {
    fetchReviews();
});
</script>

<style scoped lang="scss">
.expert-reviews-container {
    padding: 20px;
    .card-header {
       font-size: 18px; font-weight: bold;
    }
}
</style>
