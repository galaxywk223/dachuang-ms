<template>
  <div class="midterm-review-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>中期检查审核</span>
          <div class="header-actions">
            <el-button type="primary" plain @click="openBatchDialog">批量审核</el-button>
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
        <el-table-column prop="title" label="项目名称" min-width="180"show-overflow-tooltip />
        <el-table-column prop="leader_name" label="负责人" width="100" />
        <el-table-column prop="college" label="学院" width="150" show-overflow-tooltip />
        <el-table-column prop="submitted_at" label="提交时间" width="160">
           <template #default="scope">
              {{ formatDate(scope.row.mid_term_submitted_at) }}
           </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              @click="handleReview(scope.row)"
            >
              审核
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
          <el-button @click="submitReview(false)" type="danger" :loading="reviewing">不通过</el-button>
          <el-button type="primary" @click="submitReview(true)" :loading="reviewing">
            通 过
          </el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="batchDialogVisible" title="批量审核" width="520px">
      <el-form label-position="top">
        <el-form-item label="审核结果">
          <el-radio-group v-model="batchForm.action">
            <el-radio label="approve">通过</el-radio>
            <el-radio label="reject">驳回</el-radio>
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
import request from '@/utils/request'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchQuery = ref('')
const dialogVisible = ref(false)
const currentRow = ref<any>(null)
const reviewComments = ref('')
const reviewing = ref(false)
const selectedRows = ref<any[]>([])

const batchDialogVisible = ref(false)
const batchSubmitting = ref(false)
const batchForm = ref({
  action: 'approve',
  comments: ''
})

const formatDate = (dateStr: string) => {
  if(!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

const fetchData = async () => {
    loading.value = true
    try {
        // 查询项目（当前后端实现更确定：中期申请会将项目置为 MID_TERM_REVIEWING）
        
        // ADMIN Logic:
        // Level 2 Admin (College) sees MID_TERM_REVIEWING (after submission/teacher check?).
        // Wait, our service implementation:
        // apply_mid_term -> MID_TERM_SUBMITTED -> (if auto approved or teacher step?)
        // ReviewService.create_mid_term_review sets status to MID_TERM_REVIEWING.
        // So Admin should look for status='MID_TERM_REVIEWING'.
        
        const projectParams = {
           page: currentPage.value,
           page_size: pageSize.value,
           status: 'MID_TERM_REVIEWING',
           search: searchQuery.value
        }
        
        const res = await request.get('/projects/', { params: projectParams })
        const projectPayload = res.data || res
        const results = projectPayload.results || projectPayload.data?.results || []
        tableData.value = results
        total.value = projectPayload.count || projectPayload.data?.count || 0
        selectedRows.value = []

        const reviewRes: any = await request.get('/reviews/', {
          params: { review_type: 'MID_TERM', status: 'PENDING' }
        })
        const reviewPayload = reviewRes.data || reviewRes
        const reviewRecords = Array.isArray(reviewPayload)
          ? reviewPayload
          : (reviewPayload.results || reviewPayload.data?.results || reviewPayload.data || [])
        const reviewMap = new Map(reviewRecords.map((r: any) => [r.project, r.id]))
        tableData.value = results.map((item: any) => ({
          ...item,
          review_id: reviewMap.get(item.id)
        }))

    } catch(err) {
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

const handleReview = (row: any) => {
  currentRow.value = row
  reviewComments.value = ''
  dialogVisible.value = true
}

const submitReview = async (approved: boolean) => {
  if (!currentRow.value) return
  
  reviewing.value = true
  try {
     const reviewId = currentRow.value.review_id
     if (!reviewId) {
       ElMessage.error('未找到审核记录')
       return
     }
     await request.post(`/reviews/${reviewId}/review/`, {
        action: approved ? 'approve' : 'reject',
        comments: reviewComments.value
     })
     
     ElMessage.success('审核完成')
     dialogVisible.value = false
     fetchData()

  } catch(err: any) {
    ElMessage.error(err.response?.data?.message || '操作失败')
  } finally {
    reviewing.value = false
  }
}

onMounted(() => {
  fetchData()
})

const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
}

const openBatchDialog = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先勾选要审核的项目')
    return
  }
  batchForm.value = { action: 'approve', comments: '' }
  batchDialogVisible.value = true
}

const submitBatchReview = async () => {
  if (selectedRows.value.length === 0) return
  batchSubmitting.value = true
  try {
    const reviewIds = selectedRows.value
      .map((row) => row.review_id)
      .filter((id) => !!id)
    if (reviewIds.length === 0) {
      ElMessage.warning('未找到可审核的记录')
      return
    }
    const payload = {
      review_ids: reviewIds,
      action: batchForm.value.action,
      comments: batchForm.value.comments
    }
    const res: any = await request.post('/reviews/batch-review/', payload)
    if (res.code === 200) {
      ElMessage.success('批量审核完成')
      batchDialogVisible.value = false
      selectedRows.value = []
      fetchData()
    }
  } catch (err: any) {
    ElMessage.error(err.response?.data?.message || '批量审核失败')
  } finally {
    batchSubmitting.value = false
  }
}

</script>

<style scoped>
.mb-4 { margin-bottom: 16px; }
.mt-4 { margin-top: 16px; }
.mr-2 { margin-right: 8px; }
.pagination-container {
  display: flex;
  justify-content: flex-end;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
