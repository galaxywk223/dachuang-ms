<template>
  <el-form label-width="200px" class="config-form">
    <el-form-item label="在研项目允许继续申报">
      <el-switch
        v-model="localProcessRules.allow_active_reapply"
        :disabled="isProcessLocked"
      />
      <div class="form-hint">开启后，已有在研项目的学生仍可提交新申报。</div>
    </el-form-item>
    <el-form-item label="审核退回上一级">
      <el-switch
        v-model="localProcessRules.reject_to_previous"
        :disabled="isProcessLocked"
      />
      <div class="form-hint">开启后，退回会返回到上一级角色重新审核。</div>
    </el-form-item>
    <el-form-item label="结题评审可见立项材料">
      <el-switch
        v-model="localProcessRules.show_material_in_closure_review"
        :disabled="isProcessLocked"
      />
      <div class="form-hint">开启后，结题评审可查看立项阶段材料。</div>
    </el-form-item>
    <el-form-item label="导师审核意见最少字数">
      <el-input-number
        v-model="localReviewRules.teacher_application_comment_min"
        :min="0"
        :disabled="isProcessLocked"
      />
      <div class="form-hint">设置为 0 表示不限制字数。</div>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";

const props = defineProps<{
  processRules: {
    allow_active_reapply: boolean;
    reject_to_previous: boolean;
    show_material_in_closure_review: boolean;
  };
  reviewRules: {
    teacher_application_comment_min: number;
  };
  isProcessLocked: boolean;
}>();

const emit = defineEmits<{
  (event: "update:processRules", value: typeof props.processRules): void;
  (event: "update:reviewRules", value: typeof props.reviewRules): void;
}>();

const localProcessRules = reactive({ ...props.processRules });
const localReviewRules = reactive({ ...props.reviewRules });

watch(
  () => props.processRules,
  (val) => Object.assign(localProcessRules, val),
  { deep: true }
);
watch(
  () => props.reviewRules,
  (val) => Object.assign(localReviewRules, val),
  { deep: true }
);

watch(localProcessRules, (val) => emit("update:processRules", { ...val }), {
  deep: true,
});
watch(localReviewRules, (val) => emit("update:reviewRules", { ...val }), {
  deep: true,
});
</script>
<style scoped lang="scss">
.config-form {
  max-width: 800px;
  padding-top: 20px;
}

.form-hint {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  margin-top: 4px;
}
</style>
