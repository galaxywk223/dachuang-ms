<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">基本信息</span>
    </div>
    <el-row :gutter="24">
      <el-col :span="24">
        <el-form-item label="项目名称" prop="title">
          <el-input v-model="localFormData.title" placeholder="请输入项目全称" />
        </el-form-item>
      </el-col>

      <el-col :span="12">
        <el-form-item label="项目来源" prop="source">
          <el-select v-model="localFormData.source" placeholder="请选择" class="w-full">
            <el-option v-for="item in sourceOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="项目级别" prop="level">
          <el-select v-model="localFormData.level" placeholder="请选择" class="w-full">
            <el-option v-for="item in levelOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>

      <el-col :span="12">
        <el-form-item label="项目类别" prop="category">
          <el-select v-model="localFormData.category" placeholder="请选择" class="w-full">
            <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="学科分类" prop="discipline">
          <el-select v-model="localFormData.discipline" placeholder="请选择" class="w-full" filterable>
            <el-option v-for="item in disciplineOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="重点领域" prop="is_key_field">
          <el-cascader
            v-model="localKeyFieldCascaderValue"
            :options="keyFieldCascaderOptions"
            placeholder="请选择"
            class="w-full"
            style="width: 100%"
            :props="{ expandTrigger: 'hover' }"
          />
        </el-form-item>
      </el-col>

      <el-col :span="12">
        <el-form-item label="所属学院" prop="college">
          <el-select v-model="localFormData.college" placeholder="请选择" class="w-full">
            <el-option v-for="item in collegeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="所属专业" prop="major_code">
          <el-select v-model="localFormData.major_code" placeholder="请选择" class="w-full" filterable>
            <el-option v-for="item in majorOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>

      <el-col :span="12">
        <el-form-item label="经费预算" prop="budget">
          <el-input-number
            v-model="localFormData.budget"
            :min="0"
            class="w-full"
            controls-position="right"
            disabled
            placeholder="自动生成"
            style="width: 100%"
          />
        </el-form-item>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from "vue";
import type { CascaderOption } from "element-plus";

type OptionItem = {
  value: string;
  label: string;
};

type BasicFormData = {
  title: string;
  source?: string;
  level?: string;
  category?: string;
  discipline?: string;
  college?: string;
  major_code?: string;
  budget?: number;
  is_key_field?: string[] | string | boolean;
};

const props = defineProps<{
  formData: BasicFormData;
  sourceOptions: OptionItem[];
  levelOptions: OptionItem[];
  categoryOptions: OptionItem[];
  disciplineOptions: OptionItem[];
  keyFieldCascaderOptions: CascaderOption[];
  keyFieldCascaderValue: string[];
  collegeOptions: OptionItem[];
  majorOptions: OptionItem[];
}>();

const emit = defineEmits<{
  (event: "update:formData", value: BasicFormData): void;
  (event: "update:keyFieldCascaderValue", value: string[]): void;
}>();

const localFormData = reactive<BasicFormData>({
  title: "",
  source: "",
  level: "",
  category: "",
  discipline: "",
  college: "",
  major_code: "",
  budget: 0,
  is_key_field: "",
});

watch(
  () => props.formData,
  (value) => {
    Object.assign(localFormData, value);
  },
  { immediate: true, deep: true }
);

watch(
  localFormData,
  (value) => {
    emit("update:formData", { ...value });
  },
  { deep: true }
);

const localKeyFieldCascaderValue = computed({
  get: () => props.keyFieldCascaderValue,
  set: (value: string[]) => emit("update:keyFieldCascaderValue", value),
});
</script>
