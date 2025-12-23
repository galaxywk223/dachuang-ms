<template>
  <div class="midterm-review-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>中期检查审核</span>
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
      >
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
        tableData.value = res.data.results
        total.value = res.data.count

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
     // We need to find the pending review ID for this project.
     // OR call an action on the project like /projects/{id}/review_midterm/ 
     // BUT backend `approve_review` operates on Review object.
     // So we must find the Review ID.
     
     // Let's fetch the review object for this project first.
     const reviewRes: any = await request.get('/reviews/', { 
        params: { 
           project: currentRow.value.id, 
           review_type: 'MID_TERM', 
           status: 'PENDING' 
        } 
     })

     const payload = reviewRes.data || reviewRes
     const records = Array.isArray(payload) ? payload : (payload.results || payload.data?.results || payload.data || [])
     if (records.length > 0) {
         const reviewId = records[0].id
         await request.post(`/reviews/${reviewId}/review/`, {
            action: approved ? 'approve' : 'reject',
            comments: reviewComments.value
         })
         
         ElMessage.success('审核完成')
         dialogVisible.value = false
         fetchData()
     } else {
         ElMessage.error('未找到审核记录')
     }

  } catch(err: any) {
    ElMessage.error(err.response?.data?.message || '操作失败')
  } finally {
    reviewing.value = false
  }
}

onMounted(() => {
  fetchData()
})

</script>

<style scoped>
.mb-4 { margin-bottom: 16px; }
.mt-4 { margin-top: 16px; }
.mr-2 { margin-right: 8px; }
.pagination-container {
  display: flex;
  justify-content: flex-end;
}
</style>
