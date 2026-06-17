<script setup lang="ts">
import { computed } from 'vue';
import { TaskStatus, TASK_STATUS_COLORS } from '../../types/task';

interface Props {
  progress: number;
  status?: TaskStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  completedItems?: number;
  totalItems?: number;
}

const props = withDefaults(defineProps<Props>(), {
  status: TaskStatus.PROCESSING,
  size: 'md',
  showLabel: true,
});

const progressColor = computed(() => {
  switch (props.status) {
    case TaskStatus.COMPLETED:
      return '#10B981';
    case TaskStatus.FAILED:
      return '#EF4444';
    case TaskStatus.CANCELLED:
      return '#6B7280';
    case TaskStatus.RETRYING:
      return '#F59E0B';
    default:
      return TASK_STATUS_COLORS[props.status] || '#3B82F6';
  }
});

const heightClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'h-1';
    case 'lg':
      return 'h-3';
    default:
      return 'h-2';
  }
});

const progressText = computed(() => {
  if (props.completedItems !== undefined && props.totalItems !== undefined) {
    return `${props.completedItems} / ${props.totalItems}`;
  }
  return `${Math.round(props.progress)}%`;
});
</script>

<template>
  <div class="w-full">
    <div class="flex items-center justify-between mb-1.5">
      <slot name="left">
        <span class="text-xs text-gray-500">进度</span>
      </slot>
      <span
        v-if="showLabel"
        class="text-xs font-medium"
        :style="{ color: progressColor }"
      >
        {{ progressText }}
      </span>
    </div>
    <div
      class="w-full bg-gray-100 rounded-full overflow-hidden"
      :class="heightClass"
    >
      <div
        class="h-full rounded-full transition-all duration-500 ease-out relative"
        :style="{
          width: `${Math.min(100, Math.max(0, progress))}%`,
          backgroundColor: progressColor,
        }"
      >
        <div
          v-if="status === 'processing' || status === 'retrying'"
          class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"
        ></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 1.5s ease-in-out infinite;
}
</style>
