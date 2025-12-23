<template>
  <div class="expert-assignment-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="title">专家评审分配</span>
          <div class="header-actions">
              <el-select v-model="selectedGroup" placeholder="选择专家组" style="width: 200px" class="mr-2">
                 <el-option
                    v-for="group in groups"
                    :key="group.id"
                    :label="group.name"
                    :value="group.id"
                 />
              </el-select>
              <el-select v-model="reviewType" placeholder="审核类型" style="width: 150px" class="mr-2">
                 <el-option label="申报审核" value="APPLICATION" />
                 <el-option label="中期审核" value="MID_TERM" />
                 <el-option label="结题审核" value="CLOSURE" />
              </el-select>
              <el-button 
                type="primary" 
                @click="handleAssign" 
                :disabled="!selectedGroup || selectedProjects.length === 0"
                :loading="assigning"
              >
                 批量分配 ({{ selectedProjects.length }})
              </el-button>
          </div>
        </div>
      </template>
      
      <!-- Filters -->
      <div class="filter-container mb-4">
         <el-input v-model="searchQuery" placeholder="搜索项目名称/编号" style="width: 300px" clearable @clear="fetchProjects" @keyup.enter="fetchProjects">
             <template #append>
                <el-button @click="fetchProjects"><el-icon><Search /></el-icon></el-button>
             </template>
         </el-input>
         
         <el-select v-model="statusFilter" placeholder="项目状态" class="ml-2" @change="fetchProjects" clearable>
             <el-option label="待提交" value="DRAFT" />
             <el-option label="已提交" value="SUBMITTED" />
             <el-option label="进行中" value="IN_PROGRESS" />
             <!-- Add more as needed -->
         </el-select>
      </div>

      <el-table 
        v-loading="loading" 
        :data="projects" 
        style="width: 100%" 
        stripe 
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="project_no" label="项目编号" width="150" />
        <el-table-column prop="title" label="项目名称" min-width="200" show-overflow-tooltip/>
        <el-table-column prop="leader_name" label="负责人" width="120" />
        <el-table-column prop="college" label="学院" width="150" />
        <el-table-column prop="level_name" label="级别" width="100" />
        <el-table-column prop="status_display" label="当前状态" width="120">
           <template #default="scope">
              <el-tag>{{ scope.row.status_display }}</el-tag>
           </template>
        </el-table-column>
      </el-table>
      
       <div class="pagination-container mt-4">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="fetchProjects"
          @current-change="fetchProjects"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Search } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '@/utils/request';

const loading = ref(false);
const assigning = ref(false);
const projects = ref<any[]>([]);
const groups = ref<any[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);

// Filters and Selections
const searchQuery = ref("");
const statusFilter = ref("");
const selectedGroup = ref<number | null>(null);
const reviewType = ref("APPLICATION");
const selectedProjects = ref<any[]>([]);

const fetchGroups = async () => {
    try {
        const { data } = await request.get('/reviews/groups/');
        groups.value = data.results || data;
    } catch (e) {
        console.error(e);
    }
};

const fetchProjects = async () => {
    loading.value = true;
    try {
        const params: any = {
            page: currentPage.value,
            page_size: pageSize.value,
            search: searchQuery.value,
        };
        if (statusFilter.value) {
            params.status = statusFilter.value;
        }
        
        // Optionally filter by projects needing review?
        // Usually review assignment happens when project is SUBMITTED or similar status.
        
        const { data } = await request.get('/projects/', { params });
        projects.value = data.results;
        total.value = data.count;
    } catch (e) {
        console.error(e);
        ElMessage.error("获失败");
    } finally {
        loading.value = false;
    }
};

const handleSelectionChange = (val: any[]) => {
    selectedProjects.value = val;
};

const handleAssign = () => {
    if (!selectedGroup.value || selectedProjects.length === 0) return;
    
    ElMessageBox.confirm(
       `确定将选中的 ${selectedProjects.length} 个项目分配给该专家组进行 "${reviewType.value}" 评审吗？`, 
       "提示",
       { confirmButtonText: "确定", cancelButtonText: "取消", type: "warning" }
    ).then(async () => {
        assigning.value = true;
        try {
            const projectIds = selectedProjects.value.map(p => p.id);
            const { data } = await request.post('/reviews/assignments/assign_batch/', {
                project_ids: projectIds,
                group_id: selectedGroup.value,
                review_type: reviewType.value
            });
            ElMessage.success(data.message || "分配成功");
            // Clear selection?
        } catch (error: any) {
            console.error(error);
            ElMessage.error(error.response?.data?.message || "分配失败");
        } finally {
            assigning.value = false;
        }
    });
};

onMounted(() => {
    fetchGroups();
    fetchProjects();
});

</script>

<style scoped lang="scss">
.expert-assignment-container {
    padding: 20px;
    
    .card-header {
       display: flex;
       justify-content: space-between;
       align-items: center;
       
       .header-actions {
           display: flex;
           align-items: center;
       }
    }
    
    .mr-2 { margin-right: 10px; }
    .ml-2 { margin-left: 10px; }
    .mt-4 { margin-top: 16px; }
    .mb-4 { margin-bottom: 16px; }
    
    .pagination-container {
        display: flex;
        justify-content: flex-end;
    }
}
</style>
