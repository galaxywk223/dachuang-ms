import { ref } from "vue";

export interface DictionaryTreeNode {
  id: string;
  label: string;
  children?: DictionaryTreeNode[];
}

/**
 * 字典类型中文名称映射
 */
export const DICTIONARY_LABELS: Record<string, string> = {
  // 项目参数
  project_level: "项目级别",
  project_type: "项目类别",
  project_source: "项目来源",
  key_field_code: "重点领域代码",

  // 组织参数
  college: "学院",
  major_category: "专业大类",
  title: "职称",

  // 成果参数
  achievement_type: "成果类型",
};

/**
 * 字典分类树结构
 */
export const DICTIONARY_TREE: DictionaryTreeNode[] = [
  {
    id: "project",
    label: "项目参数",
    children: [
      { id: "project_level", label: "项目级别" },
      { id: "project_type", label: "项目类别" },
      { id: "project_source", label: "项目来源" },
      { id: "key_field_code", label: "重点领域代码" },
    ],
  },
  {
    id: "org",
    label: "组织参数",
    children: [
      { id: "college", label: "学院" },
      { id: "major_category", label: "专业大类" },
      { id: "title", label: "职称" },
    ],
  },
  {
    id: "achievement",
    label: "成果参数",
    children: [{ id: "achievement_type", label: "成果类型" }],
  },
];

/**
 * 使用字典树
 */
export function useDictionaryTree() {
  const treeData = ref<DictionaryTreeNode[]>(DICTIONARY_TREE);
  const selectedNode = ref<string>("");
  const selectedCategory = ref<string>("");

  /**
   * 选择树节点
   */
  const selectNode = (nodeId: string) => {
    selectedNode.value = nodeId;

    // 判断是分类还是具体字典类型
    const isCategory = DICTIONARY_TREE.some((cat) => cat.id === nodeId);
    if (isCategory) {
      selectedCategory.value = nodeId;
    } else {
      // 查找所属分类
      for (const category of DICTIONARY_TREE) {
        if (category.children?.some((child) => child.id === nodeId)) {
          selectedCategory.value = category.id;
          break;
        }
      }
    }
  };

  /**
   * 获取节点标签
   */
  const getNodeLabel = (nodeId: string): string => {
    return DICTIONARY_LABELS[nodeId] || nodeId;
  };

  /**
   * 判断是否是字典类型节点（叶子节点）
   */
  const isDictionaryType = (nodeId: string): boolean => {
    return !DICTIONARY_TREE.some((cat) => cat.id === nodeId);
  };

  return {
    treeData,
    selectedNode,
    selectedCategory,
    selectNode,
    getNodeLabel,
    isDictionaryType,
  };
}
