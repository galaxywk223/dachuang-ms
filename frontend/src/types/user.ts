export enum UserRole {
  STUDENT = "student",
  LEVEL1_ADMIN = "level1_admin", // 一级管理员（校级）
  LEVEL2_ADMIN = "level2_admin", // 二级管理员（院级）
  TEACHER = "teacher",
  EXPERT = "expert",
  ADMIN = "admin", // Legacy/Generic admin
}

export interface User {
  id: number;
  employee_id: string;
  username: string;
  real_name?: string;
  email: string;
  role: UserRole;
  expert_scope?: string;
  department?: string;
  college?: string;
  phone?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface LoginForm {
  employee_id: string;
  password: string;
}

export interface PasswordChangeForm {
  old_password: string;
  new_password: string;
  confirm_password: string;
}
