<script setup lang="ts">
import { computed } from 'vue';
import { Icon } from '@iconify/vue';
import type { Task } from '../../types/task';
import {
  TaskStatus,
  TaskType,
  TASK_TYPE_LABELS,
} from '../../types/task';
import TaskStatusBadge from './TaskStatusBadge.vue';
import TaskProgressBar from './TaskProgressBar.vue';

interface Props {
  task: Task;
  selectable?: boolean;
  selected?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  selectable: false,
  selected: false,
});

const emit = defineEmits<{
  click: [task: Task];
  retry: [task: Task];
  cancel: [task: Task];
}>(); 

const typeIcon = computed(() => {
  switch (props.task.type) {
    case TaskType.IMAGE_REPAIR:
      return 'solar:palette-linear';
    case TaskType.AI_GENERATION:
      return 'solar:magic-stick-3-linear';
    case TaskType.DIGITAL_HUMAN:
      return 'solar:user-circle-linear';
    case TaskType.FINE_TUNE:
      return 'solar:settings-linear';
    default:
      return 'solar:task-linear';
  }
});

const typeColor = computed(() => {
  switch (props.task.type) {
    case TaskType.IMAGE_REPAIR:
      return 'text-orange-600 bg-orange-50';
    case TaskType.AI_GENERATION:
      return 'text-purple-600 bg-purple-50';
    case TaskType.DIGITAL_HUMAN:
      return 'text-blue-600 bg-blue-50';
    case TaskType.FINE_TUNE:
      return 'text-emerald-600 bg-emerald-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
});

const formattedDate = computed(() => {
  const date = new Date(props.task.createdAt);
  return date.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
});

const canCancel = computed(() =>
  props.task.status === TaskStatus.PENDING ||
  props.task.status === TaskStatus.PROCESSING ||
  props.task.status === TaskStatus.RETRYING
);

const canRetry = computed(() => props.task.status === TaskStatus.FAILED);

function handleClick() {
  emit('click', props.task);
}

function handleRetry(e: Event) {
  e.stopPropagation();
  emit('retry', props.task);
}

function handleCancel(e: Event) {
  e.stopPropagation();
  emit('cancel', props.task);
}
</script>

<template>
  <div
    class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100 hover-lift cursor-pointer transition-all"
    :class="{ 'ring-2 ring-[#8B6F4E]': selected }"
    @click="handleClick"
  >
    <div class="flex items-start gap-3">
      <div
        class="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
        :class="typeColor"
      >
        <Icon :icon="typeIcon" class="text-xl" />
      </div>

      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0 flex-1">
            <h4 class="text-sm font-semibold text-gray-800 truncate">
              {{ task.title }}
            </h4>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-[10px] text-gray-400">
                {{ TASK_TYPE_LABELS[task.type] }}
              </span>
              <span class="text-gray-300">·</span>
              <span class="text-[10px] text-gray-400">
                {{ formattedDate }}
              </span>
            </div>
          </div>
          <TaskStatusBadge :status="task.status" size="sm" />
        </div>

        <div class="mt-3">
          <TaskProgressBar
            :progress="task.progress"
            :status="task.status"
            size="sm"
            :completed-items="task.completedItems"
            :total-items="task.totalItems"
          />
        </div>

        <div class="flex items-center justify-between mt-3">
          <div class="flex items-center gap-3 text-[10px] text-gray-400">
            <span class="flex items-center gap-1">
              <Icon icon="solar:gallery-wide-linear" class="text-base" />
              {{ task.totalItems }} 张
            </span>
            <span v-if="task.failedItems > 0" class="text-red-400 flex items-center gap-1">
              <Icon icon="solar:alert-circle-linear" class="text-base" />
              {{ task.failedItems }} 失败
            </span>
          </div>

          <div class="flex items-center gap-1">
            <button
              v-if="canRetry"
              class="w-7 h-7 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600 hover:bg-amber-100 transition-colors"
              title="重试"
              @click="handleRetry"
            >
              <Icon icon="solar:refresh-linear" class="text-sm" />
            </button>
            <button
              v-if="canCancel"
              class="w-7 h-7 rounded-lg bg-gray-50 flex items-center justify-center text-gray-500 hover:bg-gray-100 transition-colors"
              title="取消"
              @click="handleCancel"
            >
              <Icon icon="solar:close-circle-linear" class="text-sm" />
            </button>
            <button
              class="w-7 h-7 rounded-lg bg-[#8B6F4E]/10 flex items-center justify-center text-[#8B6F4E] hover:bg-[#8B6F4E]/20 transition-colors"
              title="查看详情"
            >
              <Icon icon="solar:arrow-right-linear" class="text-sm" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
