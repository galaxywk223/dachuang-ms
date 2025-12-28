<template>
  <div class="midterm-review-container">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
             <span class="header-title">中期检查审核</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" plain @click="openBatchDialog">批量确认</el-button>
          </div>
        </div>
      </template>

      <div class="filter-container mb-4">
         <el-input
          v-model="searchQuery"
          placeholder="搜索项目名称/编号"
          style="width: 200px"
          class="mr-2"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column prop="project_no" label="项目编号" width="140" />
        <el-table-column prop="title" label="项目名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="leader_name" label="负责人" width="100" />
        <el-table-column prop="college" label="学院" width="150" show-overflow-tooltip />
        <el-table-column prop="submitted_at" label="提交时间" width="160">
           <template #default="scope">
              {{ formatDate(scope.row.mid_term_submitted_at) }}
           </template>
        </el-table-column>
        <el-table-column label="专家评审" width="160">
          <template #default="scope">
            <el-tag v-if="(scope.row.expert_summary?.assigned || 0) === 0" type="info">未分配</el-tag>
            <el-tag
              v-else
              :type="scope.row.expert_summary?.all_submitted ? 'success' : 'warning'"
            >
              {{ scope.row.expert_summary?.submitted || 0 }}/{{ scope.row.expert_summary?.assigned || 0 }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              @click="handleReview(scope.row)"
            >
              确认
            </el-button>
          </template>
        </el-table-column>
      </el-table>

       <div class="pagination-container mt-4">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Review Dialog -->
    <el-dialog
      v-model="dialogVisible"
      title="中期检查审核"
      width="50%"
    >
      <div v-if="currentRow" class="review-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="项目名称">{{ currentRow.title }}</el-descriptions-item>
           <el-descriptions-item label="中期报告">
             <el-link type="primary" :href="currentRow.mid_term_report_url" target="_blank">
               {{ currentRow.mid_term_report_name || '下载报告' }}
             </el-link>
           </el-descriptions-item>
        </el-descriptions>
        
        <el-form class="mt-4" label-width="80px">
           <el-form-item label="审核意见">
             <el-input 
                v-model="reviewComments" 
                type="textarea" 
                :rows="3" 
                placeholder="请输入审核意见"
             />
           </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="submitFinalize('return')" type="danger" :loading="reviewing">退回学生</el-button>
          <el-button type="primary" @click="submitFinalize('pass')" :loading="reviewing">确认通过</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="batchDialogVisible" title="批量确认" width="520px">
      <el-form label-position="top">
        <el-form-item label="审核结果">
          <el-radio-group v-model="batchForm.action">
            <el-radio label="pass">确认通过</el-radio>
            <el-radio label="return">退回学生</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="batchForm.comments" type="textarea" :rows="4" placeholder="请输入审核意见" />
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { getProjects } from '@/api/projects'
import { finalizeMidterm, getProjectExpertSummary } from '@/api/projects/midterm'
import dayjs from 'dayjs'

type ExpertSummary = {
  assigned?: number
  submitted?: number
  all_submitted?: boolean
}

type ProjectRow = {
  id: number
  project_no?: string
  title?: string
  leader_name?: string
  college?: string
  mid_term_submitted_at?: string
  mid_term_report_url?: string
  mid_term_report_name?: string
  expert_summary?: ExpertSummary | null
}

type ProjectListPayload = {
  results?: ProjectRow[]
  count?: number
  data?: {
    results?: ProjectRow[]
    count?: number
  }
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

const resolveListPayload = (payload: unknown): ProjectListPayload =>
  (isRecord(payload) ? (payload as ProjectListPayload) : {})

const resolveList = (payload: unknown): ProjectRow[] => {
  if (!isRecord(payload)) return []
  if (Array.isArray((payload as ProjectListPayload).results)) {
    return (payload as ProjectListPayload).results ?? []
  }
  if (isRecord((payload as ProjectListPayload).data)) {
    const data = (payload as ProjectListPayload).data
    if (Array.isArray(data?.results)) {
      return data?.results ?? []
    }
  }
  return []
}

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback
  const response = error.response
  if (isRecord(response) && isRecord(response.data) && typeof response.data.message === 'string') {
    return response.data.message
  }
  if (typeof error.message === 'string') return error.message
  return fallback
}

const loading = ref(false)
const tableData = ref<ProjectRow[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchQuery = ref('')
const dialogVisible = ref(false)
const currentRow = ref<ProjectRow | null>(null)
const reviewComments = ref('')
const reviewing = ref(false)
const selectedRows = ref<ProjectRow[]>([])
const router = useRouter()

const batchDialogVisible = ref(false)
const batchSubmitting = ref(false)
const batchForm = ref({
  action: 'pass',
  comments: ''
})

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

const fetchData = async () => {
    loading.value = true
    try {
        const projectParams = {
           page: currentPage.value,
           page_size: pageSize.value,
           status: 'MID_TERM_REVIEWING',
           search: searchQuery.value,
           phase: 'MID_TERM'
        }
        
        const res = await getProjects(projectParams)
        const projectPayload = resolveListPayload(isRecord(res) && 'data' in res ? res.data : res)
        const results = resolveList(projectPayload)
        // Load expert summary for each project
        const enriched = await Promise.all(
          results.map(async (item) => {
            try {
              const s = await getProjectExpertSummary(item.id, {
                review_type: 'MID_TERM',
                scope: 'COLLEGE'
              })
              const sp = isRecord(s) && 'data' in s ? s.data : s
              return { ...item, expert_summary: isRecord(sp) ? (sp as ExpertSummary) : null }
            } catch {
              return { ...item, expert_summary: null }
            }
          })
        )
        tableData.value = enriched
        total.value = projectPayload.count || projectPayload.data?.count || 0
        selectedRows.value = []

    } catch (err) {
        console.error(err)
        ElMessage.error('获取列表失败')
    } finally {
        loading.value = false
    }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchData()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchData()
}

const handleReview = (row: ProjectRow) => {
  const summary = row?.expert_summary
  if (!summary || (summary.assigned || 0) === 0) {
    ElMessage.warning('请先到“院系评审分配”分配专家组')
    router.push({ path: '/level2-admin/expert/assignment', query: { reviewType: 'MID_TERM' } })
    return
  }
  if (!summary.all_submitted) {
    ElMessage.warning('专家评审尚未全部提交')
    return
  }
  currentRow.value = row
  reviewComments.value = ''
  dialogVisible.value = true
}

const submitFinalize = async (action: 'pass' | 'return') => {
  if (!currentRow.value) return
  
  reviewing.value = true
  try {
     await finalizeMidterm(currentRow.value.id, {
       action,
       reason: reviewComments.value
     })
     ElMessage.success('操作完成')
     dialogVisible.value = false
     fetchData()

  } catch (err) {
    ElMessage.error(getErrorMessage(err, '操作失败'))
  } finally {
    reviewing.value = false
  }
}

onMounted(() => {
  fetchData()
})

const handleSelectionChange = (rows: ProjectRow[]) => {
  selectedRows.value = rows
}

const openBatchDialog = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先勾选要确认的项目')
    return
  }
  batchForm.value = { action: 'pass', comments: '' }
  batchDialogVisible.value = true
}

