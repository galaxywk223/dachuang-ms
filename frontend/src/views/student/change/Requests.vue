<template>
  <div class="change-requests-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">异动管理</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="openDialog">新建申请</el-button>
          </div>
        </div>
      </template>

      <el-table :data="requests" v-loading="loading" border stripe>
        <el-table-column prop="project_no" label="项目编号" width="140" />
        <el-table-column
          prop="project_title"
          label="项目名称"
          min-width="180"
        />
        <el-table-column prop="request_type_display" label="类型" width="120" />
        <el-table-column prop="status_display" label="状态" width="140" />
        <el-table-column prop="submitted_at" label="提交时间" width="160" />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'DRAFT'"
              size="small"
              type="primary"
              @click="editRequest(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'DRAFT'"
              size="small"
              type="success"
              @click="submitRequest(row)"
            >
              提交
            </el-button>
            <el-button
              v-if="row.attachment_url"
              size="small"
              @click="openAttachment(row.attachment_url)"
            >
              附件
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      title="异动申请"
      width="620px"
      destroy-on-close
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="项目" required>
          <el-select
            v-model="form.project"
            placeholder="请选择项目"
            style="width: 100%"
            :disabled="!!route.params.projectId"
          >
            <el-option
              v-for="item in projectOptions"
              :key="item.id"
              :label="item.title"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select
            v-model="form.request_type"
            placeholder="请选择类型"
            style="width: 100%"
          >
            <el-option label="项目变更" value="CHANGE" />
            <el-option label="项目终止" value="TERMINATION" />
            <el-option label="项目延期" value="EXTENSION" />
          </el-select>
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="form.reason" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item
          v-if="form.request_type === 'EXTENSION'"
          label="延期至"
          required
        >
          <el-date-picker
            v-model="form.requested_end_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item
          v-if="form.request_type === 'CHANGE'"
          label="变更内容"
          required
        >
          <div class="change-items">
            <div v-if="changeItems.length === 0" class="empty-tip">
              请添加需要变更的项目字段
            </div>
            <div
              v-for="(item, index) in changeItems"
              :key="index"
              class="change-item"
            >
              <div class="item-row">
                <el-select
                  v-model="item.field"
                  class="field-select"
                  placeholder="选择字段"
                  @change="() => handleFieldChange(item)"
                >
                  <el-option
                    v-for="option in getFieldOptions(index)"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                    :disabled="option.disabled"
                  />
                </el-select>
                <div class="value-input">
                  <el-input
                    v-if="getFieldConfig(item.field)?.type === 'text'"
                    v-model="item.value"
                    placeholder="填写新的值"
                  />
                  <el-input
                    v-else-if="getFieldConfig(item.field)?.type === 'textarea'"
                    v-model="item.value"
                    type="textarea"
                    :rows="2"
                    placeholder="填写新的值"
                  />
                  <el-input-number
                    v-else-if="getFieldConfig(item.field)?.type === 'number'"
                    v-model="item.value"
                    class="number-input"
                    :min="0"
                    :precision="2"
                    controls-position="right"
                  />
                  <el-date-picker
                    v-else-if="getFieldConfig(item.field)?.type === 'date'"
                    v-model="item.value"
                    type="date"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                  <el-select
                    v-else-if="getFieldConfig(item.field)?.type === 'select'"
                    v-model="item.value"
                    placeholder="请选择"
                    style="width: 100%"
                  >
                    <el-option
                      v-for="option in getSelectOptions(item.field)"
                      :key="option.value"
                      :label="option.label"
                      :value="option.value"
                    />
                  </el-select>
                  <el-select
                    v-else-if="getFieldConfig(item.field)?.type === 'boolean'"
                    v-model="item.value"
                    placeholder="请选择"
                    style="width: 100%"
                  >
                    <el-option label="是" :value="true" />
                    <el-option label="否" :value="false" />
                  </el-select>
                  <el-input
                    v-else
                    v-model="item.value"
                    placeholder="填写新的值"
                  />
                </div>
                <el-button
                  text
                  type="danger"
                  @click="removeChangeItem(index)"
                  >删除</el-button
                >
              </div>
              <div v-if="item.field" class="current-value">
                当前值：{{ formatCurrentValue(item.field) || "-" }}
              </div>
            </div>
            <el-button type="primary" plain @click="addChangeItem"
              >添加变更项</el-button
            >
          </div>
        </el-form-item>
        <el-form-item label="附件">
          <el-upload
            action="#"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :file-list="fileList"
          >
            <el-button type="primary" plain>选择文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="saving"
            :disabled="saving"
            @click="saveDraft"
            >保存草稿</el-button
          >
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, type UploadFile, type UploadUserFile } from "element-plus";
import {
  createChangeRequest,
  updateChangeRequest,
  submitChangeRequest,
} from "@/api/projects/change-requests";
import request from "@/utils/request";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";

