import { ref } from "vue";
import { ElMessage } from "element-plus";
import { getAllProjects } from "@/api/projects/admin";

type ProjectRow = {
  id: number;
  title?: string;
  project_no?: string;
  status?: string;
  status_display?: string;
  leader?: number | string;
};

type ProjectListResponse = {
  results?: ProjectRow[];
  count?: number;
  data?: {
    results?: ProjectRow[];
    count?: number;
  };
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

export function useProjectTable(filters: {
  search: string;
  level: string;
  category: string;
  status: string;
  include_archived?: boolean;
}) {
  const loading = ref(false);
  const projects = ref<ProjectRow[]>([]);
  const selectedRows = ref<ProjectRow[]>([]);
  const currentPage = ref(1);
  const pageSize = ref(10);
  const total = ref(0);

  const fetchProjects = async () => {
    loading.value = true;
    try {
      const params = {
        page: currentPage.value,
        page_size: pageSize.value,
        search: filters.search,
        level: filters.level,
        category: filters.category,
        status: filters.status,
        include_archived: filters.include_archived ? 1 : 0,
      };

      const res = (await getAllProjects(params)) as
        | ProjectListResponse
        | ProjectRow[];
      if (isRecord(res) && Array.isArray(res.results)) {
        projects.value = res.results ?? [];
        total.value = res.count ?? projects.value.length;
      } else if (
        isRecord(res) &&
        isRecord(res.data) &&
        Array.isArray(res.data?.results)
      ) {
        projects.value = res.data?.results ?? [];
        total.value = res.data?.count ?? projects.value.length;
      } else {
        projects.value = Array.isArray(res) ? res : [];
        total.value = projects.value.length;
      }
    } catch {
      ElMessage.error("获取项目列表失败");
    } finally {
      loading.value = false;
    }
  };

  const handlePageChange = () => fetchProjects();
  const handleSizeChange = () => {
    currentPage.value = 1;
    fetchProjects();
  };

  const handleSelectionChange = (val: ProjectRow[]) => {
    selectedRows.value = val;
  };

  return {
    loading,
    projects,
    selectedRows,
    currentPage,
    pageSize,
    total,
    fetchProjects,
    handlePageChange,
    handleSizeChange,
    handleSelectionChange,
  };
}
