/**
 * 批次工作流配置 API
 */

import request from "@/utils/request";

export interface WorkflowNode {
  id: number;
  code: string;
  name: string;
  node_type: "SUBMIT" | "REVIEW" | "APPROVAL";
  role_fk: number | null;
  role_name: string | null;
  role_code: string | null;
  require_expert_review: boolean;
  return_policy: string;
  allowed_reject_to: number | null;
  notice: string;
  sort_order: number;
  is_active: boolean;
  can_edit: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkflowConfig {
  id: number;
  name: string;
  phase: "APPLICATION" | "MID_TERM" | "CLOSURE" | "BUDGET" | "CHANGE";
  batch: number | null;
  batch_name: string | null;
  version: number;
  description: string;
  is_active: boolean;
  is_locked: boolean;
  nodes: WorkflowNode[];
  node_count: number;
  created_by: number | null;
  updated_by: number | null;
  created_at: string;
  updated_at: string;
}

export interface BatchWorkflowSummary {
  phase: string;
  phase_display: string;
  workflow_id: number | null;
  workflow_name: string | null;
  node_count: number;
  is_active: boolean;
  is_locked: boolean;
  has_student_node: boolean;
  validation_errors: string[];
}

export interface WorkflowNodeInput {
  code: string;
  name: string;
  node_type: "SUBMIT" | "REVIEW" | "APPROVAL";
  role_fk?: number;
  require_expert_review?: boolean;
  return_policy?: string;
  allowed_reject_to?: number | null;
  notice?: string;
  sort_order: number;
  is_active?: boolean;
}

/**
 * 获取批次的所有工作流配置汇总
 */
export function getBatchWorkflows(batchId: number) {
  return request<BatchWorkflowSummary[]>({
    url: `/system-settings/batch-workflows/${batchId}/workflows/`,
    method: "get",
  });
}

/**
 * 获取批次指定阶段的工作流详情
 */
export function getBatchWorkflow(batchId: number, phase: string) {
  return request<WorkflowConfig>({
    url: `/system-settings/batch-workflows/${batchId}/workflows/${phase}/`,
    method: "get",
  });
}

/**
 * 初始化批次指定阶段的默认工作流
 */
export function initBatchWorkflow(batchId: number, phase: string) {
  return request<WorkflowConfig>({
    url: `/system-settings/batch-workflows/${batchId}/workflows/${phase}/init/`,
    method: "post",
  });
}

/**
 * 获取批次指定阶段工作流的所有节点
 */
export function getBatchWorkflowNodes(batchId: number, phase: string) {
  return request<WorkflowNode[]>({
    url: `/system-settings/batch-workflows/${batchId}/workflows/${phase}/nodes/`,
    method: "get",
  });
}

/**
 * 创建工作流节点
 */
export function createWorkflowNode(
  batchId: number,
  phase: string,
  data: WorkflowNodeInput
) {
  return request<WorkflowNode>({
    url: `/system-settings/batch-workflows/${batchId}/workflows/${phase}/nodes/`,
    method: "post",
    data,
  });
}

/**
 * 更新工作流节点
 */
export function updateWorkflowNode(
  batchId: number,
  phase: string,
  nodeId: number,
  data: Partial<WorkflowNodeInput>
) {
  return request<WorkflowNode>({
    url: `/system-settings/batch-workflows/${batchId}/workflows/${phase}/nodes/${nodeId}/`,
    method: "patch",
    data,
  });
}

/**
 * 删除工作流节点
 */
export function deleteWorkflowNode(
  batchId: number,
  phase: string,
  nodeId: number
) {
  return request({
    url: `/system-settings/batch-workflows/${batchId}/workflows/${phase}/nodes/${nodeId}/`,
    method: "delete",
  });
}

/**
 * 重新排序工作流节点
 */
export function reorderWorkflowNodes(
  batchId: number,
  phase: string,
  nodeIds: number[]
) {
  return request<WorkflowNode[]>({
    url: `/system-settings/batch-workflows/${batchId}/workflows/${phase}/nodes/reorder/`,
    method: "post",
    data: { node_ids: nodeIds },
  });
}

/**
 * 验证工作流配置的合法性
 */
export function validateBatchWorkflow(batchId: number, phase: string) {
  return request<{ valid: boolean; errors: string[] }>({
    url: `/system-settings/batch-workflows/${batchId}/workflows/${phase}/validate/`,
    method: "post",
  });
}
