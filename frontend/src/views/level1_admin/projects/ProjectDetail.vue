<template>
  <div class="project-detail-page" v-loading="pageLoading">
    <div class="form-container">
      <div class="page-header">
        <div class="title-bar">
          <span class="title">{{ pageTitle }}</span>
          <el-tag size="small" type="primary" effect="plain" round>一级管理员</el-tag>
          <el-tag
            v-if="form.status_display"
            size="small"
            effect="plain"
            type="info"
            round
          >
            {{ form.status_display }}
          </el-tag>
          <el-tag
            v-if="form.project_no"
            size="small"
            effect="plain"
            round
            type="success"
          >
            编号: {{ form.project_no }}
          </el-tag>
        </div>
        <div class="actions">
          <el-button @click="router.back()">返回</el-button>
          <el-button v-if="isViewMode" type="primary" @click="switchToEdit">
            进入编辑
          </el-button>
          <el-button
            v-else
            type="primary"
            :loading="saving"
            @click="handleSubmit"
          >
            保存修改
          </el-button>
        </div>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="right"
        label-width="120px"
        status-icon
        size="default"
        class="main-form"
        :disabled="isViewMode"
      >
        <div class="form-section">
          <div class="section-header">
            <span class="section-title">基本信息</span>
          </div>
          <el-row :gutter="32">
            <el-col :span="8">
              <el-form-item label="项目来源" prop="source">
                <el-select v-model="form.source" placeholder="请选择" class="w-full">
                  <el-option
                    v-for="item in sourceOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="项目级别" prop="level">
                <el-select v-model="form.level" placeholder="请选择" class="w-full">
                  <el-option
                    v-for="item in levelOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="项目类别" prop="category">
                <el-select v-model="form.category" placeholder="请选择" class="w-full">
                  <el-option
                    v-for="item in categoryOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="重点领域" prop="is_key_field">
                <el-cascader
                  v-model="keyFieldCascaderValue"
                  :options="keyFieldCascaderOptions"
                  placeholder="请选择"
                  class="w-full"
                  :props="{ expandTrigger: 'hover' }"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="项目名称" prop="title">
                <el-input v-model="form.title" placeholder="请输入项目全称" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="经费预算" prop="budget">
                <el-input-number
                  v-model="form.budget"
                  :min="0"
                  :precision="2"
                  class="w-full"
                  controls-position="right"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="所属学院">
                <el-select v-model="form.college" class="w-full" disabled>
                  <el-option
                    v-for="item in collegeOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="所属专业">
                <el-select v-model="form.major_code" class="w-full" filterable disabled>
                  <el-option
                    v-for="item in majorOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-header">
            <span class="section-title">负责人信息</span>
          </div>
          <el-row :gutter="32">
            <el-col :span="8">
              <el-form-item label="负责人姓名">
                <el-input v-model="form.leader_name" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="负责人学号">
                <el-input
                  v-model="form.leader_student_id"
                  disabled
                  class="is-disabled-soft"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="联系电话">
                <el-input v-model="form.leader_contact" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="电子邮箱">
                <el-input v-model="form.leader_email" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-header">
            <span class="section-title">指导教师</span>
          </div>
          <el-table
            :data="form.advisors"
            style="width: 100%"
            border
            :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          >
            <el-table-column label="次序" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.order === 1 ? 'primary' : 'success'" effect="plain">
                  {{ scope.row.order === 1 ? "第一指导老师" : "第二指导老师" }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="job_number" label="工号" width="120" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="title" label="职称" width="120">
              <template #default="scope">
                {{ getLabel(advisorTitleOptions, scope.row.title) }}
              </template>
            </el-table-column>
            <el-table-column prop="contact" label="电话" />
            <el-table-column prop="email" label="邮箱" />
            <template #empty>
              <div class="empty-text">暂无指导教师信息</div>
            </template>
          </el-table>
        </div>

        <div class="form-section">
          <div class="section-header">
            <span class="section-title">团队成员</span>
          </div>
          <el-table
            :data="form.members"
            style="width: 100%"
            border
            :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          >
            <el-table-column prop="student_id" label="学号" width="140" />
            <el-table-column prop="name" label="姓名" width="140" />
            <el-table-column prop="role" label="角色">
              <template #default="scope">
                <el-tag size="small" effect="plain" type="info">
                  {{ scope.row.role === "LEADER" ? "负责人" : "成员" }}
                </el-tag>
              </template>
            </el-table-column>
            <template #empty>
              <div class="empty-text">暂无成员信息</div>
            </template>
          </el-table>
        </div>

        <div class="form-section">
          <div class="section-header">
            <span class="section-title">项目信息</span>
          </div>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="预期成果" prop="expected_results">
                <el-input
                  type="textarea"
                  v-model="form.expected_results"
                  :rows="5"
                  placeholder="预期的项目成果"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="项目简介" prop="description">
                <el-input
                  type="textarea"
                  v-model="form.description"
                  :rows="5"
                  placeholder="项目简介"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import { getProjectDetail, updateProjectInfo } from "@/api/admin";

interface AdvisorInfo {
  job_number: string;
  name: string;
  title: string;
  contact?: string;
  email?: string;
  order: number;
}

interface MemberInfo {
  student_id: string;
  name: string;
  role?: string;
}

const router = useRouter();
const route = useRoute();

const { loadDictionaries, getOptions } = useDictionary();

const pageLoading = ref(false);
const saving = ref(false);

const formRef = ref();
const form = reactive<any>({
  id: null,
  project_no: "",
  status_display: "",
  source: "",
  level: "",
  category: "",
  is_key_field: false,
  key_field_code: "",
  title: "",
  budget: 0,
  college: "",
  major_code: "",
  leader_name: "",
  leader_student_id: "",
  leader_contact: "",
  leader_email: "",
  expected_results: "",
  description: "",
  advisors: [] as AdvisorInfo[],
  members: [] as MemberInfo[],
});

const isViewMode = computed(() => route.query.mode !== "edit");
const pageTitle = computed(() =>
  isViewMode.value ? "项目详情" : "编辑项目信息"
);

const rules = {
  title: [{ required: true, message: "请输入项目名称", trigger: "blur" }],
  level: [{ required: true, message: "请选择项目级别", trigger: "change" }],
  category: [{ required: true, message: "请选择项目类别", trigger: "change" }],
};

const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
const sourceOptions = computed(() => getOptions(DICT_CODES.PROJECT_SOURCE));
const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
const majorOptions = computed(() => getOptions(DICT_CODES.MAJOR_CATEGORY));
const keyFieldOptions = computed(() => getOptions(DICT_CODES.KEY_FIELD_CODE));
const advisorTitleOptions = computed(() => getOptions(DICT_CODES.ADVISOR_TITLE));

const keyFieldCascaderOptions = computed(() => {
  const children = keyFieldOptions.value.map((opt: any) => ({
    value: opt.value,
    label: opt.label,
  }));
  return [
    { value: "GENERAL", label: "一般项目" },
    {
      value: "KEY",
      label: "重点领域项目",
      children: children.length
        ? children
        : [{ value: "", label: "暂无数据 (请在后台添加)", disabled: true }],
    },
  ];
});

const keyFieldCascaderValue = computed({
  get: () => {
    if (!form.is_key_field) return ["GENERAL"];
    return form.key_field_code ? ["KEY", form.key_field_code] : ["KEY"];
  },
  set: (val: string[]) => {
    if (!val || val.length === 0) return;
    if (val[0] === "GENERAL") {
      form.is_key_field = false;
      form.key_field_code = "";
    } else if (val[0] === "KEY") {
      form.is_key_field = true;
      if (val.length > 1) {
        form.key_field_code = val[1];
      }
    }
  },
});

watch(
  () => form.level,
  (newVal) => {
    if (!newVal) {
      form.budget = 0;
      return;
    }
    const selected = levelOptions.value.find((opt: any) => opt.value === newVal);
    if (selected && selected.extra_data && selected.extra_data.budget) {
      form.budget = Number(selected.extra_data.budget);
    }
  }
);

const getLabel = (options: any[], value: string) => {
  const found = options.find((opt) => opt.value === value);
  return found ? found.label : value;
};

const loadProject = async () => {
  const id = Number(route.params.id);
  if (!id) {
    ElMessage.error("未找到项目");
    router.back();
    return;
  }
  pageLoading.value = true;
  try {
    const res: any = await getProjectDetail(id);
    const data = res.data || res;
    if (!data) {
      throw new Error("数据为空");
    }
    form.id = data.id;
    form.project_no = data.project_no || "";
    form.status_display = data.status_display || "";
    form.source = data.source || "";
    form.level = data.level || "";
    form.category = data.category || "";
    form.is_key_field = !!data.is_key_field;
    form.key_field_code = data.key_domain_code || data.key_field_code || "";
    form.title = data.title || "";
    form.budget = Number(data.budget || 0);
    form.college = data.college || "";
    form.major_code = data.major_code || "";
    form.leader_name = data.leader_name || "";
    form.leader_student_id = data.leader_student_id || data.student_id || "";
    form.leader_contact = data.leader_contact || "";
    form.leader_email = data.leader_email || "";
    form.expected_results = data.expected_results || "";
    form.description = data.description || "";

    if (Array.isArray(data.advisors_info)) {
      form.advisors = data.advisors_info.map((item: any, index: number) => ({
        job_number: item.job_number || "",
        name: item.name || "",
        title: item.title || "",
        contact: item.contact || "",
        email: item.email || "",
        order: item.order || index + 1,
      }));
    } else {
      form.advisors = [];
    }

    if (Array.isArray(data.members_info)) {
      form.members = data.members_info.map((item: any) => ({
        student_id: item.student_id || "",
        name: item.user_name || item.name || "",
        role: item.role || "MEMBER",
      }));
    } else {
      form.members = [];
    }
  } catch (error: any) {
    ElMessage.error(error.message || "加载项目详情失败");
  } finally {
    pageLoading.value = false;
  }
};

const handleSubmit = async () => {
  if (isViewMode.value) return;
  if (!formRef.value) return;
  // 重点领域校验：非一般项目必须选择重点领域代码
  if (form.is_key_field && !form.key_field_code) {
    ElMessage.error("请选择重点领域代码");
    return;
  }
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) {
      ElMessage.error("请完善必填信息");
      return;
    }
    saving.value = true;
    // Build payload outside try so we can log on failure
    const payload = {
      title: form.title,
      source: form.source || null,
      level: form.level || null,
      category: form.category || null,
      is_key_field: !!form.is_key_field,
      key_domain_code: form.key_field_code || "",
      budget: Number(form.budget) || 0,
      expected_results: form.expected_results,
      description: form.description,
    };
    try {
      console.info("Submitting project update payload:", payload);
      await updateProjectInfo(form.id, payload);
      ElMessage.success("保存成功");
      router.replace({
        name: "level1-project-detail",
        params: { id: form.id },
        query: { mode: "view" },
      });
    } catch (error: any) {
      // Surface后端返回的详细错误，方便排查
      const resp = error?.response;
      const respData: any = resp?.data;
      console.error("Update project failed", {
        payload,
        status: resp?.status,
        response: respData || error,
        headers: resp?.headers,
      });
      let msg = error?.message || "保存失败";
      if (respData) {
        if (respData.message) {
          msg = respData.message;
        } else if (typeof respData === "object") {
          const details = Object.entries(respData)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join("; ") : v}`)
            .join("；");
          if (details) msg = `${msg}：${details}`;
        } else if (typeof respData === "string") {
          msg = `${msg}：${respData}`;
        }
      }
      ElMessage.error(msg);
    } finally {
      saving.value = false;
    }
  });
};

const switchToEdit = () => {
  router.replace({
    name: "level1-project-detail",
    params: { id: form.id || route.params.id },
    query: { mode: "edit" },
  });
};

onMounted(async () => {
  await loadDictionaries([
    DICT_CODES.PROJECT_LEVEL,
    DICT_CODES.PROJECT_CATEGORY,
    DICT_CODES.PROJECT_SOURCE,
    DICT_CODES.COLLEGE,
    DICT_CODES.MAJOR_CATEGORY,
    DICT_CODES.KEY_FIELD_CODE,
    DICT_CODES.ADVISOR_TITLE,
  ]);
  await loadProject();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.form-container {
  background: white;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  border: 1px solid $color-border-light;
  overflow: hidden;
}

.page-header {
  padding: 16px 24px;
  border-bottom: 1px solid $slate-100;
  display: flex;
  align-items: center;
  justify-content: space-between;

  .title-bar {
    display: flex;
    align-items: center;
    gap: 12px;

    .title {
      font-size: 16px;
      font-weight: 600;
      color: $slate-800;
      position: relative;
      padding-left: 14px;

      &::before {
        content: "";
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 16px;
        background: $primary-600;
        border-radius: 2px;
      }
    }
  }
}

.main-form {
  padding: 32px;
}

.form-section {
  margin-bottom: 40px;

  &:last-child {
    margin-bottom: 0;
  }

  .section-header {
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px dashed $slate-200;
    padding-bottom: 8px;

    .section-title {
      font-size: 15px;
      font-weight: 600;
      color: $slate-700;
    }
  }
}

.w-full {
  width: 100%;
}

.empty-text {
  color: $slate-400;
  font-size: 13px;
  text-align: center;
  padding: 8px 0;
}
</style>
