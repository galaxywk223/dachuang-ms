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
                <el-table-column v-if="showCode" prop="value" label="代码" min-width="120" />
                <el-table-column v-if="currentType?.code === 'project_level'" label="预算(元)" min-width="100">
                    <template #default="{ row }">
                        {{ (row.extra_data && row.extra_data.budget) ? row.extra_data.budget : '-' }}
                    </template>
                </el-table-column>
                <!-- <el-table-column prop="sort_order" label="排序" width="80" align="center" /> -->
                
                <el-table-column label="操作" width="160" align="center" fixed="right">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="editItem(row)">编辑</el-button>
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

    <!-- Add/Edit Item Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑条目' : `添加 ${currentType?.name || ''} 条目`"
      width="500px"
      align-center
      destroy-on-close
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="label">
          <el-input v-model="form.label" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item v-if="showCode" label="代码" prop="value">
          <el-input v-model="form.value" placeholder="请输入代码" />
        </el-form-item>
        <el-form-item v-if="showBudget" label="经费预算" prop="budget">
           <el-input-number v-model="form.budget" :min="0" :step="100" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item v-if="showTemplate" label="申请书模板">
           <el-upload
              ref="uploadRef"
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleRemoveFile"
              :file-list="fileList"
              :limit="1"
           >
              <template #trigger>
                 <el-button type="primary" plain>选择文件</el-button>
              </template>
              <template #tip>
                 <div class="el-upload__tip">只能上传 PDF/Word 文件，且不超过 5MB</div>
              </template>
           </el-upload>
        </el-form-item>
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
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { Plus, Collection, ArrowRight, Upload, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules, type UploadFile } from 'element-plus'
import request from '@/utils/request'
import { 
    DICT_CODES, 
    createDictionaryItem, 
    updateDictionaryItem, 
    deleteDictionaryItem 
} from '@/api/dictionary'

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
  extra_data?: any
  template_file?: string | null // URL
}

const dictionaryTypes = ref<DictionaryType[]>([])
const currentType = ref<DictionaryType | null>(null)
const items = ref<DictionaryItem[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const submitting = ref(false)
const isEditMode = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const uploadRef = ref()

const selectedFile = ref<File | null>(null)
const fileList = ref<any[]>([])

// Types that require explicit Code input
const CODE_BASED_TYPES = ['major_category', 'key_field_code']

// Computed property to check if current type needs Code field
const showCode = computed(() => {
  if (!currentType.value) return false
  return CODE_BASED_TYPES.includes(currentType.value.code)
})

const showBudget = computed(() => currentType.value?.code === 'project_level')
const showTemplate = computed(() => currentType.value?.code === DICT_CODES.PROJECT_CATEGORY)

const form = reactive({
  label: '',
  value: '',
  description: '',
  sort_order: 0,
  budget: 0,
})

// Dynamic rules based on showCode
const rules = computed<FormRules>(() => {
  const baseRules: FormRules = {
    label: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  }
  
  if (showCode.value) {
    baseRules.value = [{ required: true, message: '请输入代码', trigger: 'blur' }]
  }
  
  return baseRules
})


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
    // Auto-sort by sort_order if backend doesn't sorting logic.
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
  isEditMode.value = false
  editingId.value = null
  resetFormState()
  dialogVisible.value = true
}

const editItem = (item: DictionaryItem) => {
  isEditMode.value = true
  editingId.value = item.id
  form.label = item.label
  form.value = item.value
  form.description = item.description || ''
  form.sort_order = item.sort_order
  
  // Load budget from extra_data if available
  if (item.extra_data && typeof item.extra_data === 'object') {
      form.budget = (item.extra_data as any).budget || 0
  } else {
      form.budget = 0
  }

  // Handle file list for display
  fileList.value = []
  if (item.template_file) {
      const fileName = item.template_file.split('/').pop() || 'template.pdf';
      fileList.value = [{ name: fileName, url: item.template_file }];
  }
  
  dialogVisible.value = true
}

const resetFormState = () => {
  form.label = ''
  form.value = ''
  form.description = ''
  form.sort_order = 0
  form.budget = 0
  selectedFile.value = null
  fileList.value = []
}

const resetForm = () => {
  resetFormState()
  formRef.value?.clearValidate()
}

const handleFileChange = (file: UploadFile) => {
    selectedFile.value = file.raw || null;
}

const handleRemoveFile = () => {
    selectedFile.value = null;
}

const submitForm = async () => {
  if (!formRef.value || !currentType.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        const finalValue = showCode.value ? form.value : form.label

        // Prepare extra_data
        let extraData: any = {}
        if (showBudget.value) {
            extraData.budget = Number(form.budget) || 0
        }

        // Prepare Payload
        // If file is selected, use FormData
        let payload: any;
        const isFormData = !!selectedFile.value || (isEditMode.value && selectedFile.value !== undefined); // Simple check: if file is picked, we must use FormData.

        if (selectedFile.value) {
            payload = new FormData();
            payload.append('label', form.label);
            payload.append('value', finalValue);
            payload.append('sort_order', String(isEditMode.value && editingId.value ? form.sort_order : items.value.length + 1));
            payload.append('extra_data', JSON.stringify(extraData));
            payload.append('dict_type', String(currentType.value!.id));
            payload.append('description', form.description || '');
            payload.append('is_active', 'true');
            if (selectedFile.value) {
                payload.append('template_file', selectedFile.value);
            }
        } else {
            // JSON fallback if no file change? 
            // Actually, for consistency, let's use JSON if no file is new, 
            // but updateDictionaryItem handles FormData check.
            // If we are editing and didn't change file, we don't send template_file field.
            payload = {
                label: form.label,
                value: finalValue,
                sort_order: isEditMode.value && editingId.value ? form.sort_order : items.value.length + 1,
                extra_data: extraData,
                dict_type: currentType.value!.id,
                description: form.description || '',
                is_active: true
            }
        }

        if (isEditMode.value && editingId.value) {
          await updateDictionaryItem(editingId.value, payload);
          ElMessage.success('修改成功')
        } else {
          await createDictionaryItem(payload);
          ElMessage.success('添加成功')
        }
        
        dialogVisible.value = false
        await fetchItems(currentType.value!.code)
      } catch (error) {
        console.error(error);
        ElMessage.error(isEditMode.value ? '修改失败' : '添加失败')
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
    
    await deleteDictionaryItem(item.id);
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
        margin-top: 4px;
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
