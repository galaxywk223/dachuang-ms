// 用户角色类型
export enum UserRole {
  STUDENT = "student",
  LEVEL1_ADMIN = "level1_admin", // 一级管理员（校级）
  LEVEL2_ADMIN = "level2_admin", // 二级管理员（院级）
  TEACHER = "teacher",
  EXPERT = "expert",
  ADMIN = "admin", // Legacy/Generic admin
}

// 用户信息
export interface User {
  id: number;
  employee_id: string;
  username: string;
  real_name?: string;
  email: string;
  role: UserRole;
  department?: string;
  phone?: string;
  created_at: string;
  updated_at: string;
}

// 项目状态
export enum ProjectStatus {
  DRAFT = "draft",
  SUBMITTED = "submitted",
  LEVEL1_REVIEWING = "level1_reviewing",
  LEVEL1_APPROVED = "level1_approved",
  LEVEL1_REJECTED = "level1_rejected",
  LEVEL2_REVIEWING = "level2_reviewing",
  LEVEL2_APPROVED = "level2_approved",
  LEVEL2_REJECTED = "level2_rejected",
}

// 项目信息
export interface Project {
  id: number;
  title: string;
  description: string;
  status: ProjectStatus;
  creator: User;
  members: User[];
  level1_reviewer?: User;
  level2_reviewer?: User;
  created_at: string;
  updated_at: string;
  submitted_at?: string;
}

// 评审意见
export interface Review {
  id: number;
  project: Project | number;
  reviewer: User;
  level: 1 | 2;
  status: "pending" | "approved" | "rejected";
  comment: string;
  score?: number;
  created_at: string;
  updated_at: string;
}

// 通知类型
export enum NotificationType {
  PROJECT_SUBMITTED = "project_submitted",
  REVIEW_ASSIGNED = "review_assigned",
  REVIEW_COMPLETED = "review_completed",
  PROJECT_APPROVED = "project_approved",
  PROJECT_REJECTED = "project_rejected",
  SYSTEM = "system",
}

// 通知信息
export interface Notification {
  id: number;
  recipient: User | number;
  type: NotificationType;
  title: string;
  content: string;
  is_read: boolean;
  related_project?: Project | number;
  created_at: string;
}

// API 响应基础结构
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 分页响应
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// 登录响应
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

// 表单数据类型
export interface LoginForm {
  employee_id: string;
  password: string;
}

export interface PasswordChangeForm {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

export interface ProjectForm {
  title: string;
  description: string;
  member_ids?: number[];
}

export interface ReviewForm {
  status: "approved" | "rejected";
  comment: string;
  score?: number;
}
