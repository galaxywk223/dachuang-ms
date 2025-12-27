<template>
  <div class="review-templates-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">评审模板</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="openTemplateDialog">新建模板</el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="never" class="panel-card">
            <template #header>
              <div class="panel-header">模板列表</div>
            </template>
            <el-scrollbar height="540px">
              <div
                v-for="item in templates"
                :key="item.id"
                class="list-item"
                :class="{ active: currentTemplate?.id === item.id }"
                @click="selectTemplate(item)"
              >
                <div class="item-title">{{ item.name }}</div>
                <div class="item-meta">
                  <el-tag size="small" effect="plain">{{ item.review_type }}</el-tag>
                  <el-tag size="small" effect="plain" type="info">{{ item.review_level }}</el-tag>
                </div>
              </div>
            </el-scrollbar>
          </el-card>
        </el-col>

        <el-col :span="18">
          <el-card shadow="never" class="panel-card">
            <template #header>
              <div class="panel-header">
                <span>评分项配置</span>
                <div class="header-actions">
                  <el-button type="primary" plain :disabled="!currentTemplate" @click="openItemDialog">
                    新增评分项
                  </el-button>
                </div>
              </div>
            </template>

            <div v-if="!currentTemplate" class="empty-state">
              <el-empty description="请选择模板" />
            </div>

            <div v-else class="node-list">
              <div
                v-for="(item, index) in items"
                :key="item.id"
                class="node-item"
                draggable="true"
                @dragstart="handleDragStart(index)"
                @dragover.prevent
                @drop="handleDrop(index)"
              >
                <div class="node-handle">⋮⋮</div>
                <div class="node-content">
                  <div class="node-title">{{ item.title }}</div>
                  <div class="node-meta">
                    <el-tag size="small" effect="plain">权重 {{ item.weight }}</el-tag>
                    <el-tag size="small" effect="plain" type="info">满分 {{ item.max_score }}</el-tag>
                    <el-tag v-if="item.is_required" size="small" effect="plain" type="danger">必填</el-tag>
                  </div>
                </div>
                <div class="node-actions">
                  <el-button link type="primary" @click="editItem(item)">编辑</el-button>
                  <el-button link type="danger" @click="removeItem(item)">删除</el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="templateDialogVisible" title="评审模板" width="520px" destroy-on-close>
      <el-form :model="templateForm" label-width="120px">
        <el-form-item label="模板名称">
          <el-input v-model="templateForm.name" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="评审类型">
          <el-select v-model="templateForm.review_type" placeholder="请选择">
            <el-option label="立项" value="APPLICATION" />
            <el-option label="中期" value="MID_TERM" />
            <el-option label="结题" value="CLOSURE" />
          </el-select>
        </el-form-item>
        <el-form-item label="评审级别">
          <el-select v-model="templateForm.review_level" placeholder="请选择">
            <el-option label="导师" value="TEACHER" />
            <el-option label="二级" value="LEVEL2" />
            <el-option label="一级" value="LEVEL1" />
          </el-select>
        </el-form-item>
        <el-form-item label="范围">
          <el-select v-model="templateForm.scope" placeholder="请选择">
            <el-option label="院级" value="COLLEGE" />
            <el-option label="校级" value="SCHOOL" />
          </el-select>
        </el-form-item>
        <el-form-item label="注意事项">
          <el-input v-model="templateForm.notice" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="templateDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="itemDialogVisible" title="评分项" width="520px" destroy-on-close>
      <el-form :model="itemForm" label-width="120px">
        <el-form-item label="评分项">
          <el-input v-model="itemForm.title" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="itemForm.weight" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="最高分">
          <el-input-number v-model="itemForm.max_score" :min="0" />
        </el-form-item>
        <el-form-item label="必填">
          <el-switch v-model="itemForm.is_required" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="itemForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="itemDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveItem">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  getReviewTemplates,
  createReviewTemplate,
  updateReviewTemplate,
  getReviewTemplateItems,
  createReviewTemplateItem,
  updateReviewTemplateItem,
  deleteReviewTemplateItem,
  reorderReviewTemplateItems,
} from "@/api/system-settings";

const templates = ref<any[]>([]);
const currentTemplate = ref<any | null>(null);
const items = ref<any[]>([]);
const saving = ref(false);
const dragIndex = ref<number | null>(null);

