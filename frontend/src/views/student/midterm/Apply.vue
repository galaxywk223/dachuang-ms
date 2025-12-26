<template>
  <div class="midterm-apply-container">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">中期检查报告提交</span>
            <el-tag v-if="project" :type="getStatusType(project.status)" class="ml-3">
              {{ getStatusText(project.status) }}
            </el-tag>
          </div>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="!project" class="empty-container">
        <el-empty :description="emptyMessage" />
      </div>

      <div v-else class="content-container">
        <el-descriptions title="项目基本信息" :column="2" border>
          <el-descriptions-item label="项目编号">{{ project.project_no }}</el-descriptions-item>
          <el-descriptions-item label="项目名称">{{ project.title }}</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ project.leader_name }}</el-descriptions-item>
          <el-descriptions-item label="指导教师">
            <span v-for="advisor in project.advisors_info" :key="advisor.id" class="mr-2">
              {{ advisor.name }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="项目任务书">
            <el-link
              v-if="project.task_book_file_url"
              type="primary"
              :href="project.task_book_file_url"
              target="_blank"
            >
              {{ project.task_book_file_name || "下载任务书" }}
            </el-link>
            <span v-else>暂无</span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="form-section">
          <h3>上传中期检查报告</h3>
          <el-alert
            title="请下载模板填写后上传PDF格式文件，大小不超过5MB"
            type="info"
            show-icon
            :closable="false"
            class="mb-4"
          />

          <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
            <el-form-item label="中期报告" prop="mid_term_report">
              <el-upload
                class="upload-demo"
                drag
                action=""
                :auto-upload="false"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                :limit="1"
                accept=".pdf"
                :file-list="fileList"
                :disabled="!canSubmit"
              >
                <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                <div class="el-upload__text">
                  拖拽文件到此处或 <em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    只能上传 pdf 文件，且不超过 5MB
                  </div>
                </template>
              </el-upload>
            </el-form-item>

            <div v-if="project.mid_term_report_url" class="current-file mb-4">
              <span class="label">当前报告：</span>
              <el-link type="primary" :href="project.mid_term_report_url" target="_blank">
                {{ project.mid_term_report_name || '点击查看' }}
              </el-link>
            </div>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="submitForm(false)" 
                :loading="submitting"
                :disabled="!canSubmit"
              >
                提交报告
              </el-button>
              <el-button 
                @click="submitForm(true)" 
                :loading="saving" 
                :disabled="!canSubmit"
              >
                保存草稿
              </el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type UploadUserFile, type UploadFile } from 'element-plus'
import request from '@/utils/request'
import { getProjectDetail } from '@/api/projects'

interface Project {
  id: number
  project_no: string
  title: string
  leader_name: string
  advisors_info: any[]
  status: string
  mid_term_report_url: string
  mid_term_report_name: string
  task_book_file_url: string
  task_book_file_name: string
}

const loading = ref(true)
const submitting = ref(false)
const saving = ref(false)
const project = ref<Project | null>(null)
const formRef = ref<FormInstance>()
const fileList = ref<UploadUserFile[]>([])
const route = useRoute()

const form = ref({
  mid_term_report: null as File | null
})

const rules = {
  mid_term_report: [
    { required: true, message: '请上传中期检查报告', trigger: 'change' }
  ]
}

const canSubmit = computed(() => {
  if (!project.value) return false
  const status = project.value.status
  return ['IN_PROGRESS', 'MID_TERM_DRAFT', 'MID_TERM_REJECTED'].includes(status)
})

const projectId = computed(() => Number(route.query.projectId))
const hasProjectId = computed(() => Number.isFinite(projectId.value) && projectId.value > 0)
const emptyMessage = computed(() =>
  hasProjectId.value ? '未找到项目或无权限' : '请从列表选择需要提交中期检查的项目'
)

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'IN_PROGRESS': 'success',
    'MID_TERM_DRAFT': 'info',
    'MID_TERM_SUBMITTED': 'warning',
    'MID_TERM_REVIEWING': 'warning',
    'MID_TERM_APPROVED': 'success',
    'MID_TERM_REJECTED': 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'IN_PROGRESS': '进行中',
    'MID_TERM_DRAFT': '中期草稿',
    'MID_TERM_SUBMITTED': '已提交',
    'MID_TERM_REVIEWING': '审核中',
    'MID_TERM_APPROVED': '审核通过',
    'MID_TERM_REJECTED': '审核不通过'
  }
  return map[status] || status
}

const fetchProject = async () => {
  try {
    if (!hasProjectId.value) {
      project.value = null
      fileList.value = []
      form.value.mid_term_report = null
      loading.value = false
      return
    }

    loading.value = true
    const res: any = await getProjectDetail(projectId.value)
    if (res?.code === 200) {
      project.value = res.data
      fileList.value = []
      form.value.mid_term_report = null
    } else {
      project.value = null
    }
  } catch (error) {
    console.error('Failed to fetch project', error)
  } finally {
    loading.value = false
  }
}

const handleFileChange = (uploadFile: UploadFile, uploadFiles: UploadUserFile[]) => {
  if (uploadFile.raw) {
    form.value.mid_term_report = uploadFile.raw
    // Clear validation
    formRef.value?.clearValidate('mid_term_report')
  }
  fileList.value = uploadFiles.slice(-1)
}

const handleFileRemove = () => {
  form.value.mid_term_report = null
  fileList.value = []
}

const submitForm = async (isDraft: boolean) => {
  if (!project.value) return

  // Draft doesn't strictly need file if one exists, but let's encourage it.
  // Real submission needs file validation
  if (!isDraft) {
    if (!form.value.mid_term_report && !project.value.mid_term_report_url) {
      ElMessage.warning('请上传中期检查报告')
      return
    }
  }

  const formData = new FormData()
  if (form.value.mid_term_report) {
    formData.append('mid_term_report', form.value.mid_term_report)
  }
  formData.append('is_draft', isDraft.toString())

  try {
    if (isDraft) {
      saving.value = true
    } else {
      submitting.value = true
    }

    await request.post(`/projects/${project.value.id}/apply-mid-term/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    ElMessage.success(isDraft ? '保存成功' : '提交成功')
    fetchProject() // Refresh
    fileList.value = [] // Clear upload list
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '操作失败')
  } finally {
    saving.value = false
    submitting.value = false
  }
}

onMounted(() => {
  fetchProject()
})

watch(
  () => route.query.projectId,
  () => {
    fetchProject()
  }
)
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.midterm-apply-container {
  padding: 20px;
}

.main-card {
  border-radius: 8px;
  :deep(.el-card__header) {
      padding: 16px 20px;
      font-weight: 600;
      border-bottom: 1px solid $color-border-light;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
    display: flex;
    align-items: center;
}

.header-title {
    font-size: 16px;
    color: $slate-800;
}

.content-container {
    .form-section {
      margin-top: 30px;
      
      h3 {
        margin-bottom: 20px;
        padding-left: 10px;
        border-left: 4px solid $primary-500;
        font-size: 16px;
        color: $slate-800;
      }
    }
}

.ml-3 {
    margin-left: 12px;
}
  
.mt-4 {
    margin-top: 16px;
}
  
.mb-4 {
    margin-bottom: 16px;
}
  
.mr-2 {
    margin-right: 8px;
}
</style>
