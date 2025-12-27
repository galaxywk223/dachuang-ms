<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">基本信息</span>
    </div>
    <el-row :gutter="24">
      <el-col :span="24">
        <el-form-item label="项目名称" prop="title">
          <el-input v-model="formData.title" placeholder="请输入项目全称" />
        </el-form-item>
      </el-col>

      <el-col :span="12">
        <el-form-item label="项目来源" prop="source">
          <el-select v-model="formData.source" placeholder="请选择" class="w-full">
            <el-option v-for="item in sourceOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="项目级别" prop="level">
          <el-select v-model="formData.level" placeholder="请选择" class="w-full">
            <el-option v-for="item in levelOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>

      <el-col :span="12">
        <el-form-item label="项目类别" prop="category">
          <el-select v-model="formData.category" placeholder="请选择" class="w-full">
            <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="学科分类" prop="discipline">
          <el-select v-model="formData.discipline" placeholder="请选择" class="w-full" filterable>
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
          <el-select v-model="formData.college" placeholder="请选择" class="w-full">
            <el-option v-for="item in collegeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="所属专业" prop="major_code">
          <el-select v-model="formData.major_code" placeholder="请选择" class="w-full" filterable>
            <el-option v-for="item in majorOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-col>

      <el-col :span="12">
        <el-form-item label="经费预算" prop="budget">
          <el-input-number
            v-model="formData.budget"
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
import { computed } from "vue";

const props = defineProps<{
  formData: any;
  sourceOptions: any[];
  levelOptions: any[];
  categoryOptions: any[];
  disciplineOptions: any[];
  keyFieldCascaderOptions: any[];
  keyFieldCascaderValue: string[];
  collegeOptions: any[];
  majorOptions: any[];
}>();

const emit = defineEmits<{
  (event: "update:keyFieldCascaderValue", value: string[]): void;
}>();

const localKeyFieldCascaderValue = computed({
  get: () => props.keyFieldCascaderValue,
  set: (value: string[]) => emit("update:keyFieldCascaderValue", value),
});
</script>