defineOptions({
  name: "StudentChangeRequestsView",
});

const route = useRoute();

type ProjectOption = {
  id: number;
  title: string;
};

type ChangeRequest = {
  id: number;
  project: number;
  project_no?: string;
  project_title?: string;
  request_type?: string;
  request_type_display?: string;
  status?: string;
  status_display?: string;
  submitted_at?: string;
  requested_end_date?: string;
  reason?: string;
  attachment_url?: string;
  change_data?: Record<string, unknown>;
};

type RequestForm = {
  id: number | null;
  project: number | null;
  request_type: string;
  reason: string;
  requested_end_date: string;
};

type ChangeItem = {
  field: string;
  value: string | number | boolean | null;
};

type ProjectDetail = {
  id: number;
  title?: string;
  description?: string;
  level?: string;
  level_display?: string;
  category?: string;
  category_display?: string;
  source?: string;
  source_display?: string;
  start_date?: string;
  end_date?: string;
  budget?: number | string;
  research_content?: string;
  research_plan?: string;
  expected_results?: string;
  innovation_points?: string;
  is_key_field?: boolean;
  key_domain_code?: string;
  category_description?: string;
  self_funding?: number | string;
};

type ChangeFieldConfig = {
  key: string;
  label: string;
  type: "text" | "textarea" | "select" | "date" | "number" | "boolean";
  dictCode?: string;
  valueSource?: "id" | "value";
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveList = <T>(payload: unknown): T[] => {
  if (Array.isArray(payload)) return payload as T[];
  if (isRecord(payload) && Array.isArray(payload.results)) {
    return payload.results as T[];
  }
  if (
    isRecord(payload) &&
    isRecord(payload.data) &&
    Array.isArray(payload.data.results)
  ) {
    return payload.data.results as T[];
  }
  if (isRecord(payload) && Array.isArray(payload.data)) {
    return payload.data as T[];
  }
  return [];
};

const getErrorMessage = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    return error.message || fallback;
  }
  if (typeof error === "string") {
    return error || fallback;
  }
  return fallback;
};

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const requests = ref<ChangeRequest[]>([]);
const projectOptions = ref<ProjectOption[]>([]);
const fileList = ref<UploadUserFile[]>([]);
const attachmentFile = ref<File | null>(null);
const changeItems = ref<ChangeItem[]>([]);
const selectedProject = ref<ProjectDetail | null>(null);

const { getOptions, getLabel, loadDictionaries } = useDictionary();

const form = reactive<RequestForm>({
  id: null,
  project: null,
  request_type: "CHANGE",
  reason: "",
  requested_end_date: "",
});

const changeFieldConfigs: ChangeFieldConfig[] = [
  { key: "title", label: "项目名称", type: "text" },
  { key: "description", label: "项目简介", type: "textarea" },
  {
    key: "level_id",
    label: "项目级别",
    type: "select",
    dictCode: DICT_CODES.PROJECT_LEVEL,
    valueSource: "id",
  },
  {
    key: "category_id",
    label: "项目类别",
    type: "select",
    dictCode: DICT_CODES.PROJECT_CATEGORY,
    valueSource: "id",
  },
  {
    key: "source_id",
    label: "项目来源",
    type: "select",
    dictCode: DICT_CODES.PROJECT_SOURCE,
    valueSource: "id",
  },
  { key: "start_date", label: "开始日期", type: "date" },
  { key: "end_date", label: "结束日期", type: "date" },
  { key: "budget", label: "项目经费(元)", type: "number" },
  { key: "self_funding", label: "项目自筹(元)", type: "number" },
  { key: "research_content", label: "研究内容", type: "textarea" },
  { key: "research_plan", label: "研究方案", type: "textarea" },
  { key: "expected_results", label: "预期成果", type: "textarea" },
  { key: "innovation_points", label: "创新点", type: "textarea" },
  { key: "is_key_field", label: "重点领域项目", type: "boolean" },
  {
    key: "key_domain_code",
    label: "重点领域代码",
    type: "select",
    dictCode: DICT_CODES.KEY_FIELD_CODE,
    valueSource: "value",
  },
  { key: "category_description", label: "立项类别描述", type: "textarea" },
];

