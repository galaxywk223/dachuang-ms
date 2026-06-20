import type { Project } from "./project";
import type { User } from "./user";

export enum NotificationType {
  PROJECT_SUBMITTED = "project_submitted",
  REVIEW_ASSIGNED = "review_assigned",
  REVIEW_COMPLETED = "review_completed",
  PROJECT_APPROVED = "project_approved",
  PROJECT_REJECTED = "project_rejected",
  SYSTEM = "system",
}

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