const templateDialogVisible = ref(false);
const itemDialogVisible = ref(false);

const templateForm = ref({
  id: null as number | null,
  name: "",
  review_type: "APPLICATION",
  review_level: "LEVEL2",
  scope: "COLLEGE",
  notice: "",
});

const itemForm = ref({
  id: null as number | null,
  template: null as number | null,
  title: "",
  weight: 0,
  max_score: 100,
  is_required: false,
  description: "",
});

const loadTemplates = async () => {
  const res: any = await getReviewTemplates();
  templates.value = res.data || res;
};

const loadItems = async (templateId: number) => {
  const res: any = await getReviewTemplateItems({ template: templateId });
  items.value = res.data || res;
};

const selectTemplate = async (item: any) => {
  currentTemplate.value = item;
  await loadItems(item.id);
};

const openTemplateDialog = () => {
  templateForm.value = {
    id: null,
    name: "",
    review_type: "APPLICATION",
    review_level: "LEVEL2",
    scope: "COLLEGE",
    notice: "",
  };
  templateDialogVisible.value = true;
};

const saveTemplate = async () => {
  saving.value = true;
  try {
    if (templateForm.value.id) {
      await updateReviewTemplate(templateForm.value.id, templateForm.value);
    } else {
      await createReviewTemplate(templateForm.value);
    }
    ElMessage.success("保存成功");
    templateDialogVisible.value = false;
    await loadTemplates();
  } catch (error) {
    ElMessage.error("保存失败");
  } finally {
    saving.value = false;
  }
};

const openItemDialog = () => {
  if (!currentTemplate.value) return;
  itemForm.value = {
    id: null,
    template: currentTemplate.value.id,
    title: "",
    weight: 0,
    max_score: 100,
    is_required: false,
    description: "",
  };
  itemDialogVisible.value = true;
};

const editItem = (item: any) => {
  itemForm.value = { ...item };
  itemDialogVisible.value = true;
};

const saveItem = async () => {
  if (!currentTemplate.value) return;
  saving.value = true;
  try {
    const payload = { ...itemForm.value, template: currentTemplate.value.id };
    if (payload.id) {
      await updateReviewTemplateItem(payload.id, payload);
    } else {
      await createReviewTemplateItem(payload);
    }
    ElMessage.success("保存成功");
    itemDialogVisible.value = false;
    await loadItems(currentTemplate.value.id);
  } catch (error) {
    ElMessage.error("保存失败");
  } finally {
    saving.value = false;
  }
};

const removeItem = async (item: any) => {
  await ElMessageBox.confirm("确认删除评分项？", "提示", { type: "warning" });
  await deleteReviewTemplateItem(item.id);
  ElMessage.success("已删除");
  if (currentTemplate.value) {
    await loadItems(currentTemplate.value.id);
  }
};

const handleDragStart = (index: number) => {
  dragIndex.value = index;
};

const handleDrop = async (index: number) => {
  if (dragIndex.value === null || dragIndex.value === index) return;
  const moving = items.value.splice(dragIndex.value, 1)[0];
  items.value.splice(index, 0, moving);
  dragIndex.value = null;
  const payload = items.value.map((item, idx) => ({
    id: item.id,
    sort_order: idx,
  }));
  await reorderReviewTemplateItems(payload);
  await loadItems(currentTemplate.value.id);
};

onMounted(async () => {
  await loadTemplates();
});
</script>

<style scoped lang="scss">
.review-templates-page {
  .panel-card {
    min-height: 560px;
  }

  .list-item {
    padding: 12px 16px;
    border-bottom: 1px solid #f1f5f9;
    cursor: pointer;

    &.active {
      background: #eff6ff;
    }

    .item-title {
      font-weight: 600;
      margin-bottom: 4px;
    }

    .item-meta {
      display: flex;
      gap: 6px;
    }
  }

  .node-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .node-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background: #fff;
  }

  .node-handle {
    cursor: grab;
    color: #94a3b8;
  }

  .node-content {
    flex: 1;
  }

  .node-title {
    font-weight: 600;
  }

  .node-meta {
    display: flex;
    gap: 6px;
    margin-top: 6px;
    flex-wrap: wrap;
  }
}
</style>