const getFieldConfig = (fieldKey: string) =>
  changeFieldConfigs.find((field) => field.key === fieldKey);

const getDictIdByValue = (code: string, value?: string | null) => {
  if (!value) return null;
  const options = getOptions(code);
  const match = options.find((item) => item.value === value);
  return match?.id ?? null;
};

const normalizeChangeValue = (fieldKey: string, value: unknown) => {
  const fieldConfig = getFieldConfig(fieldKey);
  if (!fieldConfig) return null;
  if (fieldConfig.type === "boolean") {
    if (typeof value === "boolean") return value;
    if (typeof value === "string") return value.toLowerCase() === "true";
    if (typeof value === "number") return value === 1;
    return null;
  }
  if (fieldConfig.type === "number") {
    if (typeof value === "number") return value;
    if (typeof value === "string" && value.trim() !== "") {
      const num = Number(value);
      return Number.isNaN(num) ? null : num;
    }
    return null;
  }
  if (fieldConfig.type === "select" && fieldConfig.valueSource === "id") {
    if (typeof value === "number") return value;
    if (typeof value === "string") {
      return getDictIdByValue(fieldConfig.dictCode || "", value);
    }
  }
  if (typeof value === "string") return value;
  return value as string | number | boolean | null;
};

const getSelectOptions = (fieldKey: string) => {
  const fieldConfig = getFieldConfig(fieldKey);
  if (!fieldConfig || fieldConfig.type !== "select") return [];
  const dictCode = fieldConfig.dictCode;
  if (!dictCode) return [];
  const options = getOptions(dictCode);
  return options.map((item) => ({
    value:
      fieldConfig.valueSource === "id" ? item.id ?? item.value : item.value,
    label: item.label,
  }));
};

const getFieldOptions = (currentIndex: number) => {
  const usedFields = new Set(
    changeItems.value
      .map((item, index) => (index === currentIndex ? "" : item.field))
      .filter(Boolean)
  );
  return changeFieldConfigs.map((field) => ({
    label: field.label,
    value: field.key,
    disabled: usedFields.has(field.key),
  }));
};

const getCurrentValue = (fieldKey: string) => {
  const project = selectedProject.value;
  if (!project) return null;
  switch (fieldKey) {
    case "level_id":
      return getDictIdByValue(DICT_CODES.PROJECT_LEVEL, project.level);
    case "category_id":
      return getDictIdByValue(DICT_CODES.PROJECT_CATEGORY, project.category);
    case "source_id":
      return getDictIdByValue(DICT_CODES.PROJECT_SOURCE, project.source);
    case "key_domain_code":
      return project.key_domain_code || "";
    case "is_key_field":
      return !!project.is_key_field;
    case "budget":
      return project.budget ?? null;
    case "self_funding":
      return project.self_funding ?? null;
    case "start_date":
      return project.start_date || "";
    case "end_date":
      return project.end_date || "";
    case "title":
      return project.title || "";
    case "description":
      return project.description || "";
    case "research_content":
      return project.research_content || "";
    case "research_plan":
      return project.research_plan || "";
    case "expected_results":
      return project.expected_results || "";
    case "innovation_points":
      return project.innovation_points || "";
    case "category_description":
      return project.category_description || "";
    default:
      return null;
  }
};

