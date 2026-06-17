<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { Icon } from '@iconify/vue';
import type { Task } from '../../types/task';
import { TaskStatus, TaskType } from '../../types/task';
import { taskApi } from '../../api';
import TaskCard from './TaskCard.vue';
import useTaskWebSocket from '../../composables/useTaskWebSocket';

interface Props {
  filterStatus?: TaskStatus | 'all';
  filterType?: TaskType | 'all';
  showFilters?: boolean;
  limit?: number;
}

const props = withDefaults(defineProps<Props>(), {
  filterStatus: 'all',
  filterType: 'all',
  showFilters: true,
  limit: 20,
});

const emit = defineEmits<{
  'task-click': [task: Task];
  'task-retry': [task: Task];
  'task-cancel': [task: Task];
  'task-submitted': [task: Task];
}>(); 

const tasks = ref<Task[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
const activeStatusFilter = ref<TaskStatus | 'all'>('all');
const activeTypeFilter = ref<TaskType | 'all'>('all');

const { connectionStatus, tasks: wsTasks } = useTaskWebSocket();

const filteredTasks = computed(() => {
  let result = tasks.value;

  if (activeStatusFilter.value !== 'all') {
    result = result.filter((t) => t.status === activeStatusFilter.value);
  }
  if (activeTypeFilter.value !== 'all') {
    result = result.filter((t) => t.type === activeTypeFilter.value);
  }

  return result;
});

const statusOptions = [
  { value: 'all', label: '全部' },
  { value: TaskStatus.PENDING, label: '排队中' },
  { value: TaskStatus.PROCESSING, label: '处理中' },
  { value: TaskStatus.RETRYING, label: '重试中' },
  { value: TaskStatus.COMPLETED, label: '已完成' },
  { value: TaskStatus.FAILED, label: '失败' },
];

const typeOptions = [
  { value: 'all', label: '全部类型' },
  { value: TaskType.IMAGE_REPAIR, label: '照片修复' },
  { value: TaskType.AI_GENERATION, label: 'AI生成' },
];

async function loadTasks() {
  loading.value = true;
  error.value = null;
  try {
    const response = await taskApi.list({ limit: props.limit });
    if (response.success) {
      tasks.value = response.data.items;

      tasks.value.forEach((task) => {
        wsTasks.value.set(task.id, task);
      });
    } else {
      error.value = response.error?.message || '加载失败';
    }
  } catch (err: any) {
    error.value = err.message || '加载失败';
  } finally {
    loading.value = false;
  }
}

function handleTaskClick(task: Task) {
  emit('task-click', task);
}

async function handleTaskRetry(task: Task) {
  try {
    const response = await taskApi.retry(task.id);
    if (response.success) {
      const index = tasks.value.findIndex((t) => t.id === task.id);
      if (index !== -1) {
        tasks.value[index] = response.data;
      }
      emit('task-retry', response.data);
    }
  } catch (err) {
    console.error('Retry task error:', err);
  }
}

async function handleTaskCancel(task: Task) {
  try {
    const response = await taskApi.cancel(task.id);
    if (response.success) {
      const index = tasks.value.findIndex((t) => t.id === task.id);
      if (index !== -1) {
        tasks.value[index] = response.data;
      }
      emit('task-cancel', response.data);
    }
  } catch (err) {
    console.error('Cancel task error:', err);
  }
}

watch(
  wsTasks,
  () => {
    const wsTaskList = Array.from(wsTasks.value.values());
    if (wsTaskList.length > 0) {
      wsTaskList.forEach((wsTask) => {
        const index = tasks.value.findIndex((t) => t.id === wsTask.id);
        if (index !== -1) {
          tasks.value[index] = wsTask;
        } else {
          tasks.value.unshift(wsTask);
        }
      });
    }
  },
  { deep: true }
);

watch(
  () => props.filterStatus,
  (val) => {
    activeStatusFilter.value = val;
  }
);

watch(
  () => props.filterType,
  (val) => {
    activeTypeFilter.value = val;
  }
);

onMounted(() => {
  loadTasks();
});

defineExpose({
  loadTasks,
  tasks,
});
</script>

<template>
  <div class="task-list">
    <div v-if="showFilters" class="flex items-center gap-3 mb-4 flex-wrap">
      <div class="flex items-center gap-1 bg-gray-50 rounded-xl p-1">
        <button
          v-for="option in statusOptions"
          :key="option.value"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
          :class="{
            'bg-white shadow-sm text-[#8B6F4E]': activeStatusFilter === option.value,
            'text-gray-500 hover:text-gray-700': activeStatusFilter !== option.value,
          }"
          @click="activeStatusFilter = option.value as any"
        >
          {{ option.label }}
        </button>
      </div>

      <div class="flex items-center gap-1 bg-gray-50 rounded-xl p-1">
        <button
          v-for="option in typeOptions"
          :key="option.value"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
          :class="{
            'bg-white shadow-sm text-[#8B6F4E]': activeTypeFilter === option.value,
            'text-gray-500 hover:text-gray-700': activeTypeFilter !== option.value,
          }"
          @click="activeTypeFilter = option.value as any"
        >
          {{ option.label }}
        </button>
      </div>

      <button
        class="w-8 h-8 rounded-lg bg-gray-50 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors ml-auto"
        title="刷新"
        @click="loadTasks"
      >
        <Icon icon="solar:refresh-linear" class="text-lg" />
      </button>
    </div>

    <div
      class="flex items-center gap-2 mb-3 text-[10px] text-gray-400"
    >
      <span
        class="w-2 h-2 rounded-full"
        :class="{
          'bg-green-500': connectionStatus === 'connected',
          'bg-yellow-500 animate-pulse': connectionStatus === 'connecting',
          'bg-blue-500': connectionStatus === 'polling',
          'bg-gray-400': connectionStatus === 'disconnected',
        }"
      ></span>
      <span>
        {{
          connectionStatus === 'connected'
            ? '实时连接'
            : connectionStatus === 'connecting'
            ? '连接中...'
            : connectionStatus === 'polling'
            ? '轮询同步'
            : '已断开'
        }}
      </span>
      <span class="ml-auto">{{ filteredTasks.length }} 个任务</span>
    </div>

    <div v-if="loading && tasks.length === 0" class="py-12 text-center">
      <div class="w-10 h-10 border-2 border-[#8B6F4E]/20 border-t-[#8B6F4E] rounded-full animate-spin mx-auto mb-3"></div>
      <p class="text-sm text-gray-500">加载中...</p>
    </div>

    <div v-else-if="error && tasks.length === 0" class="py-12 text-center">
      <Icon icon="solar:alert-circle-linear" class="text-4xl text-gray-300 mx-auto mb-3" />
      <p class="text-sm text-gray-500">{{ error }}</p>
      <button
        class="mt-3 px-4 py-2 bg-[#8B6F4E] text-white text-sm rounded-xl hover:bg-[#6B5342] transition-colors"
        @click="loadTasks"
      >
        重试
      </button>
    </div>

    <div v-else-if="filteredTasks.length === 0" class="py-12 text-center">
      <Icon icon="solar:inbox-line-duotone" class="text-4xl text-gray-300 mx-auto mb-3" />
      <p class="text-sm text-gray-500">暂无任务</p>
    </div>

    <div v-else class="space-y-3">
      <TaskCard
        v-for="task in filteredTasks"
        :key="task.id"
        :task="task"
        @click="handleTaskClick(task)"
        @retry="handleTaskRetry(task)"
        @cancel="handleTaskCancel(task)"
      />
    </div>
  </div>
</template>
