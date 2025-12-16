<template>
  <div class="apply-page">
    <div class="form-container">
      <!-- Header -->
      <div class="page-header">
        <div class="title-bar">
           <span class="title">结题申请</span>
           <el-tag size="small" type="success" effect="plain" round>项目结题</el-tag>
        </div>
        <div class="actions">
           <el-button @click="router.back()">返回</el-button>
           <el-button type="info" plain @click="saveAsDraft">保存草稿</el-button>
           <el-button type="primary" @click="submitForm">提交申请</el-button>
        </div>
      </div>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="right"
        label-width="120px"
        status-icon
        size="default"
        class="main-form"
        v-loading="loading"
      >
        <!-- Project Info -->
        <div class="form-section">
          <div class="section-header">
              <span class="section-title">项目基本信息</span>
          </div>
          <el-row :gutter="32">
            <el-col :span="8">
              <el-form-item label="项目名称">
                <el-input :model-value="projectInfo.title" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="项目编号">
                <el-input :model-value="projectInfo.project_no" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="负责人">
                <el-input :model-value="projectInfo.leader_name" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="级别">
                <el-input :model-value="projectInfo.level_display" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="类别">
                <el-input :model-value="projectInfo.category_display" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
               <el-form-item label="经费">
                 <el-input :model-value="projectInfo.budget" disabled class="is-disabled-soft">
                     <template #append>元</template>
                 </el-input>
               </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- Closure Materials -->
        <div class="form-section">
          <div class="section-header">
              <span class="section-title">结题材料</span>
          </div>
          <el-row :gutter="32">
            <el-col :span="12">
              <el-form-item label="结题报告" prop="final_report">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleReportChange"
                  :file-list="reportFileList"
                  :limit="1"
                  accept=".pdf"
                  class="upload-demo w-full"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    拖拽上传结题报告 (PDF) <em>点击上传</em>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="支撑附件" prop="achievement_file">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleAchievementFileChange"
                  :file-list="achievementFileList"
                  :limit="1"
                  accept=".zip,.rar,.pdf"
                  class="upload-demo w-full"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                     拖拽上传其他附件 (ZIP/PDF) <em>点击上传</em>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
          </el-row>
           <el-form-item label="成果简介" prop="achievement_summary" style="margin-top: 16px;">
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
                <span class="section-title">项目成果列表</span>
                <el-button type="primary" plain size="small" :icon="Plus" @click="openAchievementDialog()">添加成果</el-button>
            </div>
            
            <el-table 
                :data="achievements" 
                border 
                style="width: 100%; margin-top: 12px;"
                :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
            >
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
                <template #empty>
                    <div class="empty-text">暂无成果，请点击上方按钮添加</div>
                </template>
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
    </div>
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
        payload.append('is_draft', String(isDraft));

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

.form-container {
  background: white;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  border: 1px solid $color-border-light;
  overflow: hidden;
  max-width: 1200px; /* Optional: limit width for better readability */
  margin: 0 auto;
}

.page-header {
  padding: 16px 24px;
  border-bottom: 1px solid $slate-100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .title-bar {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .title {
        font-size: 18px;
        font-weight: 600;
        color: $slate-800;
      }
  }
}

.main-form {
  padding: 24px 32px;
}

.form-section {
  margin-bottom: 32px;
  
  &:last-child {
      margin-bottom: 0;
  }

  .section-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 1px solid $slate-100;
      
      .section-title {
          font-size: 16px;
          font-weight: 600;
          color: $slate-800;
          display: flex;
          align-items: center;
          
          &::before {
              content: '';
              display: inline-block;
              width: 4px;
              height: 16px;
              background-color: $primary-500;
              margin-right: 8px;
              border-radius: 2px;
          }
      }
  }
}

.upload-demo {
  :deep(.el-upload-dragger) {
    width: 100%;
    background-color: $slate-50;
    border-color: $slate-200;
    
    &:hover {
        border-color: $primary-500;
        background-color: white;
    }
  }
}

.is-disabled-soft {
    :deep(.el-input__wrapper) {
        background-color: $slate-50 !important;
        box-shadow: none !important;
        border: 1px solid $slate-200;
        
        .el-input__inner {
            color: $slate-600;
            -webkit-text-fill-color: $slate-600;
        }
    }
}

.empty-text {
    color: $slate-400;
    padding: 20px 0;
    text-align: center;
}
</style>