const formatCurrentValue = (fieldKey: string) => {
  const project = selectedProject.value;
  if (!project) return "";
  switch (fieldKey) {
    case "level_id":
      return (
        project.level_display ||
        (project.level ? getLabel(DICT_CODES.PROJECT_LEVEL, project.level) : "")
      );
    case "category_id":
      return (
        project.category_display ||
        (project.category
          ? getLabel(DICT_CODES.PROJECT_CATEGORY, project.category)
          : "")
      );
    case "source_id":
      return (
        project.source_display ||
        (project.source ? getLabel(DICT_CODES.PROJECT_SOURCE, project.source) : "")
      );
    case "key_domain_code":
      return project.key_domain_code
        ? getLabel(DICT_CODES.KEY_FIELD_CODE, project.key_domain_code)
        : "";
    case "is_key_field":
      return project.is_key_field ? "是" : "否";
    case "budget":
      return project.budget?.toString() || "";
    case "self_funding":
      return project.self_funding?.toString() || "";
    case "start_date":
      return project.start_date || "";
    case "end_date":
      return project.end_date || "";
    case "title":
      return project.title || "";
    case "description":
      return project.description || "";
    case "research_content":
      return project.research_content || "";
    case "research_plan":
      return project.research_plan || "";
    case "expected_results":
      return project.expected_results || "";
    case "innovation_points":
      return project.innovation_points || "";
    case "category_description":
      return project.category_description || "";
    default:
      return "";
  }
};

const addChangeItem = () => {
  changeItems.value.push({ field: "", value: null });
};

const removeChangeItem = (index: number) => {
  changeItems.value.splice(index, 1);
};

const handleFieldChange = (item: ChangeItem) => {
  if (!item.field) {
    item.value = null;
    return;
  }
  item.value = getCurrentValue(item.field);
};

const fetchRequests = async () => {
  loading.value = true;
  try {
    const projectIdParam = route.params.projectId;
    if (!projectIdParam) {
      ElMessage.error("缺少项目ID参数");
      return;
    }
    const projectId = Number(projectIdParam);
    if (isNaN(projectId)) {
      ElMessage.error("项目ID格式错误");
      return;
    }
    // 获取指定项目的异动申请
    const res = await request.get("/projects/change-requests/", {
      params: { project: projectId },
    });
    const payload = isRecord(res) && isRecord(res.data) ? res.data : res;
    requests.value = resolveList<ChangeRequest>(payload);
  } catch (error: unknown) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const fetchProjects = async () => {
  try {
    const projectIdParam = route.params.projectId;
    if (projectIdParam) {
      // 如果URL中有projectId，只获取该项目
      const projectId = Number(projectIdParam);
      const res = await request.get(`/projects/${projectId}/`);
      const project = isRecord(res) && isRecord(res.data) ? res.data : res;
      if (project && isRecord(project)) {
        projectOptions.value = [
          {
            id: project.id as number,
            title: project.title as string,
          },
        ];
        selectedProject.value = project as ProjectDetail;
      }
    } else {
      // 否则获取所有可申请异动的项目
      const res = await request.get("/projects/", {
        params: {
          status_in:
            "IN_PROGRESS,MID_TERM_DRAFT,MID_TERM_SUBMITTED,MID_TERM_REVIEWING,READY_FOR_CLOSURE",
        },
      });
      const payload = isRecord(res) && isRecord(res.data) ? res.data : res;
      projectOptions.value = resolveList<ProjectOption>(payload);
    }
  } catch (error) {
    console.error("Failed to fetch projects", error);
  }
};

const fetchProjectDetail = async (projectId: number) => {
  try {
    const res = await request.get(`/projects/${projectId}/`);
    const project = isRecord(res) && isRecord(res.data) ? res.data : res;
    if (project && isRecord(project)) {
      selectedProject.value = project as ProjectDetail;
    }
  } catch (error) {
    console.error("Failed to fetch project detail", error);
  }
};

const openDialog = () => {
  form.id = null;
  const projectIdParam = route.params.projectId;
  form.project = projectIdParam ? Number(projectIdParam) : null;
  form.request_type = "CHANGE";
  form.reason = "";
  form.requested_end_date = "";
  changeItems.value = [];
  addChangeItem();
  attachmentFile.value = null;
  fileList.value = [];
  dialogVisible.value = true;
};

const editRequest = (row: ChangeRequest) => {
  form.id = row.id;
  form.project = row.project;
  form.request_type = row.request_type ?? "";
  form.reason = row.reason || "";
  form.requested_end_date = row.requested_end_date || "";
  if (row.request_type === "CHANGE" && isRecord(row.change_data)) {
    const entries = Object.entries(row.change_data).filter(([key]) =>
      changeFieldConfigs.some((field) => field.key === key)
    );
    changeItems.value = entries.map(([field, value]) => ({
      field,
      value: normalizeChangeValue(field, value),
    }));
  } else {
    changeItems.value = [];
  }
  if (row.project) {
    fetchProjectDetail(row.project);
  }
  dialogVisible.value = true;
};

const handleFileChange = (file: UploadFile) => {
  attachmentFile.value = file.raw || null;
  fileList.value = file.raw ? [{ name: file.name, url: "" }] : [];
};

const saveDraft = async () => {
  saving.value = true;
  try {
    if (!form.project) {
      ElMessage.error("请选择项目");
      saving.value = false;
      return;
    }
    if (form.request_type === "EXTENSION" && !form.requested_end_date) {
      ElMessage.error("请选择延期日期");
      saving.value = false;
      return;
    }

    let changeData: Record<string, unknown> = {};
    if (form.request_type === "CHANGE") {
      if (changeItems.value.length === 0) {
        ElMessage.error("请添加变更项");
        saving.value = false;
        return;
      }
      for (const item of changeItems.value) {
        if (!item.field) {
          ElMessage.error("请选择变更字段");
          saving.value = false;
          return;
        }
        const config = getFieldConfig(item.field);
        if (!config) {
          ElMessage.error("存在无效的变更字段");
          saving.value = false;
          return;
        }
        const value = item.value;
        if (
          value === null ||
          value === "" ||
          (typeof value === "number" && Number.isNaN(value))
        ) {
          ElMessage.error(`请填写 ${config.label}`);
          saving.value = false;
          return;
        }
        changeData[item.field] = value;
      }
    }

    const payload = new FormData();
    payload.append("project", String(form.project || ""));
    payload.append("request_type", form.request_type);
    payload.append("reason", form.reason || "");
    if (form.request_type === "EXTENSION" && form.requested_end_date) {
      payload.append("requested_end_date", form.requested_end_date);
    }
    if (form.request_type === "CHANGE") {
      payload.append("change_data", JSON.stringify(changeData));
    }
    if (attachmentFile.value) {
      payload.append("attachment", attachmentFile.value);
    }

    if (form.id) {
      await updateChangeRequest(form.id, payload);
    } else {
      await createChangeRequest(payload);
    }
    ElMessage.success("保存成功");
    dialogVisible.value = false;
    fetchRequests();
  } catch (error: unknown) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  } finally {
    saving.value = false;
  }
};

