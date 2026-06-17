<script setup lang="ts">
import { computed } from 'vue';
import { TaskStatus, TASK_STATUS_COLORS, TASK_STATUS_LABELS } from '../../types/task';

interface Props {
  status: TaskStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  showLabel: true,
});

const statusColor = computed(() => TASK_STATUS_COLORS[props.status] || '#9CA3AF');
const statusLabel = computed(() => TASK_STATUS_LABELS[props.status] || props.status);

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'w-2 h-2';
    case 'lg':
      return 'w-3 h-3';
    default:
      return 'w-2.5 h-2.5';
  }
});

const isAnimating = computed(() =>
  props.status === TaskStatus.PROCESSING || props.status === TaskStatus.RETRYING
);
</script>

<template>
  <div class="inline-flex items-center gap-2">
    <span
      class="rounded-full flex-shrink-0 relative"
      :class="sizeClasses"
      :style="{ backgroundColor: statusColor }"
    >
      <span
        v-if="isAnimating"
        class="absolute inset-0 rounded-full animate-ping opacity-75"
        :style="{ backgroundColor: statusColor }"
      ></span>
    </span>
    <span
      v-if="showLabel"
      class="text-xs font-medium"
      :style="{ color: statusColor }"
    >
      {{ statusLabel }}
    </span>
  </div>
</template>
