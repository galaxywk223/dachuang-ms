import request from "@/utils/request";

/**
 * 字典条目类型
 */
export interface DictionaryItem {
  id?: number;
  value: string;
  label: string;
  extra_data?: Record<string, unknown>;
  template_file?: string;
}

/**
 * 字典数据类型
 */
export interface DictionaryData {
  name: string;
  items: DictionaryItem[];
}

/**
 * 批量字典响应类型
 */
export type DictionaryBatchResponse = Record<string, DictionaryData>;

/**
 * 根据编码获取单个字典
 */
export function getDictionaryByCode(code: string): Promise<{
  code: string;
  name: string;
  items: DictionaryItem[];
}> {
  return request({
    url: `/dictionaries/types/by-code/${code}/`,
    method: "get",
  });
}

/**
 * 批量获取多个字典
 */
export function getDictionariesBatch(
  codes: string[]
): Promise<DictionaryBatchResponse> {
  return request({
    url: "/dictionaries/types/batch/",
    method: "post",
    data: { codes },
  });
}

/**
 * 获取所有字典数据
 */
export function getAllDictionaries(): Promise<DictionaryBatchResponse> {
  return request({
    url: "/dictionaries/types/all/",
    method: "get",
  });
}

/**
 * 创建字典项
 */
export function createDictionaryItem(
  data: Record<string, unknown> | FormData
): Promise<unknown> {
  return request({
    url: "/dictionaries/items/",
    method: "post",
    data,
    headers: {
      "Content-Type":
        data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

/**
 * 更新字典项
 */
export function updateDictionaryItem(
  id: number,
  data: Record<string, unknown> | FormData
): Promise<unknown> {
  return request({
    url: `/dictionaries/items/${id}/`,
    method: "patch", // Use PATCH for partial updates
    data,
    headers: {
      "Content-Type":
        data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

/**
 * 删除字典项
 */
export function deleteDictionaryItem(id: number) {
  return request({
    url: `/dictionaries/items/${id}/`,
    method: "delete",
  });
}

/**
 * 常用字典编码常量
 */
export const DICT_CODES = {
  USER_ROLE: "user_role",
  PROJECT_STATUS: "project_status",
  PROJECT_LEVEL: "project_level",
  PROJECT_CATEGORY: "project_type", // Merged
  MEMBER_ROLE: "member_role",
  ACHIEVEMENT_TYPE: "achievement_type",
  REVIEW_TYPE: "review_type",
  REVIEW_LEVEL: "review_level",
  REVIEW_STATUS: "review_status",
  CLOSURE_RATING: "closure_rating",
  NOTIFICATION_TYPE: "notification_type",
  // New codes
  PROJECT_SOURCE: "project_source",
  COLLEGE: "college",
  MAJOR_CATEGORY: "major_category", // Corrected
  TITLE: "title",
  KEY_FIELD_CODE: "key_field_code",
  PROJECT_TYPE: "project_type",
  // Backward-compatible aliases (avoid null codes in batch requests)
  SPECIAL_PROJECT_TYPE: "project_type", // Not used anymore but kept safe
  ADVISOR_TITLE: "title",
} as const;
