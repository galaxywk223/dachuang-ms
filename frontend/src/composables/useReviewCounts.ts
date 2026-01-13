import { ref, onMounted, onUnmounted } from "vue";
import { getPendingCounts } from "@/api/reviews/statistics";

export interface ReviewCounts {
  establishment: number;
  midterm: number;
  closure: number;
  change: number;
}

/**
 * 使用待审核数量
 * @param autoRefresh 是否自动刷新（默认30秒）
 * @param interval 刷新间隔（毫秒）
 */
export function useReviewCounts(autoRefresh = true, interval = 30000) {
  const counts = ref<ReviewCounts>({
    establishment: 0,
    midterm: 0,
    closure: 0,
    change: 0,
  });

  const loading = ref(false);
  const error = ref<string | null>(null);
  let timer: ReturnType<typeof setInterval> | null = null;

  /**
   * 加载待审核数量
   */
  const loadCounts = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getPendingCounts();
      if (response.code === 200) {
        counts.value = response.data;
      } else {
        error.value = response.message || "获取待审核数量失败";
      }
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : "网络错误";
    } finally {
      loading.value = false;
    }
  };

  /**
   * 启动自动刷新
   */
  const startAutoRefresh = () => {
    if (timer) return;
    timer = setInterval(loadCounts, interval);
  };

  /**
   * 停止自动刷新
   */
  const stopAutoRefresh = () => {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  };

  onMounted(() => {
    loadCounts();
    if (autoRefresh) {
      startAutoRefresh();
    }
  });

  onUnmounted(() => {
    stopAutoRefresh();
  });

  return {
    counts,
    loading,
    error,
    loadCounts,
    startAutoRefresh,
    stopAutoRefresh,
  };
}
