<template>
  <div class="dictionary-page">
    <div class="page-header-wrapper">
       <div class="title-bar">
          <span class="title">系统字典管理</span>
       </div>
    </div>

    <div class="content-container">
      <el-row :gutter="20">
        <!-- Dictionary Types List -->
        <el-col :span="6">
          <el-card class="types-card" shadow="never" :body-style="{ padding: '0' }">
            <template #header>
              <div class="card-header">
                <span>字典类型</span>
              </div>
            </template>
            <div class="types-list">
              <div
                v-for="type in dictionaryTypes"
                :key="type.code"
                class="type-item"
                :class="{ active: currentType?.code === type.code }"
                @click="handleTypeSelect(type)"
              >
                <el-icon class="icon"><Collection /></el-icon>
                <span class="type-name">{{ type.name }}</span>
                <el-icon class="arrow"><ArrowRight /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- Dictionary Items Management -->
        <el-col :span="18">
          <el-card class="items-card" shadow="never">
            <template #header>
              <div class="items-header">
                <div class="left-panel">
                  <span class="type-title">{{ currentType?.name || '请选择左侧字典类型' }}</span>
                  <span class="type-desc" v-if="currentType">{{ currentType.description }}</span>
                </div>
                <div class="right-panel" v-if="currentType">
                   <el-button type="primary" @click="openAddDialog">
                     <el-icon><Plus /></el-icon> 添加条目
                   </el-button>
                </div>
              </div>
            </template>

            <!-- Items Table -->
            <div v-if="currentType">
              <el-table
                v-loading="loading"
                :data="items"
                style="width: 100%"
                stripe
                border
                :header-cell-style="{ background: '#f8fafc', color: '#475569', fontWeight: '600' }"
              >
                <el-table-column prop="label" label="显示名称" min-width="150" />
                <!-- User requested to only show Name and Delete -->
                <!-- <el-table-column prop="value" label="值" min-width="120" /> -->
                <!-- <el-table-column prop="sort_order" label="排序" width="80" align="center" /> -->
                
                <el-table-column label="操作" width="100" align="center" fixed="right">
                  <template #default="{ row }">
                    <el-button link type="danger" size="small" @click="deleteItem(row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
              
              <div class="empty-tip" v-if="!loading && items.length === 0">
                暂无数据
              </div>
            </div>
            <div v-else class="empty-selection">
              <el-empty description="请选择左侧的字典类型进行管理" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Add Item Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="`添加 ${currentType?.name || ''} 条目`"
      width="500px"
      align-center
      destroy-on-close
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="label">
          <el-input v-model="form.label" placeholder="请输入名称" />
        </el-form-item>
        <!-- Value is hidden and defaults to label -->
        
        <!-- Sort Order is auto-calculated -->
        
        <!-- Description is removed as requested -->
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { Plus, Collection, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import request from '@/utils/request'

interface DictionaryType {
  id: number
  code: string
  name: string
  description: string
}

interface DictionaryItem {
  id: number
  dict_type: number
  label: string
  value: string
  description?: string
  sort_order: number
  is_active: boolean
}

const dictionaryTypes = ref<DictionaryType[]>([])
const currentType = ref<DictionaryType | null>(null)
const items = ref<DictionaryItem[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  label: '',
  value: '',
  description: '',
  sort_order: 0,
})

const rules: FormRules = {
  label: [{ required: true, message: '请输入名称', trigger: 'blur' }],
}

onMounted(async () => {
  await fetchTypes()
})

watch(currentType, async (newType) => {
  if (newType) {
    await fetchItems(newType.code)
  } else {
    items.value = []
  }
})

const fetchTypes = async () => {
  try {
    const response = await request.get('/dictionaries/types/')
    // Handle various response structures
    const list = (response as any)?.data?.results 
       ?? (response as any)?.results 
       ?? (response as any)?.data 
       ?? response;
       
    dictionaryTypes.value = Array.isArray(list) ? list : []
    
    if (dictionaryTypes.value.length > 0) {
      currentType.value = dictionaryTypes.value[0]
    }
  } catch (error) {
    console.error('Failed to fetch dictionary types:', error)
    ElMessage.error('获取字典类型失败')
  }
}

