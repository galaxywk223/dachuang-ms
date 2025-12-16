<template>
  <div class="page-container">
    <el-card class="main-card" :body-style="{ padding: '24px' }">
      <template #header>
        <div class="card-header-flex">
          <div class="header-title">结题申请</div>
          <div class="header-actions">
            <el-button @click="router.back()">返回</el-button>
            <el-button type="info" plain @click="saveAsDraft">保存草稿</el-button>
            <el-button type="primary" @click="submitForm">提交申请</el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="top"
        status-icon
        v-loading="loading"
      >
        <!-- Project Info -->
        <div class="form-section">
          <h3 class="section-title">项目基本信息</h3>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="项目名称">{{ projectInfo.title }}</el-descriptions-item>
            <el-descriptions-item label="项目编号">{{ projectInfo.project_no }}</el-descriptions-item>
            <el-descriptions-item label="负责人">{{ projectInfo.leader_name }}</el-descriptions-item>
            <el-descriptions-item label="级别">{{ projectInfo.level_display }}</el-descriptions-item>
            <el-descriptions-item label="类别">{{ projectInfo.category_display }}</el-descriptions-item>
            <el-descriptions-item label="经费">{{ projectInfo.budget }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Closure Materials -->
        <div class="form-section">
          <h3 class="section-title">结题材料</h3>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="结题报告 (PDF)" prop="final_report">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleReportChange"
                  :file-list="reportFileList"
                  :limit="1"
                  accept=".pdf"
                  class="upload-demo"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    拖拽上传结题报告 <em>点击上传</em>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="其他支撑附件 (ZIP/PDF)" prop="achievement_file">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleAchievementFileChange"
                  :file-list="achievementFileList"
                  :limit="1"
                  accept=".zip,.rar,.pdf"
                  class="upload-demo"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                     拖拽上传其他附件 <em>点击上传</em>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
          </el-row>
           <el-form-item label="项目总结/成果简介" prop="achievement_summary">
                <el-input 
                  type="textarea" 
                  v-model="formData.achievement_summary"
                  :rows="3" 
                  placeholder="请简要描述项目取得的主要成果（200字以内）"
                  maxlength="200"
                  show-word-limit
                />
           </el-form-item>
        </div>

        <!-- Achievements List -->
        <div class="form-section">
            <div class="section-header">
                <h3 class="section-title" style="margin-bottom: 0;">项目成果列表</h3>
                <el-button type="primary" plain size="small" :icon="Plus" @click="openAchievementDialog()">添加成果</el-button>
            </div>
            
            <el-table :data="achievements" border stripe style="width: 100%; margin-top: 16px;">
                <el-table-column type="index" label="序号" width="60" align="center" />
                <el-table-column prop="achievement_type" label="类型" width="100">
                    <template #default="{ row }">
                        <el-tag size="small">{{ getDictLabel(DICT_CODES.ACHIEVEMENT_TYPE, row.achievement_type) }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="title" label="成果名称" show-overflow-tooltip />
                <el-table-column prop="description" label="描述/备注" show-overflow-tooltip />
                <el-table-column label="附件" width="100" align="center">
                    <template #default="{ row }">
                        <el-tag v-if="row.file" type="success" size="small">已选择</el-tag>
                        <span v-else class="text-gray-400 text-xs">无</span>
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="120" align="center">
                    <template #default="{ row, $index }">
                        <el-button link type="primary" @click="openAchievementDialog(row, $index)">编辑</el-button>
                        <el-button link type="danger" @click="removeAchievement($index)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

      </el-form>

      <!-- Achievement Dialog -->
      <el-dialog
        v-model="dialogVisible"
        :title="dialogIndex === -1 ? '添加成果' : '编辑成果'"
        width="600px"
        destroy-on-close
        append-to-body
      >
        <el-form :model="achievementForm" label-width="100px" ref="achievementFormRef">
            <el-form-item label="成果类型" required>
                <el-select v-model="achievementForm.achievement_type" placeholder="请选择类型" style="width: 100%">
                    <el-option v-for="item in achievementTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
            </el-form-item>
            <el-form-item label="成果名称" required>
                <el-input v-model="achievementForm.title" placeholder="论文题目/专利名称/奖项名称" />
            </el-form-item>
            
            <!-- Type Specific Fields -->
            <template v-if="achievementForm.achievement_type === 'PAPER'">
                <el-form-item label="期刊/会议">
                    <el-input v-model="achievementForm.journal" placeholder="发表期刊或会议名称" />
                </el-form-item>
                <el-form-item label="发表时间">
                    <el-date-picker v-model="achievementForm.publication_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
                </el-form-item>
                <el-form-item label="DOI">
                    <el-input v-model="achievementForm.doi" placeholder="DOI号" />
                </el-form-item>
                <el-form-item label="作者列表">
                    <el-input v-model="achievementForm.authors" placeholder="所有作者，用逗号分隔" />
                </el-form-item>
            </template>

            <template v-if="achievementForm.achievement_type === 'PATENT'">
                <el-form-item label="专利号">
                    <el-input v-model="achievementForm.patent_no" />
                </el-form-item>
                <el-form-item label="专利类型">
                    <el-input v-model="achievementForm.patent_type" placeholder="如：发明专利、实用新型" />
                </el-form-item>
                <el-form-item label="申请人">
                    <el-input v-model="achievementForm.applicant" />
                </el-form-item>
            </template>

             <template v-if="achievementForm.achievement_type === 'COMPETITION_AWARD'">
                <el-form-item label="竞赛名称">
                    <el-input v-model="achievementForm.competition_name" />
                </el-form-item>
                <el-form-item label="获奖等级">
                    <el-input v-model="achievementForm.award_level" placeholder="如：国家级一等奖" />
                </el-form-item>
                <el-form-item label="获奖日期">
                    <el-date-picker v-model="achievementForm.award_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
                </el-form-item>
            </template>

            <el-form-item label="描述/备注">
                <el-input type="textarea" v-model="achievementForm.description" :rows="2" />
            </el-form-item>
            
            <el-form-item label="成果附件">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleDialogFileChange"
                  :file-list="dialogFileList"
                  :limit="1"
                  class="w-full"
                >
                    <el-button type="primary" link>点击上传附件</el-button>
                    <template #tip>
                        <div class="el-upload__tip">PDF/图片/压缩包</div>
                    </template>
                </el-upload>
            </el-form-item>
        </el-form>
        <template #footer>
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmAchievement">确定</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, type FormInstance, type UploadFile } from "element-plus";
import { UploadFilled, Plus } from "@element-plus/icons-vue";
import { getProjectDetail, createClosureApplication } from "@/api/project";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";

const route = useRoute();
const router = useRouter();
const formRef = ref<FormInstance>();
const loading = ref(false);
const { loadDictionaries, getOptions, getDictLabel } = useDictionary();

const projectId = route.query.projectId as string;

// Project Info
const projectInfo = reactive({
  title: "",
  project_no: "",
  leader_name: "",
  level_display: "",
  category_display: "",
  budget: 0
});

// Main Form Data
const formData = reactive({
  final_report: null as File | null,
  achievement_file: null as File | null,
  achievement_summary: ""
});

const reportFileList = ref<any[]>([]);
const achievementFileList = ref<any[]>([]);

// Achievements List
const achievements = ref<any[]>([]);
const dialogVisible = ref(false);
const dialogIndex = ref(-1);
const achievementFormRef = ref<FormInstance>();
const dialogFileList = ref<any[]>([]);

const achievementForm = reactive({
    achievement_type: "",
    title: "",
    description: "",
    authors: "",
    journal: "",
    publication_date: "",
    doi: "",
    patent_no: "",
    patent_type: "",
    applicant: "",
    competition_name: "",
    award_level: "",
    award_date: "",
    file: null as File | null
});

const achievementTypeOptions = computed(() => getOptions(DICT_CODES.ACHIEVEMENT_TYPE));

const rules = {
  final_report: [{ required: true, message: "请上传结题报告", trigger: "change" }],
  achievement_summary: [{ required: true, message: "请填写成果简介", trigger: "blur" }]
};

// File Handlers
const handleReportChange = (file: UploadFile) => {
  formData.final_report = file.raw as File;
  reportFileList.value = [file];
  if (file) formRef.value?.clearValidate('final_report');
};

const handleAchievementFileChange = (file: UploadFile) => {
  formData.achievement_file = file.raw as File;
  achievementFileList.value = [file];
};

const handleDialogFileChange = (file: UploadFile) => {
    achievementForm.file = file.raw as File;
    dialogFileList.value = [file];
};

// Achievement Dialog Logic
const openAchievementDialog = (row?: any, index = -1) => {
    dialogIndex.value = index;
    dialogVisible.value = true;
    dialogFileList.value = [];
    
    if (row && index > -1) {
        Object.assign(achievementForm, { ...row });
        if (row.file) {
             dialogFileList.value = [{ name: row.file.name, status: 'ready' }];
        }
    } else {
        // Reset form
        Object.keys(achievementForm).forEach(key => {
            (achievementForm as any)[key] = "";
        });
        achievementForm.file = null;
    }
};

const confirmAchievement = () => {
    if (!achievementForm.achievement_type || !achievementForm.title) {
        ElMessage.warning("请填写类型和标题");
        return;
    }
    
    const newItem = { ...achievementForm };
    if (dialogIndex.value > -1) {
        achievements.value[dialogIndex.value] = newItem;
    } else {
        achievements.value.push(newItem);
    }
    dialogVisible.value = false;
};

const removeAchievement = (index: number) => {
    achievements.value.splice(index, 1);
};

// Initialization
const fetchProjectInfo = async () => {
    if (!projectId) {
        ElMessage.error("参数错误：缺少项目ID");
        return;
    }
    loading.value = true;
    try {
        const res: any = await getProjectDetail(Number(projectId));
        if (res.code === 200) {
            const data = res.data;
            projectInfo.title = data.title;
            projectInfo.project_no = data.project_no;
            projectInfo.leader_name = data.leader_info?.real_name || data.leader_name;
            projectInfo.level_display = data.level_display;
            projectInfo.category_display = data.category_display;
            projectInfo.budget = data.budget;
        }
    } catch (e) {
        ElMessage.error("获取项目详情失败");
    } finally {
        loading.value = false;
    }
};

// Submission
const submit = async (isDraft: boolean) => {
    if (!isDraft) {
        if (!formRef.value) return;
        await formRef.value.validate(async (valid) => {
            if (!valid) return;
            await doSubmit(false);
        });
    } else {
        await doSubmit(true);
    }
};

const doSubmit = async (isDraft: boolean) => {
    loading.value = true;
    try {
        const payload = new FormData();
        
        // Basic fields
        if (formData.final_report) payload.append('final_report', formData.final_report);
        if (formData.achievement_file) payload.append('achievement_file', formData.achievement_file);
        payload.append('achievement_summary', formData.achievement_summary);
        payload.append('is_draft', String(isDraft)); // Explicit string conversion for FormData

        // Achievements Logic
        // 1. Serialize the list (excluding file objects)
        const achievementsData = achievements.value.map(item => {
            const { file, ...rest } = item; 
            return rest;
        });
        payload.append('achievements_json', JSON.stringify(achievementsData));

        // 2. Append files with indexed keys
        achievements.value.forEach((item, index) => {
            if (item.file) {
                payload.append(`achievement_${index}`, item.file);
            }
        });

        const res: any = await createClosureApplication(Number(projectId), payload);
        if (res.code === 200 || res.status === 201) {
             ElMessage.success(isDraft ? "草稿已保存" : "申请已提交");
             router.push('/closure/applied'); 
        } else {
             ElMessage.error(res.message || "操作失败");
        }
    } catch (e: any) {
        ElMessage.error(e.message || "提交失败");
    } finally {
        loading.value = false;
    }
};

const submitForm = () => submit(false);
const saveAsDraft = () => submit(true);

onMounted(() => {
    loadDictionaries([DICT_CODES.ACHIEVEMENT_TYPE]);
    fetchProjectInfo();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.page-container {
  background-color: #f0f2f5;
  min-height: 100%;
}

.main-card {
  border: none;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08) !important;
  background: #fff;
  margin-top: 24px;
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.form-section {
  margin-bottom: 32px;
  
  .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 8px;
      border-bottom: 1px solid #eee;
  }
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin: 0;
    padding-left: 10px;
    border-left: 3px solid $primary-600;
    line-height: 1.2;
  }
}

.upload-demo {
  :deep(.el-upload-dragger) {
    width: 100%;
  }
}
</style>
