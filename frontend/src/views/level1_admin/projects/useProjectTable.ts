import { ref } from "vue";
import { ElMessage } from "element-plus";
import { getAllProjects } from "@/api/admin";

export function useProjectTable(filters: {
  search: string;
  level: string;
  category: string;
  status: string;
}) {
  const loading = ref(false);
  const projects = ref<any[]>([]);
  const selectedRows = ref<any[]>([]);
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
      };

      const res: any = await getAllProjects(params);
      if (res.results) {
        projects.value = res.results;
        total.value = res.count;
      } else if (res.data && res.data.results) {
        projects.value = res.data.results;
        total.value = res.data.count;
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

  const handleSelectionChange = (val: any[]) => {
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
