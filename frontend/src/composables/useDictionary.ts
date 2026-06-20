import { ref, readonly } from "vue";
import {
    getAllDictionaries,
    getDictionariesBatch,
    getDictionaryByCode,
    type DictionaryItem,
    type DictionaryBatchResponse,
} from "@/api/dictionaries";

/**
 * 字典缓存
 */
const dictionaryCache = ref<DictionaryBatchResponse>({});
const isLoaded = ref(false);
const isLoading = ref(false);

/**
 * 字典数据 composable
 * 提供字典数据的获取、缓存和查询功能
 */
export function useDictionary() {
    /**
     * 初始化所有字典数据
     * 应在应用启动时调用一次
     */
    const initDictionaries = async () => {
        if (isLoaded.value || isLoading.value) return;

        isLoading.value = true;
        try {
            const data = await getAllDictionaries();
            dictionaryCache.value = data;
            isLoaded.value = true;
        } catch (error) {
            console.error("Failed to load dictionaries:", error);
        } finally {
            isLoading.value = false;
        }
    };

    /**
     * 获取指定字典类型的选项列表
     * @param code 字典类型编码
     * @returns 选项列表
     */
    const getOptions = (code: string): DictionaryItem[] => {
        return dictionaryCache.value[code]?.items || [];
    };

    /**
     * 根据字典值获取显示标签
     * @param code 字典类型编码
     * @param value 选项值
     * @returns 显示标签
     */
    const getLabel = (code: string, value: string): string => {
        const items = getOptions(code);
        const item = items.find((i) => i.value === value);
        return item?.label || value;
    };

    /**
     * 批量加载指定的字典类型
     * @param codes 字典类型编码列表
     */
    const loadDictionaries = async (codes: Array<string | null | undefined>) => {
        const cleanedCodes = Array.from(new Set(codes))
            .filter((code): code is string => typeof code === "string")
            .map((code) => code.trim())
            .filter(Boolean);

        if (cleanedCodes.length === 0) return;

        // 过滤出尚未缓存的编码
        const missingCodes = cleanedCodes.filter(
            (code) => !dictionaryCache.value[code]
        );

        if (missingCodes.length === 0) return;

        try {
            const data = await getDictionariesBatch(missingCodes);
            dictionaryCache.value = { ...dictionaryCache.value, ...data };
        } catch (error) {
            console.error("Failed to load dictionaries:", error);
        }
    };

    /**
     * 加载单个字典类型
     * @param code 字典类型编码
     */
    const loadDictionary = async (code: string) => {
        if (dictionaryCache.value[code]) return;

        try {
            const data = await getDictionaryByCode(code);
            dictionaryCache.value[code] = {
                name: data.name,
                items: data.items,
            };
        } catch (error) {
            console.error(`Failed to load dictionary ${code}:`, error);
        }
    };

    /**
     * 强制刷新单个字典类型
     * @param code 字典类型编码
     */
    const refreshDictionary = async (code: string) => {
        try {
            const data = await getDictionaryByCode(code);
            dictionaryCache.value[code] = {
                name: data.name,
                items: data.items,
            };
        } catch (error) {
            console.error(`Failed to refresh dictionary ${code}:`, error);
        }
    };

    /**
     * 刷新所有字典缓存
     */
    const refreshDictionaries = async () => {
        isLoaded.value = false;
        dictionaryCache.value = {};
        await initDictionaries();
    };

    return {
        // 状态
        isLoaded: readonly(isLoaded),
        isLoading: readonly(isLoading),

        // 方法
        initDictionaries,
        loadDictionaries,
        loadDictionary,
        refreshDictionary,
        refreshDictionaries,
        getOptions,
        getLabel,
    };
}

/**
 * 导出单例，方便在非组件中使用
 */
export const dictionaryService = {
    getOptions: (code: string) => dictionaryCache.value[code]?.items || [],
    getLabel: (code: string, value: string) => {
        const items = dictionaryCache.value[code]?.items || [];
        return items.find((i) => i.value === value)?.label || value;
    },
};
