<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">申报内容</span>
    </div>
    <el-row>
      <el-col :span="24">
        <el-form-item label="预期成果" prop="expected_results">
          <el-input
            v-model="formData.expected_results"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="请列出具体成果形式，如：发表论文1篇、软件著作权1项等"
          />
        </el-form-item>
      </el-col>
      <el-col :span="24">
        <el-form-item label="预期成果清单">
          <div class="expected-grid">
            <el-select
              v-model="expectedForm.achievement_type"
              placeholder="成果类型"
              class="expected-select"
            >
              <el-option
                v-for="item in achievementTypeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
            <el-input-number
              v-model="expectedForm.expected_count"
              :min="1"
              controls-position="right"
              class="expected-count"
            />
            <el-button type="primary" plain @click="addExpectedResult">
              <el-icon class="mr-1"><Plus /></el-icon> 添加
            </el-button>
          </div>
          <el-table
            v-if="formData.expected_results_data.length"
            :data="formData.expected_results_data"
            border
            style="width: 100%; margin-top: 12px;"
            :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          >
            <el-table-column label="成果类型">
              <template #default="{ row }">
                {{ getLabel(achievementTypeOptions, row.achievement_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="expected_count" label="数量" width="120" />
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ $index }">
                <el-button link type="danger" @click="removeExpectedResult($index)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-col>
      <el-col :span="24">
        <el-form-item label="项目简介" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="6"
            maxlength="500"
            show-word-limit
            placeholder="请简要介绍项目背景、创新点及研究内容"
          />
        </el-form-item>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { Plus } from "@element-plus/icons-vue";

defineProps<{
  formData: any;
  expectedForm: any;
  achievementTypeOptions: any[];
  getLabel: (options: any[], value: string) => string;
  addExpectedResult: () => void;
  removeExpectedResult: (index: number) => void;
}>();
</script>