const submitBatchReview = async () => {
  if (selectedRows.value.length === 0) return
  batchSubmitting.value = true
  try {
    const readyRows = selectedRows.value.filter((row) => {
      const s = row?.expert_summary
      return s && (s.assigned || 0) > 0 && !!s.all_submitted
    })
    const skipped = selectedRows.value.length - readyRows.length
    if (readyRows.length === 0) {
      ElMessage.warning('所选项目均未完成专家评审或未分配专家')
      return
    }

    await Promise.all(
      readyRows.map((row) =>
        finalizeMidterm(row.id, {
          action: batchForm.value.action as 'pass' | 'return',
          reason: batchForm.value.comments,
        })
      )
    )

    ElMessage.success(skipped ? `批量完成（跳过${skipped}条未就绪）` : '批量完成')
    batchDialogVisible.value = false
    selectedRows.value = []
    fetchData()
  } catch (err) {
    ElMessage.error(getErrorMessage(err, '批量确认失败'))
  } finally {
    batchSubmitting.value = false
  }
}

</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.midterm-review-container {
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

.header-actions {
    display: flex;
    align-items: center;
}

.mb-4 { margin-bottom: 16px; }
.mt-4 { margin-top: 16px; }
.mr-2 { margin-right: 8px; }

.pagination-container {
  display: flex;
  justify-content: flex-end;
}
</style>