const submitRequest = async (row: ChangeRequest) => {
  try {
    await submitChangeRequest(row.id);
    ElMessage.success("提交成功");
    fetchRequests();
  } catch (error: unknown) {
    ElMessage.error(getErrorMessage(error, "提交失败"));
  }
};

const openAttachment = (url: string) => {
  window.open(url, "_blank");
};

watch(
  () => form.project,
  (value) => {
    if (!value) {
      selectedProject.value = null;
      return;
    }
    fetchProjectDetail(value);
  }
);

watch(
  () => form.request_type,
  (value) => {
    if (value !== "EXTENSION") {
      form.requested_end_date = "";
    }
    if (value !== "CHANGE") {
      changeItems.value = [];
    } else if (changeItems.value.length === 0) {
      addChangeItem();
    }
  }
);

onMounted(() => {
  fetchRequests();
  fetchProjects();
  loadDictionaries([
    DICT_CODES.PROJECT_LEVEL,
    DICT_CODES.PROJECT_CATEGORY,
    DICT_CODES.PROJECT_SOURCE,
    DICT_CODES.KEY_FIELD_CODE,
  ]);
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.change-requests-page {
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
  align-items: center;
  justify-content: space-between;
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
  gap: 12px;
}

.change-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.change-item {
  padding: 12px;
  border: 1px solid $color-border-light;
  border-radius: 8px;
  background: $slate-50;
}

.item-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.field-select {
  width: 160px;
}

.value-input {
  flex: 1;
}

.number-input {
  width: 100%;
}

.current-value {
  margin-top: 6px;
  color: $slate-500;
  font-size: 12px;
}

.empty-tip {
  color: $slate-500;
  font-size: 12px;
}
</style>
