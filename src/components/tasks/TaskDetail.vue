<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { Icon } from '@iconify/vue';
import type { Task, TaskItem, TaskLog } from '../../types/task';
import { TaskStatus, TASK_TYPE_LABELS } from '../../types/task';
import { taskApi } from '../../api';
import TaskStatusBadge from './TaskStatusBadge.vue';
import TaskProgressBar from './TaskProgressBar.vue';

interface Props {
  taskId: string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  back: [];
  close: [];
  retry: [task: Task];
  cancel: [task: Task];
}>(); 

const task = ref<Task | null>(null);
const items = ref<TaskItem[]>([]);
const logs = ref<TaskLog[]>([]);
const loading = ref(false);
const activeTab = ref<'items' | 'logs'>('items');

const canCancel = computed(() => {
  if (!task.value) return false;
  const cancelableStatuses: TaskStatus[] = [
    TaskStatus.PENDING,
    TaskStatus.PROCESSING,
    TaskStatus.RETRYING,
  ];
  return cancelableStatuses.includes(task.value.status);
});

const canRetry = computed(() => {
  return task.value?.status === TaskStatus.FAILED;
});

const stats = computed(() => {
  if (!task.value) return { total: 0, success: 0, failed: 0, processing: 0, pending: 0 };
  return {
    total: task.value.totalItems,
    success: task.value.completedItems,
    failed: task.value.failedItems,
    processing: items.value.filter((i) => i.status === TaskStatus.PROCESSING).length,
    pending: items.value.filter(
      (i) => i.status === TaskStatus.PENDING || i.status === TaskStatus.RETRYING
    ).length,
  };
});

const formattedDate = computed(() => {
  if (!task.value) return '';
  const date = new Date(task.value.createdAt);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
});

async function loadTaskDetail() {
  loading.value = true;
  try {
    const response = await taskApi.get(props.taskId);
    if (response.success) {
      task.value = response.data;
      items.value = response.data.items || [];

      await loadTaskLogs();
    }
  } catch (err) {
    console.error('Load task detail error:', err);
  } finally {
    loading.value = false;
  }
}

async function loadTaskLogs() {
  try {
    const response = await taskApi.listLogs(props.taskId, { limit: 50 });
    if (response.success) {
      logs.value = response.data.items;
    }
  } catch (err) {
    console.error('Load task logs error:', err);
  }
}

async function handleRetry() {
  if (!task.value) return;
  try {
    const response = await taskApi.retry(props.taskId);
    if (response.success) {
      task.value = response.data;
      emit('retry', response.data);
    }
  } catch (err) {
    console.error('Retry task error:', err);
  }
}

async function handleCancel() {
  if (!task.value) return;
  try {
    const response = await taskApi.cancel(props.taskId);
    if (response.success) {
      task.value = response.data;
      emit('cancel', response.data);
    }
  } catch (err) {
    console.error('Cancel task error:', err);
  }
}

function getItemIcon(item: TaskItem) {
  switch (item.status) {
    case TaskStatus.COMPLETED:
      return 'solar:check-circle-bold';
    case TaskStatus.FAILED:
      return 'solar:close-circle-bold';
    case TaskStatus.PROCESSING:
      return 'solar:loader-bold';
    case TaskStatus.RETRYING:
      return 'solar:refresh-bold';
    case TaskStatus.CANCELLED:
      return 'solar:minus-circle-bold';
    default:
      return 'solar:circle-outline';
  }
}

function getItemIconColor(item: TaskItem) {
  switch (item.status) {
    case TaskStatus.COMPLETED:
      return 'text-emerald-500';
    case TaskStatus.FAILED:
      return 'text-red-500';
    case TaskStatus.PROCESSING:
      return 'text-blue-500';
    case TaskStatus.RETRYING:
      return 'text-amber-500';
    case TaskStatus.CANCELLED:
      return 'text-gray-400';
    default:
      return 'text-gray-300';
  }
}

