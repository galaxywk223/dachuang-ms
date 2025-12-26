export function useProjectSearch(
  filters: {
    search: string;
    level: string;
    category: string;
    status: string;
  },
  fetchProjects: () => void,
  currentPage: { value: number }
) {

  const handleSearch = () => {
    currentPage.value = 1;
    fetchProjects();
  };

  const handleReset = () => {
    filters.search = "";
    filters.level = "";
    filters.category = "";
    filters.status = "";
    currentPage.value = 1;
    fetchProjects();
  };

  return {
    handleSearch,
    handleReset,
  };
}
