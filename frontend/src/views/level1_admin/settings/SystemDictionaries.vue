<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">系统字典管理</h1>
        <p class="mt-1 text-sm text-gray-500">
          管理系统基础配置数据，如项目级别、类别、学院等。
        </p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-4">
      <!-- Dictionary Types List -->
      <div class="lg:col-span-1">
        <div class="overflow-hidden bg-white shadow sm:rounded-lg">
          <div class="px-4 py-5 border-b border-gray-200 sm:px-6">
            <h3 class="text-lg font-medium leading-6 text-gray-900">字典类型</h3>
          </div>
          <ul role="list" class="divide-y divide-gray-200">
            <li
              v-for="type in dictionaryTypes"
              :key="type.code"
              @click="currentType = type"
              class="relative px-4 py-4 cursor-pointer hover:bg-gray-50"
              :class="{ 'bg-blue-50': currentType?.code === type.code }"
            >
              <div class="flex justify-between space-x-3">
                <div class="flex-1 min-w-0">
                  <span class="absolute inset-0" aria-hidden="true" />
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ type.name }}
                  </p>
                  <p class="text-sm text-gray-500 truncate">{{ type.code }}</p>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- Dictionary Items Management -->
      <div class="lg:col-span-3">
        <div class="bg-white shadow sm:rounded-lg">
          <div v-if="currentType" class="px-4 py-5 sm:p-6">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-lg font-medium leading-6 text-gray-900">
                  {{ currentType.name }}
                </h3>
                <p class="mt-1 text-sm text-gray-500">
                  {{ currentType.description }}
                </p>
              </div>
              <button
                type="button"
                @click="openAddDialog"
                class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <PlusIcon class="w-5 h-5 mr-2 -ml-1" aria-hidden="true" />
                添加条目
              </button>
            </div>

            <!-- Items Table -->
            <div class="flex flex-col">
              <div class="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                  <div
                    class="overflow-hidden border-b border-gray-200 shadow sm:rounded-lg"
                  >
                    <table class="min-w-full divide-y divide-gray-200">
                      <thead class="bg-gray-50">
                        <tr>
                          <th
                            scope="col"
                            class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase"
                          >
                            显示名称
                          </th>
                          <th
                            scope="col"
                            class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase"
                          >
                            值
                          </th>
                          <th
                            scope="col"
                            class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase"
                          >
                            排序
                          </th>
                          <th
                            scope="col"
                            class="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-500 uppercase"
                          >
                            状态
                          </th>
                          <th scope="col" class="relative px-6 py-3">
                            <span class="sr-only">操作</span>
                          </th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-if="loading" class="animate-pulse">
                          <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500">
                            加载中...
                          </td>
                        </tr>
                        <tr v-else-if="items.length === 0">
                          <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500">
                            暂无数据
                          </td>
                        </tr>
                        <tr v-for="item in items" :key="item.id">
                          <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm font-medium text-gray-900">
                              {{ item.label }}
                            </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-500">
                              {{ item.value }}
                            </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <div class="text-sm text-gray-500">
                              {{ item.sort_order }}
                            </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <span
                              class="inline-flex px-2 text-xs font-semibold leading-5 text-green-800 bg-green-100 rounded-full"
                              :class="{
                                'bg-green-100 text-green-800': item.is_active,
                                'bg-red-100 text-red-800': !item.is_active,
                              }"
                            >
                              {{ item.is_active ? '启用' : '禁用' }}
                            </span>
                          </td>
                          <td
                            class="px-6 py-4 text-sm font-medium text-right whitespace-nowrap"
                          >
                            <button
                              @click="deleteItem(item)"
                              class="text-red-600 hover:text-red-900"
                            >
                              删除
                            </button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="flex items-center justify-center h-64 text-gray-500">
            请选择左侧的字典类型进行管理
          </div>
        </div>
      </div>
    </div>

    <!-- Add Item Modal -->
    <TransitionRoot as="template" :show="shouldOpenDialog">
      <Dialog as="div" class="fixed inset-0 z-10 overflow-y-auto" @close="shouldOpenDialog = false">
        <div
          class="flex items-end justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0"
        >
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0"
            enter-to="opacity-100"
            leave="ease-in duration-200"
            leave-from="opacity-100"
            leave-to="opacity-0"
          >
            <DialogOverlay
              class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
            />
          </TransitionChild>

          <span
            class="hidden sm:inline-block sm:align-middle sm:h-screen"
            aria-hidden="true"
            >&#8203;</span
          >
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <div
              class="relative inline-block px-4 pt-5 pb-4 overflow-hidden text-left align-bottom transition-all transform bg-white rounded-lg shadow-xl sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6"
            >
              <div>
                <div
                  class="flex items-center justify-center w-12 h-12 mx-auto bg-indigo-100 rounded-full"
                >
                  <PlusIcon class="w-6 h-6 text-indigo-600" aria-hidden="true" />
                </div>
                <div class="mt-3 text-center sm:mt-5">
                  <DialogTitle
                    as="h3"
                    class="text-lg font-medium leading-6 text-gray-900"
                  >
                    添加{{ currentType?.name }}
                  </DialogTitle>
                  <div class="mt-2">
                    <form @submit.prevent="submitForm" class="space-y-4">
                      <div>
                        <label
                          for="label"
                          class="block text-sm font-medium text-left text-gray-700"
                          >显示名称</label
                        >
                        <div class="mt-1">
                          <input
                            type="text"
                            name="label"
                            id="label"
                            v-model="form.label"
                            required
                            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            placeholder="例如：计算机学院"
                          />
                        </div>
                      </div>
                      <div>
                        <label
                          for="value"
                          class="block text-sm font-medium text-left text-gray-700"
                          >值 (唯一标识)</label
                        >
                        <div class="mt-1">
                          <input
                            type="text"
                            name="value"
                            id="value"
                            v-model="form.value"
                            required
                            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                            placeholder="例如：CS"
                          />
                        </div>
                      </div>
                      <div>
                        <label
                          for="sort_order"
                          class="block text-sm font-medium text-left text-gray-700"
                          >排序</label
                        >
                        <div class="mt-1">
                          <input
                            type="number"
                            name="sort_order"
                            id="sort_order"
                            v-model="form.sort_order"
                            class="block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                          />
                        </div>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
              <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                <button
                  type="button"
                  class="inline-flex justify-center w-full px-4 py-2 text-base font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:col-start-2 sm:text-sm"
                  @click="submitForm"
                >
                  确定
                </button>
                <button
                  type="button"
                  class="inline-flex justify-center w-full px-4 py-2 mt-3 text-base font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-1 sm:text-sm"
                  @click="shouldOpenDialog = false"
                >
                  取消
                </button>
              </div>
            </div>
          </TransitionChild>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import {
  Dialog,
  DialogOverlay,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'
import { PlusIcon } from '@heroicons/vue/24/outline'
import request from '@/utils/request'

interface DictionaryType {
  id: number
  code: string
  name: string
  description: string
}

interface DictionaryItem {
  id: number
  dict_type: number
  label: string
  value: string
  sort_order: number
  is_active: boolean
}

const dictionaryTypes = ref<DictionaryType[]>([])
const currentType = ref<DictionaryType | null>(null)
const items = ref<DictionaryItem[]>([])
const loading = ref(false)
const shouldOpenDialog = ref(false)

const form = ref({
  label: '',
  value: '',
  sort_order: 0,
})

// 初始化
onMounted(async () => {
  await fetchTypes()
})

// 监听当前类型变化，加载对应的条目
watch(currentType, async (newType) => {
  if (newType) {
    await fetchItems(newType.code)
  } else {
    items.value = []
  }
})

const fetchTypes = async () => {
  try {
    const response = await request.get('/dictionaries/types/')
    dictionaryTypes.value = response.data
    // 默认选中第一个
    if (dictionaryTypes.value.length > 0) {
      currentType.value = dictionaryTypes.value[0]
    }
  } catch (error) {
    console.error('Failed to fetch dictionary types:', error)
  }
}

const fetchItems = async (typeCode: string) => {
  loading.value = true
  try {
    const response = await request.get('/dictionaries/items/', {
      params: { dict_type_code: typeCode },
    })
    items.value = response.data
  } catch (error) {
    console.error('Failed to fetch items:', error)
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  form.value = {
    label: '',
    value: '',
    sort_order: 0,
  }
  shouldOpenDialog.value = true
}

const submitForm = async () => {
  if (!currentType.value) return

  try {
    await request.post('/dictionaries/items/', {
      dict_type: currentType.value.id,
      ...form.value,
      is_active: true,
    })
    shouldOpenDialog.value = false
    await fetchItems(currentType.value.code)
  } catch (error) {
    console.error('Failed to create item:', error)
    // 这里可以添加错误提示
  }
}

const deleteItem = async (item: DictionaryItem) => {
  if (!confirm(`确认要删除 "${item.label}" 吗？`)) return

  try {
    await request.delete(`/dictionaries/items/${item.id}/`)
    if (currentType.value) {
      await fetchItems(currentType.value.code)
    }
  } catch (error) {
    console.error('Failed to delete item:', error)
    alert('删除失败，可能该条目正在被使用。')
  }
}
</script>