function formatLogTime(timestamp: string) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function getLogLevelColor(level: string) {
  switch (level) {
    case 'error':
      return 'text-red-500 bg-red-50';
    case 'warn':
      return 'text-amber-500 bg-amber-50';
    case 'info':
      return 'text-blue-500 bg-blue-50';
    default:
      return 'text-gray-500 bg-gray-50';
  }
}

watch(
  () => props.taskId,
  () => {
    if (props.taskId) {
      loadTaskDetail();
    }
  }
);

onMounted(() => {
  if (props.taskId) {
    loadTaskDetail();
  }
});
</script>

<template>
  <div class="task-detail h-full flex flex-col bg-white rounded-t-3xl">
    <div class="flex items-center justify-between p-4 border-b border-stone-100 flex-shrink-0">
      <button
        class="w-9 h-9 rounded-full bg-gray-50 flex items-center justify-center text-gray-600 hover:bg-gray-100 transition-colors"
        @click="emit('back')"
      >
        <Icon icon="solar:arrow-left-linear" class="text-lg" />
      </button>
      <h3 class="text-base font-bold text-gray-800">任务详情</h3>
      <button
        class="w-9 h-9 rounded-full bg-gray-50 flex items-center justify-center text-gray-600 hover:bg-gray-100 transition-colors"
        @click="emit('close')"
      >
        <Icon icon="solar:close-linear" class="text-lg" />
      </button>
    </div>

    <div class="flex-1 overflow-y-auto">
      <div v-if="loading && !task" class="py-16 text-center">
        <div class="w-10 h-10 border-2 border-[#8B6F4E]/20 border-t-[#8B6F4E] rounded-full animate-spin mx-auto mb-3"></div>
        <p class="text-sm text-gray-500">加载中...</p>
      </div>

      <div v-else-if="task" class="p-4">
        <div class="mb-4">
          <div class="flex items-start justify-between gap-3 mb-2">
            <h2 class="text-lg font-bold text-gray-800">{{ task.title }}</h2>
            <TaskStatusBadge :status="task.status" />
          </div>
          <p class="text-xs text-gray-400 mb-3">
            {{ TASK_TYPE_LABELS[task.type] }} · {{ formattedDate }}
          </p>
          <p v-if="task.description" class="text-sm text-gray-600 mb-4">
            {{ task.description }}
          </p>

          <TaskProgressBar
            :progress="task.progress"
            :status="task.status"
            :completed-items="task.completedItems"
            :total-items="task.totalItems"
          />
        </div>

        <div class="grid grid-cols-4 gap-2 mb-4">
          <div class="bg-gray-50 rounded-xl p-3 text-center">
            <p class="text-lg font-bold text-gray-800">{{ stats.total }}</p>
            <p class="text-[10px] text-gray-500">总数</p>
          </div>
          <div class="bg-emerald-50 rounded-xl p-3 text-center">
            <p class="text-lg font-bold text-emerald-600">{{ stats.success }}</p>
            <p class="text-[10px] text-emerald-500">成功</p>
          </div>
          <div class="bg-red-50 rounded-xl p-3 text-center">
            <p class="text-lg font-bold text-red-500">{{ stats.failed }}</p>
            <p class="text-[10px] text-red-500">失败</p>
          </div>
          <div class="bg-blue-50 rounded-xl p-3 text-center">
            <p class="text-lg font-bold text-blue-500">{{ stats.pending }}</p>
            <p class="text-[10px] text-blue-500">等待中</p>
          </div>
        </div>

        <div class="flex items-center gap-2 mb-4">
          <button
            v-if="canRetry"
            class="flex-1 py-2.5 bg-amber-500 text-white text-sm font-medium rounded-xl hover:bg-amber-600 transition-colors flex items-center justify-center gap-2"
            @click="handleRetry"
          >
            <Icon icon="solar:refresh-bold" class="text-base" />
            重试失败项
          </button>
          <button
            v-if="canCancel"
            class="flex-1 py-2.5 bg-gray-100 text-gray-600 text-sm font-medium rounded-xl hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
            @click="handleCancel"
          >
            <Icon icon="solar:close-circle-bold" class="text-base" />
            取消任务
          </button>
          <button
            class="w-10 h-10 bg-[#8B6F4E]/10 rounded-xl flex items-center justify-center text-[#8B6F4E] hover:bg-[#8B6F4E]/20 transition-colors"
            @click="loadTaskDetail"
          >
            <Icon icon="solar:refresh-linear" class="text-lg" />
          </button>
        </div>

        <div class="flex items-center gap-1 bg-gray-50 rounded-xl p-1 mb-4">
          <button
            class="flex-1 py-2 text-xs font-medium rounded-lg transition-all"
            :class="{
              'bg-white shadow-sm text-[#8B6F4E]': activeTab === 'items',
              'text-gray-500': activeTab !== 'items',
            }"
            @click="activeTab = 'items'"
          >
            子任务 ({{ items.length }})
          </button>
          <button
            class="flex-1 py-2 text-xs font-medium rounded-lg transition-all"
            :class="{
              'bg-white shadow-sm text-[#8B6F4E]': activeTab === 'logs',
              'text-gray-500': activeTab !== 'logs',
            }"
            @click="activeTab = 'logs'"
          >
            运行日志 ({{ logs.length }})
          </button>
        </div>

        <div v-if="activeTab === 'items'" class="space-y-2">
          <div
            v-for="item in items"
            :key="item.id"
            class="bg-gray-50 rounded-xl p-3 hover:bg-gray-100/50 transition-colors"
          >
            <div class="flex items-start gap-3">
              <div class="pt-0.5">
                <Icon
                  :icon="getItemIcon(item)"
                  :class="[
                    getItemIconColor(item),
                    'text-lg',
                    { 'animate-spin': item.status === 'processing' }
                  ]"
                />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-2">
                  <span class="text-sm font-medium text-gray-800 truncate">
                    {{ item.title || `任务 ${item.index + 1}` }}
                  </span>
                  <span class="text-[10px] text-gray-400 flex-shrink-0">
                    #{{ item.index + 1 }}
                  </span>
                </div>

                <div v-if="item.error" class="mt-1">
                  <p class="text-xs text-red-500 line-clamp-1">
                    {{ item.error.code }}: {{ item.error.message }}
                  </p>
                </div>

                <div class="flex items-center gap-3 mt-2 text-[10px] text-gray-400">
                  <span v-if="item.retryCount > 0" class="text-amber-500">
                    已重试 {{ item.retryCount }} 次
                  </span>
                  <span v-if="item.status === 'retrying' && item.nextRetryAt">
                    下次重试: {{ new Date(item.nextRetryAt).toLocaleTimeString('zh-CN') }}
                  </span>
                  <span v-if="item.completedAt">
                    耗时: {{ Math.round((new Date(item.completedAt).getTime() - new Date(item.startedAt || item.createdAt).getTime()) / 1000) }}s
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else-if="activeTab === 'logs'" class="space-y-2">
          <div
            v-for="log in logs"
            :key="log.id"
            class="bg-gray-50 rounded-xl p-3"
          >
            <div class="flex items-start gap-3">
              <span
                class="px-2 py-0.5 rounded-md text-[10px] font-medium flex-shrink-0"
                :class="getLogLevelColor(log.level)"
              >
                {{ log.level.toUpperCase() }}
              </span>
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-2">
                  <span class="text-xs font-medium text-gray-700">{{ log.action }}</span>
                  <span class="text-[10px] text-gray-400 flex-shrink-0">
                    {{ formatLogTime(log.timestamp) }}
                  </span>
                </div>
                <p class="text-xs text-gray-500 mt-1">{{ log.message }}</p>
                <div
                  v-if="log.details && Object.keys(log.details).length > 0"
                  class="mt-2 p-2 bg-white/50 rounded-lg text-[10px] text-gray-400 font-mono"
                >
                  {{ JSON.stringify(log.details, null, 2) }}
                </div>
              </div>
            </div>
          </div>

          <div v-if="logs.length === 0" class="py-8 text-center">
            <Icon icon="solar:file-text-linear" class="text-3xl text-gray-300 mx-auto mb-2" />
            <p class="text-xs text-gray-400">暂无日志</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
