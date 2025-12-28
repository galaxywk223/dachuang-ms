<template>
  <div class="certificate-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">结题证书设置</span>
           </div>
           <div class="header-actions">
            <el-button type="primary" :loading="saving" @click="saveConfig">
              保存配置
            </el-button>
           </div>
        </div>
      </template>

      <el-form label-width="140px" class="config-form" v-loading="loading">
        <el-form-item label="模板名称">
          <el-input v-model="form.name" placeholder="如：默认模板" />
        </el-form-item>
        <el-form-item label="学校名称">
          <el-input v-model="form.school_name" placeholder="请输入学校名称" />
        </el-form-item>
        <el-form-item label="证书发放单位">
          <el-input v-model="form.issuer_name" placeholder="请输入发放单位名称" />
        </el-form-item>
        <el-form-item label="模板编码">
          <el-input v-model="form.template_code" placeholder="如：DEFAULT" />
        </el-form-item>
        <el-form-item label="适用项目级别">
          <el-select v-model="form.project_level" placeholder="不限制" clearable>
            <el-option v-for="item in levelOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用项目类别">
          <el-select v-model="form.project_category" placeholder="不限制" clearable>
            <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="证书底图">
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
            class="ml-2"
            type="primary"
            :href="form.background_image_url"
            target="_blank"
          >
            查看当前底图
          </el-link>
        </el-form-item>
        <el-form-item label="电子印章">
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
            class="ml-2"
            type="primary"
            :href="form.seal_image_url"
            target="_blank"
          >
            查看当前印章
          </el-link>
        </el-form-item>
        <el-form-item label="样式配置(JSON)">
          <el-input
            v-model="styleConfigText"
            type="textarea"
            :rows="4"
            placeholder='{"font": "SimSun", "layout": "classic"}'
          />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from "vue";
import { ElMessage, type UploadUserFile, type UploadFile } from "element-plus";
import { getDictionaryByCode } from "@/api/dictionaries";
import {
  getCertificateSettings,
  createCertificateSetting,
  updateCertificateSetting,
} from "@/api/system-settings";

defineOptions({ name: "Level1CertificateSettingsView" });

type OptionItem = {
  value: string;
  label: string;
};

type CertificateSetting = {
  id?: number;
  name?: string;
  school_name?: string;
  issuer_name?: string;
  template_code?: string;
  project_level?: string | null;
  project_category?: string | null;
  background_image_url?: string;
  seal_image_url?: string;
  style_config?: Record<string, unknown>;
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
const currentId = ref<number | null>(null);

const levelOptions = ref<OptionItem[]>([]);
const categoryOptions = ref<OptionItem[]>([]);

const form = reactive<CertificateSetting>({
  name: "默认模板",
  school_name: "",
  issuer_name: "",
  template_code: "DEFAULT",
  project_level: null,
  project_category: null,
  background_image_url: "",
  seal_image_url: "",
});

const styleConfigText = ref("{}");
const backgroundFile = ref<File | null>(null);
const sealFile = ref<File | null>(null);
const backgroundFileList = ref<UploadUserFile[]>([]);
const sealFileList = ref<UploadUserFile[]>([]);

const extractOptions = (payload: unknown): OptionItem[] => {
  if (!isRecord(payload)) return [];
  if (Array.isArray(payload.items)) return payload.items as OptionItem[];
  const data = payload.data;
  if (isRecord(data) && Array.isArray(data.items)) return data.items as OptionItem[];
  return [];
};

const loadOptions = async () => {
  const [levels, categories] = await Promise.all([
    getDictionaryByCode("project_level"),
    getDictionaryByCode("project_type"),
  ]);
  levelOptions.value = extractOptions(levels);
  categoryOptions.value = extractOptions(categories);
};

const loadConfig = async () => {
  loading.value = true;
  try {
    const res = (await getCertificateSettings()) as SettingsResponse | CertificateSetting[];
    const data = isRecord(res) && "data" in res ? res.data : res;
    const list = isRecord(data) && Array.isArray(data.data) ? data.data : data;
    if (Array.isArray(list) && list.length > 0) {
      const item = list[0];
      currentId.value = item.id ?? null;
      form.name = item.name || "默认模板";
      form.school_name = item.school_name || "";
      form.issuer_name = item.issuer_name || "";
      form.template_code = item.template_code || "DEFAULT";
      form.project_level = item.project_level || null;
      form.project_category = item.project_category || null;
      form.background_image_url = item.background_image_url || "";
      form.seal_image_url = item.seal_image_url || "";
      styleConfigText.value = JSON.stringify(item.style_config || {}, null, 2);
    }
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

const buildPayload = () => {
  let styleConfig = {};
  try {
    styleConfig = JSON.parse(styleConfigText.value || "{}");
  } catch {
    throw new Error("样式配置不是有效的JSON");
  }

  const payload = new FormData();
  payload.append("name", form.name || "");
  payload.append("school_name", form.school_name || "");
  payload.append("issuer_name", form.issuer_name || "");
  payload.append("template_code", form.template_code || "DEFAULT");
  if (form.project_level) {
    payload.append("project_level", String(form.project_level));
  }
  if (form.project_category) {
    payload.append("project_category", String(form.project_category));
  }
  payload.append("style_config", JSON.stringify(styleConfig));
  if (backgroundFile.value) {
    payload.append("background_image", backgroundFile.value);
  }
  if (sealFile.value) {
    payload.append("seal_image", sealFile.value);
  }
  return payload;
};

const saveConfig = async () => {
  saving.value = true;
  try {
    const payload = buildPayload();
    if (currentId.value) {
      await updateCertificateSetting(currentId.value, payload);
    } else {
      await createCertificateSetting(payload);
    }
    ElMessage.success("保存成功");
    await loadConfig();
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  } finally {
    saving.value = false;
  }
};

onMounted(async () => {
  await loadOptions();
  await loadConfig();
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

.config-form {
  max-width: 760px;
  margin-top: 16px;
}
.ml-2 {
  margin-left: 8px;
}
</style>
