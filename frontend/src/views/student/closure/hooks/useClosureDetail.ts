import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import {
  getProjectDetail,
  getProjectAchievements,
  getProjectCertificate,
} from "@/api/projects";
import { DICT_CODES } from "@/api/dictionaries";
import { useDictionary } from "@/composables/useDictionary";

type ProjectDetail = {
  id: number;
  title?: string;
  project_no?: string;
  leader_name?: string;
  leader_info?: { real_name?: string };
  leader_student_id?: string;
  leader_contact?: string;
  leader_email?: string;
  level_display?: string;
  level?: string;
  category_display?: string;
  category?: string;
  source_display?: string;
  college?: string;
  budget?: number;
  status?: string;
  status_display?: string;
  final_report_url?: string;
  final_report_name?: string;
  achievement_file_url?: string;
  achievement_file_name?: string;
  closure_applied_at?: string;
  advisors_info?: Array<{
    name?: string;
    job_number?: string;
    title?: string;
    contact?: string;
    email?: string;
  }>;
  members_info?: Array<{
    student_id?: string;
    user_name?: string;
    name?: string;
    role?: string;
  }>;
};

type AchievementItem = {
  id?: number;
  achievement_type?: string;
  achievement_type_display?: string;
  achievement_type_value?: string;
  title?: string;
  description?: string;
  authors?: string;
  journal?: string;
  publication_date?: string;
  doi?: string;
  patent_no?: string;
  patent_type?: string;
  applicant?: string;
  competition_name?: string;
  award_level?: string;
  award_date?: string;
  company_name?: string;
  company_role?: string;
  company_date?: string;
  conference_name?: string;
  conference_level?: string;
  conference_date?: string;
  report_title?: string;
  report_type?: string;
  media_title?: string;
  media_format?: string;
  media_link?: string;
  extra_data?: Record<string, string>;
  attachment_url?: string;
  attachment_name?: string;
};

type ApiResponse<T> = {
  code?: number;
  status?: number;
  data?: T;
  message?: string;
};

const getErrorMessage = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    return error.message || fallback;
  }
  if (typeof error === "string") {
    return error || fallback;
  }
  return fallback;
};

export function useClosureDetail() {
  const route = useRoute();
  const router = useRouter();
  const loading = ref(false);
  const { loadDictionaries, getLabel } = useDictionary();

  const projectId = route.query.projectId as string;

  const projectInfo = reactive<ProjectDetail>({
    id: 0,
    title: "",
    project_no: "",
    leader_name: "",
    leader_student_id: "",
    leader_contact: "",
    leader_email: "",
    level_display: "",
    category_display: "",
    source_display: "",
    college: "",
    budget: 0,
    status: "",
    status_display: "",
    final_report_url: "",
    final_report_name: "",
    achievement_file_url: "",
    achievement_file_name: "",
    closure_applied_at: "",
    advisors_info: [],
    members_info: [],
  });

  const achievements = ref<AchievementItem[]>([]);

  // 加载项目详情
  const loadProjectDetail = async () => {
    if (!projectId) {
      ElMessage.error("项目ID不存在");
      router.back();
      return;
    }

    loading.value = true;
    try {
      const res = (await getProjectDetail(
        Number(projectId)
      )) as ApiResponse<ProjectDetail>;
      const data = res.data || (res as ProjectDetail);

      if (data && (data.id || res.code === 200)) {
        const projectData = data.id ? data : (data as ProjectDetail);

        Object.assign(projectInfo, {
          id: projectData.id,
          title: projectData.title || "",
          project_no: projectData.project_no || "",
          leader_name:
            projectData.leader_name || projectData.leader_info?.real_name || "",
          leader_student_id: projectData.leader_student_id || "",
          leader_contact: projectData.leader_contact || "",
          leader_email: projectData.leader_email || "",
          level_display: projectData.level_display || "",
          category_display: projectData.category_display || "",
          source_display: projectData.source_display || "",
          college: projectData.college || "",
          budget: projectData.budget ?? 0,
          status: projectData.status || "",
          status_display: projectData.status_display || "",
          final_report_url: projectData.final_report_url || "",
          final_report_name: projectData.final_report_name || "",
          achievement_file_url: projectData.achievement_file_url || "",
          achievement_file_name: projectData.achievement_file_name || "",
          closure_applied_at: projectData.closure_applied_at || "",
          advisors_info: projectData.advisors_info || [],
          members_info: projectData.members_info || [],
        });

        // 加载成果列表
        await loadAchievements();
      } else {
        throw new Error("项目详情加载失败");
      }
    } catch (error) {
      console.error("加载项目详情失败:", error);
      ElMessage.error(getErrorMessage(error, "加载项目详情失败"));
      router.back();
    } finally {
      loading.value = false;
    }
  };

  // 加载项目成果
  const loadAchievements = async () => {
    try {
      const achRes = (await getProjectAchievements(
        Number(projectId)
      )) as ApiResponse<AchievementItem[]>;

      if (achRes.code === 200 && achRes.data) {
        achievements.value = achRes.data;
      } else if (Array.isArray(achRes)) {
        achievements.value = achRes as AchievementItem[];
      } else {
        achievements.value = [];
      }
    } catch (error) {
      console.error("加载项目成果失败:", error);
      achievements.value = [];
    }
  };

  // 下载文件
  const handleDownload = (url?: string, filename?: string) => {
    if (!url) {
      ElMessage.warning("文件不存在");
      return;
    }
    const link = document.createElement("a");
    link.href = url;
    link.download = filename || "文件";
    link.target = "_blank";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 下载结题证书
  const handleDownloadCertificate = async () => {
    try {
      const res = await getProjectCertificate(Number(projectId));
      const blob =
        res instanceof Blob
          ? res
          : new Blob(
              [typeof res === "string" ? res : JSON.stringify(res ?? "")],
              {
                type: "text/html",
              }
            );
      const url = window.URL.createObjectURL(blob);
      window.open(url, "_blank");
      window.setTimeout(() => URL.revokeObjectURL(url), 10000);
    } catch (error: unknown) {
      console.error("获取结题证书失败:", error);
      ElMessage.error(getErrorMessage(error, "获取结题证书失败"));
    }
  };

  // 返回上一页
  const handleBack = () => {
    router.back();
  };

  onMounted(async () => {
    await loadDictionaries([DICT_CODES.ACHIEVEMENT_TYPE]);
    await loadProjectDetail();
  });

  return {
    loading,
    projectInfo,
    achievements,
    DICT_CODES,
    getLabel,
    handleDownload,
    handleDownloadCertificate,
    handleBack,
  };
}
