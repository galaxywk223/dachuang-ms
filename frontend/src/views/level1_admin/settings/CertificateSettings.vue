<template>
  <div class="certificate-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">结题证书设置</span>
          <el-button type="primary" :loading="saving" @click="saveConfig">
            保存配置
          </el-button>
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
            <el-option v-for="item in levelOptions" :key="item.id" :label="item.label" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用项目类别">
          <el-select v-model="form.project_category" placeholder="不限制" clearable>
            <el-option v-for="item in categoryOptions" :key="item.id" :label="item.label" :value="item.id" />
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
import { getDictionaryByCode } from "@/api/dictionary";
import {
  getCertificateSettings,
  createCertificateSetting,
  updateCertificateSetting,
} from "@/api/system-settings";

const loading = ref(false);
const saving = ref(false);
const currentId = ref<number | null>(null);

const levelOptions = ref<any[]>([]);
const categoryOptions = ref<any[]>([]);

const form = reactive<any>({
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

const loadOptions = async () => {
  const [levels, categories] = await Promise.all([
    getDictionaryByCode("project_level"),
    getDictionaryByCode("project_type"),
  ]);
  levelOptions.value = (levels as any)?.items || (levels as any)?.data?.items || [];
  categoryOptions.value = (categories as any)?.items || (categories as any)?.data?.items || [];
};

const loadConfig = async () => {
  loading.value = true;
  try {
    const res: any = await getCertificateSettings();
    const data = res.data || res;
    const list = data.data || data;
    if (Array.isArray(list) && list.length > 0) {
      const item = list[0];
      currentId.value = item.id;
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
    ElMessage.error("加载证书配置失败");
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
  } catch (error: any) {
    ElMessage.error(error.message || "保存失败");
  } finally {
    saving.value = false;
  }
};

onMounted(async () => {
  await loadOptions();
  await loadConfig();
});
</script>

<style scoped>
.certificate-page {
  padding: 20px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
.config-form {
  max-width: 760px;
}
.ml-2 {
  margin-left: 8px;
}
</style>
