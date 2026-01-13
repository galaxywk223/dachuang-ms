#!/usr/bin/env python3
"""
批量更新管理员评审页面的脚本
为所有管理员审核页面添加动态工作流退回节点选择功能
"""

import re
from pathlib import Path

# 需要更新的文件列表（已排除level1/Establishment，它已完成）
FILES_TO_UPDATE = [
    "frontend/src/views/admin/level1/review/Closure.vue",
    "frontend/src/views/admin/level2/review/Establishment.vue",
    "frontend/src/views/admin/level2/review/MidTerm.vue",
    "frontend/src/views/admin/level2/review/Closure.vue",
]


def update_imports(content: str) -> str:
    """添加API导入"""
    # 查找request导入行
    import_pattern = r'(import request from "@/utils/request";)'
    replacement = r'\1\nimport { getRejectTargetsByProject, type WorkflowNode } from "@/api/reviews";'

    if "getRejectTargetsByProject" not in content:
        content = re.sub(import_pattern, replacement, content, count=1)

    return content


def add_reactive_variables(content: str) -> str:
    """添加响应式变量"""
    # 在reviewForm定义后添加rejectTargets
    if "const rejectTargets = ref" not in content:
        # 查找reviewForm定义的结束位置
        pattern = r"(const reviewForm = ref\(\{[^}]+\}\);)"
        replacement = r"\1\nconst rejectTargets = ref<WorkflowNode[]>([]);"
        content = re.sub(pattern, replacement, content, count=1)

    # 在reviewForm中添加target_node_id字段
    if "target_node_id:" not in content:
        pattern = r'(const reviewForm = ref\(\{[^}]*return_to: "[^"]+",)'
        replacement = r"\1\n  target_node_id: null as number | null,"
        content = re.sub(pattern, replacement, content, count=1)

    return content


def update_handle_reject(content: str) -> str:
    """更新handleReject函数为async并加载退回节点"""
    # 查找handleReject函数
    pattern = r"const handleReject = \(row: ProjectRow\) => \{([^}]*)\};"

    def replacer(match):
        body = match.group(1)
        # 如果已经是async，跳过
        if "await getRejectTargetsByProject" in body:
            return match.group(0)

        # 构建新的函数体
        new_body = f"""
  reviewType.value = "reject";
  reviewForm.value.projectId = row.id;
  reviewForm.value.comment = "";
  reviewForm.value.return_to = "student";
  reviewForm.value.target_node_id = null;
  rejectTargets.value = [];
  // 加载可退回节点
  try {{
    const res = await getRejectTargetsByProject(row.id);
    if (res.code === 200) {{
      rejectTargets.value = res.data || [];
    }}
  }} catch (error) {{
    console.error("获取退回节点失败", error);
    rejectTargets.value = [];
  }}
  reviewDialogVisible.value = true;
"""
        return f"const handleReject = async (row: ProjectRow) => {{{new_body}}};"

    content = re.sub(pattern, replacer, content, flags=re.DOTALL)
    return content


def add_template_selector(content: str) -> str:
    """在模板中添加节点选择器"""
    # 在退回原因输入框之后，return_to选择之前添加节点选择器
    if "v-if=\"reviewType === 'reject' && rejectTargets.length > 0\"" in content:
        return content  # 已添加

    selector_html = """
        <el-form-item
          label="退回至"
          v-if="reviewType === 'reject' && rejectTargets.length > 0"
        >
          <el-select
            v-model="reviewForm.target_node_id"
            placeholder="请选择退回节点"
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="node in rejectTargets"
              :key="node.id"
              :label="node.name"
              :value="node.id"
            >
              <span>{{ node.name }}</span>
              <span style="float: right; color: var(--el-text-color-secondary); font-size: 12px">
                {{ node.role }}
              </span>
            </el-option>
          </el-select>
          <div style="color: var(--el-text-color-secondary); font-size: 12px; margin-top: 4px">
            未选择时将使用下方的退回规则或默认退回节点
          </div>
        </el-form-item>
"""

    # 在驳回原因之后、return_to之前插入
    pattern = r'(</el-form-item>\s*<el-form-item v-if="reviewType === \'reject\'" label="退回到">)'
    replacement = selector_html + r"\1"
    content = re.sub(pattern, replacement, content, count=1)

    return content


def update_confirm_review(content: str) -> str:
    """更新confirmReview函数，传递target_node_id"""
    # 查找reject数据构建部分
    pattern = r"(const data:[^{]*\{[^}]*comment: reviewForm\.value\.comment,[^}]*\})"

    if "target_node_id" in content and "data.target_node_id" in content:
        return content  # 已更新

    # 这个更复杂，需要手动处理每个文件
    print("  Note: confirmReview需要手动检查和更新")

    return content


def update_file(filepath: Path):
    """更新单个文件"""
    print(f"\n更新文件: {filepath}")

    if not filepath.exists():
        print(f"  ⚠️  文件不存在: {filepath}")
        return False

    # 读取文件
    content = filepath.read_text(encoding="utf-8")
    original_content = content

    # 应用所有更新
    content = update_imports(content)
    content = add_reactive_variables(content)
    content = update_handle_reject(content)
    content = add_template_selector(content)
    content = update_confirm_review(content)

    # 如果有变化，写回文件
    if content != original_content:
        filepath.write_text(content, encoding="utf-8")
        print("  ✅ 文件已更新")
        return True
    else:
        print("  ℹ️  无需更新")
        return False


def main():
    """主函数"""
    print("开始批量更新管理员评审页面...")
    print("=" * 60)

    project_root = Path(__file__).parent.parent
    updated_count = 0

    for file_path in FILES_TO_UPDATE:
        full_path = project_root / file_path
        if update_file(full_path):
            updated_count += 1

    print("\n" + "=" * 60)
    print(f"完成！共更新 {updated_count}/{len(FILES_TO_UPDATE)} 个文件")
    print("\n⚠️  注意事项：")
    print("1. 请手动检查每个文件的 confirmReview 函数")
    print("2. 确保在 rejectProject 调用时传递 target_node_id")
    print("3. 运行 'npm run dev' 检查是否有编译错误")
    print("4. 测试每个审核页面的退回功能")


if __name__ == "__main__":
    main()
