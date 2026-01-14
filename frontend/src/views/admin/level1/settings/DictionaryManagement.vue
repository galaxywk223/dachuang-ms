<template>
  <div class="dictionary-management">
    <el-tabs v-model="activeTab" class="custom-tabs">
      <el-tab-pane label="系统参数" name="system">
        <div class="content-wrapper">
          <el-row :gutter="20">
            <!-- 左侧树形导航 -->
            <el-col :span="5">
              <el-card class="tree-card" shadow="never">
                <template #header>
                  <span>参数分类</span>
                </template>
                <el-tree
                  :data="treeData"
                  :props="{ label: 'label', children: 'children' }"
                  node-key="id"
                  :default-expand-all="false"
                  :expand-on-click-node="false"
                  :highlight-current="true"
                  @node-click="handleNodeClick"
                >
                  <template #default="{ node, data }">
                    <span class="tree-node">
                      <el-icon v-if="!isDictionaryType(data.id)">
                        <Folder />
                      </el-icon>
                      <el-icon v-else>
                        <Document />
                      </el-icon>
                      <span class="node-label">{{ node.label }}</span>
                    </span>
                  </template>
                </el-tree>
              </el-card>
            </el-col>

            <!-- 右侧字典项管理 -->
            <el-col :span="19">
              <SystemDictionaries
                v-if="selectedNode && isDictionaryType(selectedNode)"
                :key="selectedNode"
                :category="selectedCategory"
                :dict-type-code="selectedNode"
              />
              <el-card v-else class="empty-card" shadow="never">
                <el-empty description="请从左侧选择具体的字典类型进行管理" />
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
      <el-tab-pane label="用户角色" name="roles">
        <RoleManagement />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Folder, Document } from "@element-plus/icons-vue";
import { useDictionaryTree } from "@/composables/useDictionaryTree";
import SystemDictionaries from "./SystemDictionaries.vue";
// Import RoleManagement from its location
import RoleManagement from "@/views/admin/level1/users/RoleManagement.vue";

const activeTab = ref("system");

const {
  treeData,
  selectedNode,
  selectedCategory,
  selectNode,
  isDictionaryType,
} = useDictionaryTree();

/**
 * 处理树节点点击
 */
const handleNodeClick = (data: { id: string }) => {
  // 只有点击叶子节点（字典类型）才加载数据
  if (isDictionaryType(data.id)) {
    selectNode(data.id);
  }
};
</script>

<style scoped lang="scss">
.dictionary-management {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;

    .title {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }

  .content-wrapper {
    .tree-card {
      min-height: calc(100vh - 180px);

      :deep(.el-card__header) {
        font-weight: 600;
        padding: 16px 20px;
        background: #f8fafc;
      }

      :deep(.el-card__body) {
        padding: 10px;
      }

      .tree-node {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
        padding: 4px 0;

        .el-icon {
          font-size: 16px;
          color: #909399;
        }

        .node-label {
          font-size: 14px;
          color: #606266;
        }
      }

      :deep(.el-tree) {
        .el-tree-node__content {
          height: 36px;
          border-radius: 4px;

          &:hover {
            background-color: #f5f7fa;
          }
        }

        .el-tree-node.is-current > .el-tree-node__content {
          background-color: #ecf5ff;
          color: #409eff;

          .tree-node {
            .el-icon,
            .node-label {
              color: #409eff;
            }
          }
        }
      }
    }

    .empty-card {
      min-height: calc(100vh - 180px);
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}
</style>
