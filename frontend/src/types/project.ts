import type { User } from "./user";

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