const fetchItems = async (typeCode: string) => {
  loading.value = true
  try {
    const response = await request.get('/dictionaries/items/', {
      params: { dict_type_code: typeCode },
    })
    const list = (response as any)?.data?.results 
       ?? (response as any)?.results 
       ?? (response as any)?.data 
       ?? response;
    // Auto-sort by sort_order if backend doesn't, though backend likely does. 
    // If user wants automatic sorting, we often just rely on backend creation order or explicit sort logic there.
    // For now, simple display.
    items.value = Array.isArray(list) ? list : []
  } catch (error) {
    console.error('Failed to fetch items:', error)
    ElMessage.error('获取字典数据失败')
  } finally {
    loading.value = false
  }
}

const handleTypeSelect = (type: DictionaryType) => {
  currentType.value = type
}

const openAddDialog = () => {
  dialogVisible.value = true
}

const resetForm = () => {
  form.label = ''
  form.value = ''
  form.description = ''
  form.sort_order = 0 // Keeping internal state for type safety, but not used in UI
  formRef.value?.clearValidate()
}

const submitForm = async () => {
  if (!formRef.value || !currentType.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        // Calculate a simple auto-sort order (append to end)
        // Or just let backend use default 0. 
        // Logic: if we want "automatic", usually means "append". 
        // We'll set sort_order to items.length + 1 to put it at the end visually if backend sorts by it.
        const nextOrder = items.value.length + 1;

        await request.post('/dictionaries/items/', {
          dict_type: currentType.value!.id,
          label: form.label,
          value: form.label, // Value = Name
          description: '',   // Empty description
          sort_order: nextOrder,
          is_active: true,
        })
        ElMessage.success('添加成功')
        dialogVisible.value = false
        await fetchItems(currentType.value!.code)
      } catch (error) {
        ElMessage.error('添加失败，可能该名称已存在')
      } finally {
        submitting.value = false
      }
    }
  })
}

const deleteItem = async (item: DictionaryItem) => {
  try {
    await ElMessageBox.confirm(`确认要删除 "${item.label}" 吗？此操作不可恢复。`, '警告', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    
    await request.delete(`/dictionaries/items/${item.id}/`)
    ElMessage.success('删除成功')
    if (currentType.value) {
      await fetchItems(currentType.value.code)
    }
  } catch (error) {
    if (error !== 'cancel') {
        ElMessage.error('删除失败，可能该条目正在被使用')
    }
  }
}
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.dictionary-page {
  /* Inherit layout margins */
}

.page-header-wrapper {
  background: white;
  padding: 16px 24px;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  border: 1px solid $color-border-light;
  margin-bottom: 20px;
  
  .title-bar {
      display: flex;
      align-items: center;
      
      .title {
          font-size: 18px;
          font-weight: 600;
          color: $slate-800;
          position: relative;
          padding-left: 14px;
          
          &::before {
              content: '';
              position: absolute;
              left: 0;
              top: 50%;
              transform: translateY(-50%);
              width: 4px;
              height: 18px;
              background: $primary-600;
              border-radius: 2px;
          }
      }
  }
}

.types-card {
  min-height: 600px;
  border-radius: $radius-lg;
  
  .card-header {
    font-weight: 600;
    font-size: 16px;
    color: $slate-800;
  }
  
  .types-list {
    .type-item {
      display: flex;
      align-items: center;
      padding: 12px 20px;
      cursor: pointer;
      border-bottom: 1px solid $slate-50;
      transition: all 0.2s;
      
      &:hover {
        background-color: $slate-50;
        color: $primary-600;
      }
      
      &.active {
        background-color: #ecf5ff; // Element Plus primary light
        color: $primary-600;
        border-right: 3px solid $primary-600;
      }
      
      .icon {
        margin-right: 12px;
        font-size: 16px;
      }
      
      .type-name {
        flex: 1;
        font-size: 14px;
      }
      
      .arrow {
        font-size: 14px;
        color: $slate-400;
      }
    }
  }
}

.items-card {
  min-height: 600px;
  border-radius: $radius-lg;

  .items-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .left-panel {
      .type-title {
        font-size: 18px;
        font-weight: 600;
        color: $slate-800;
        margin-right: 12px;
      }
      
      .type-desc {
        color: $slate-500;
        font-size: 13px;
      }
    }
  }
}

.empty-tip {
  padding: 40px;
  text-align: center;
  color: $slate-400;
}

.empty-selection {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 500px;
}
</style>
