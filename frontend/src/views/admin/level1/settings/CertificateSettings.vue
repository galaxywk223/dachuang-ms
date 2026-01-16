<template>
  <div class="certificate-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">结题证书设置</span>
           </div>
           <div class="header-actions">
            <el-button type="primary" @click="openCreateDialog">
              <el-icon class="mr-1"><Plus /></el-icon>新建模板
            </el-button>
           </div>
        </div>
      </template>

      <el-table
        :data="settings"
        v-loading="loading"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="模板名称" min-width="160" />
        <el-table-column label="适用级别" min-width="140">
          <template #default="{ row }">
            {{ getScopeLabel(row.project_level, levelOptions) }}
          </template>
        </el-table-column>
        <el-table-column label="适用类别" min-width="140">
          <template #default="{ row }">
            {{ getScopeLabel(row.project_category, categoryOptions) }}
          </template>
        </el-table-column>
        <el-table-column label="启用状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" effect="light">
              {{ row.is_active ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="160">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="860px"
      :close-on-click-modal="false"
    >
      <el-form label-width="110px" class="dialog-form" :model="form">
        <el-divider content-position="left">基础信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="模板名称">
              <el-input v-model="form.name" placeholder="如：默认模板" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用状态">
              <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">适用范围</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="项目级别">
              <el-select v-model="form.project_level" placeholder="不限制" clearable>
                <el-option
                  v-for="item in levelOptions"
                  :key="getOptionKey(item)"
                  :label="item.label"
                  :value="getOptionValue(item)"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目类别">
              <el-select v-model="form.project_category" placeholder="不限制" clearable>
                <el-option
                  v-for="item in categoryOptions"
                  :key="getOptionKey(item)"
                  :label="item.label"
                  :value="getOptionValue(item)"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">证书内容</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学校名称">
              <el-input v-model="form.school_name" placeholder="请输入学校名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发证单位">
              <el-input v-model="form.issuer_name" placeholder="请输入发放单位名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">样式资源</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="证书底图">
              <div class="upload-row">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :limit="1"
                  :on-change="handleBackgroundChange"
                  :file-list="backgroundFileList"
                >
                  <el-button type="primary" plain>选择图片</el-button>
                </el-upload>
                <el-link
                  v-if="form.background_image_url"
                  type="primary"
                  :href="form.background_image_url"
                  target="_blank"
                >
                  查看当前底图
                </el-link>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电子印章">
              <div class="upload-row">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :limit="1"
                  :on-change="handleSealChange"
                  :file-list="sealFileList"
                >
                  <el-button type="primary" plain>选择图片</el-button>
                </el-upload>
                <el-link
                  v-if="form.seal_image_url"
                  type="primary"
                  :href="form.seal_image_url"
                  target="_blank"
                >
                  查看当前印章
                </el-link>
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">高级配置</el-divider>
        <el-collapse v-model="advancedPanels">
          <el-collapse-item name="advanced">
            <template #title>JSON 样式配置</template>
            <el-row :gutter="16">
              <el-col :span="12">
                <el-form-item label="模板编码">
                  <el-input v-model="form.template_code" placeholder="系统自动生成" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="样式配置(JSON)">
              <el-input
                v-model="styleConfigText"
                type="textarea"
                :rows="5"
                placeholder='{"font": "SimSun", "layout": "classic"}'
              />
            </el-form-item>
          </el-collapse-item>
        </el-collapse>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveSetting">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type UploadUserFile,
  type UploadFile,
} from "element-plus";
import { Plus } from "@element-plus/icons-vue";
import { getDictionaryByCode } from "@/api/dictionaries";
import {
  getCertificateSettings,
  createCertificateSetting,
  updateCertificateSetting,
  deleteCertificateSetting,
} from "@/api/system-settings";

defineOptions({ name: "Level1CertificateSettingsView" });

type OptionItem = {
  id?: number;
  value: string;
  label: string;
};

type CertificateSetting = {
  id?: number;
  name?: string;
  school_name?: string;
  issuer_name?: string;
  template_code?: string;
  project_level?: number | string | null;
  project_category?: number | string | null;
  background_image_url?: string;
  seal_image_url?: string;
  style_config?: Record<string, unknown>;
  is_active?: boolean;
  updated_at?: string;
};

type SettingsResponse = {
  data?: {
    data?: CertificateSetting[];
  } | CertificateSetting[];
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (isRecord(response) && isRecord(response.data) && typeof response.data.message === "string") {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const dialogMode = ref<"create" | "edit">("create");
const editingId = ref<number | null>(null);
const advancedPanels = ref<string[]>([]);

const settings = ref<CertificateSetting[]>([]);

const levelOptions = ref<OptionItem[]>([]);
const categoryOptions = ref<OptionItem[]>([]);

const form = reactive<CertificateSetting>({
  name: "",
  school_name: "",
  issuer_name: "",
  template_code: "",
  project_level: null,
  project_category: null,
  background_image_url: "",
  seal_image_url: "",
  is_active: true,
});

const styleConfigText = ref("{}");
const backgroundFile = ref<File | null>(null);
const sealFile = ref<File | null>(null);
const backgroundFileList = ref<UploadUserFile[]>([]);
const sealFileList = ref<UploadUserFile[]>([]);

const dialogTitle = computed(() =>
  dialogMode.value === "create" ? "新建证书模板" : "编辑证书模板"
);

const extractOptions = (payload: unknown): OptionItem[] => {
  if (!isRecord(payload)) return [];
  if (Array.isArray(payload.items)) return payload.items as OptionItem[];
  const data = payload.data;
  if (isRecord(data) && Array.isArray(data.items)) return data.items as OptionItem[];
  return [];
};

const getOptionValue = (item: OptionItem) => item.id ?? item.value;
const getOptionKey = (item: OptionItem) => item.id ?? item.value;

const isSameValue = (optionValue: number | string | undefined, target: number | string) =>
  optionValue !== undefined && String(optionValue) === String(target);

const getScopeLabel = (
  value: number | string | null | undefined,
  options: OptionItem[]
) => {
  if (value === null || value === undefined || value === "") return "不限制";
  const match = options.find(
    (item) => isSameValue(item.id, value) || isSameValue(item.value, value)
  );
  return match ? match.label : String(value);
};

const formatDate = (value?: string) => {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  const hh = String(date.getHours()).padStart(2, "0");
  const min = String(date.getMinutes()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd} ${hh}:${min}`;
};

const loadOptions = async () => {
  const [levels, categories] = await Promise.all([
    getDictionaryByCode("project_level"),
    getDictionaryByCode("project_type"),
  ]);
  levelOptions.value = extractOptions(levels);
  categoryOptions.value = extractOptions(categories);
};

const loadSettings = async () => {
  loading.value = true;
  try {
    const res = (await getCertificateSettings()) as SettingsResponse | CertificateSetting[];
    const data = isRecord(res) && "data" in res ? res.data : res;
    const list = isRecord(data) && Array.isArray(data.data) ? data.data : data;
    settings.value = Array.isArray(list) ? list : [];
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "加载证书配置失败"));
  } finally {
    loading.value = false;
  }
};

const handleBackgroundChange = (file: UploadFile) => {
  backgroundFile.value = file.raw || null;
  backgroundFileList.value = file.raw ? [{ name: file.name, url: "" }] : [];
};

const handleSealChange = (file: UploadFile) => {
  sealFile.value = file.raw || null;
  sealFileList.value = file.raw ? [{ name: file.name, url: "" }] : [];
};

const resetForm = () => {
  form.name = "";
  form.school_name = "";
  form.issuer_name = "";
  form.template_code = "";
  form.project_level = null;
  form.project_category = null;
  form.background_image_url = "";
  form.seal_image_url = "";
  form.is_active = true;
  styleConfigText.value = "{}";
  backgroundFile.value = null;
  sealFile.value = null;
  backgroundFileList.value = [];
  sealFileList.value = [];
  advancedPanels.value = [];
};

const openCreateDialog = () => {
  dialogMode.value = "create";
  editingId.value = null;
  resetForm();
  dialogVisible.value = true;
};

const openEditDialog = (item: CertificateSetting) => {
  dialogMode.value = "edit";
  editingId.value = item.id ?? null;
  form.name = item.name || "";
  form.school_name = item.school_name || "";
  form.issuer_name = item.issuer_name || "";
  form.template_code = item.template_code || "";
  form.project_level = item.project_level ?? null;
  form.project_category = item.project_category ?? null;
  form.background_image_url = item.background_image_url || "";
  form.seal_image_url = item.seal_image_url || "";
  form.is_active = item.is_active ?? true;
  styleConfigText.value = JSON.stringify(item.style_config || {}, null, 2);
  backgroundFile.value = null;
  sealFile.value = null;
  backgroundFileList.value = [];
  sealFileList.value = [];
  advancedPanels.value =
    item.style_config && Object.keys(item.style_config).length > 0
      ? ["advanced"]
      : [];
  dialogVisible.value = true;
};

const buildPayload = () => {
  let styleConfig: Record<string, unknown> = {};
  try {
    styleConfig = JSON.parse(styleConfigText.value || "{}");
  } catch {
    throw new Error("样式配置不是有效的JSON");
  }

  const basePayload: Record<string, unknown> = {
    name: form.name || "",
    school_name: form.school_name || "",
    issuer_name: form.issuer_name || "",
    style_config: styleConfig,
    is_active: form.is_active ?? true,
  };

  if (form.template_code) {
    basePayload.template_code = form.template_code;
  }
  if (form.project_level) {
    basePayload.project_level = form.project_level;
  }
  if (form.project_category) {
    basePayload.project_category = form.project_category;
  }

  if (!backgroundFile.value && !sealFile.value) {
    return basePayload;
  }

  const payload = new FormData();
  Object.entries(basePayload).forEach(([key, value]) => {
    if (value === undefined) return;
    if (key === "style_config") {
      payload.append(key, JSON.stringify(value));
      return;
    }
    payload.append(key, String(value));
  });
  if (backgroundFile.value) payload.append("background_image", backgroundFile.value);
  if (sealFile.value) payload.append("seal_image", sealFile.value);
  return payload;
};

const saveSetting = async () => {
  if (!form.name) {
    ElMessage.warning("请填写模板名称");
    return;
  }
  saving.value = true;
  try {
    const payload = buildPayload();
    if (dialogMode.value === "edit" && editingId.value) {
      await updateCertificateSetting(editingId.value, payload);
      ElMessage.success("更新成功");
    } else {
      await createCertificateSetting(payload);
      ElMessage.success("创建成功");
    }
    dialogVisible.value = false;
    await loadSettings();
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  } finally {
    saving.value = false;
  }
};

const handleDelete = async (item: CertificateSetting) => {
  if (!item.id) return;
  try {
    await ElMessageBox.confirm(
      `确认删除模板「${item.name || "未命名"}」？`,
      "提示",
      {
        type: "warning",
        confirmButtonText: "删除",
        cancelButtonText: "取消",
      }
    );
  } catch {
    return;
  }
  try {
    await deleteCertificateSetting(item.id);
    ElMessage.success("删除成功");
    await loadSettings();
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "删除失败"));
  }
};

onMounted(async () => {
  await loadOptions();
  await loadSettings();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.certificate-page {
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

.dialog-form {
  margin-top: 8px;
}

.upload-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.dialog-footer {
  display: inline-flex;
  gap: 12px;
}
</style>
