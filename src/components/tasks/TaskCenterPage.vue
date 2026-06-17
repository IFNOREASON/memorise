<script setup lang="ts">
import { ref } from 'vue';
import { Icon } from '@iconify/vue';
import type { Task } from '../../types/task';
import { taskApi } from '../../api';
import TaskList from './TaskList.vue';
import TaskDetail from './TaskDetail.vue';
import MessageCenter from './MessageCenter.vue';

const emit = defineEmits<{
  back: [];
  'submit-repair': [];
  'submit-generation': [];
}>(); 

const showMessageCenter = ref(false);
const selectedTaskId = ref<string | null>(null);
const showSubmitType = ref<'none' | 'repair' | 'generation'>('none');
const taskListRef = ref<InstanceType<typeof TaskList> | null>(null);

function handleTaskClick(task: Task) {
  selectedTaskId.value = task.id;
}

function handleTaskDetailBack() {
  selectedTaskId.value = null;
}

function handleTaskDetailClose() {
  selectedTaskId.value = null;
}

function handleTaskRetry(task: Task) {
  console.log('Task retried:', task.id);
}

function handleTaskCancel(task: Task) {
  console.log('Task cancelled:', task.id);
}

function openRepairSubmit() {
  showSubmitType.value = 'repair';
}

function openGenerationSubmit() {
  showSubmitType.value = 'generation';
}

function closeSubmit() {
  showSubmitType.value = 'none';
}

async function handleRepairSubmit() {
  try {
    const response = await taskApi.submitRepair({
      images: [
        { url: 'https://example.com/old-photo-1.jpg', title: '老照片1' },
        { url: 'https://example.com/old-photo-2.jpg', title: '老照片2' },
        { url: 'https://example.com/old-photo-3.jpg', title: '老照片3' },
        { url: 'https://example.com/old-photo-4.jpg', title: '老照片4' },
        { url: 'https://example.com/old-photo-5.jpg', title: '老照片5' },
      ],
      title: '家族老照片批量修复',
      description: '春节期间整理的老照片，需要全部修复并上色',
      repairOptions: {
        mode: 'full',
        enableScratchRemoval: true,
        enableColorize: true,
        enableFaceEnhance: true,
      },
      autoAddToGallery: true,
      autoCreateMemory: true,
    });

    if (response.success) {
      closeSubmit();
      if (taskListRef.value) {
        taskListRef.value.loadTasks();
      }
    }
  } catch (err) {
    console.error('Submit repair error:', err);
  }
}

async function handleGenerationSubmit() {
  try {
    const response = await taskApi.submitGeneration({
      type: 'scene',
      prompt: '1980年代中国家庭春节团圆场景，温馨怀旧风格',
      title: '春节团圆场景生成',
      numImages: 3,
      generationOptions: {
        style: 'vintage',
        width: 1024,
        height: 768,
      },
      autoAddToGallery: true,
    });

    if (response.success) {
      closeSubmit();
      if (taskListRef.value) {
        taskListRef.value.loadTasks();
      }
    }
  } catch (err) {
    console.error('Submit generation error:', err);
  }
}
</script>

<template>
  <div class="task-center h-full flex flex-col bg-[#FAF7F2]">
    <header class="px-4 py-3 flex items-center justify-between sticky top-0 z-40 bg-white/80 backdrop-blur-lg border-b border-stone-100">
      <div class="flex items-center gap-3">
        <button
          class="w-9 h-9 rounded-full bg-gray-50 flex items-center justify-center text-gray-600 hover:bg-gray-100 transition-colors"
          @click="emit('back')"
        >
          <Icon icon="solar:arrow-left-linear" class="text-lg" />
        </button>
        <div>
          <h1 class="text-lg font-bold text-[#5C4A3A] font-serif">任务中心</h1>
          <p class="text-[10px] text-gray-400">管理所有AI处理任务</p>
        </div>
      </div>
      <button
        class="w-9 h-9 rounded-full bg-gray-50 flex items-center justify-center text-gray-600 hover:bg-gray-100 transition-colors relative"
        @click="showMessageCenter = true"
      >
        <Icon icon="solar:bell-bing-linear" class="text-lg" />
        <span
          class="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-red-500 text-white text-[9px] flex items-center justify-center"
        >
          3
        </span>
      </button>
    </header>

    <div class="px-4 py-4 flex gap-3">
      <button
        class="flex-1 bg-gradient-to-br from-orange-100 to-orange-50 rounded-2xl p-4 text-left hover:shadow-md transition-shadow"
        @click="openRepairSubmit"
      >
        <div class="w-10 h-10 bg-orange-500 rounded-xl flex items-center justify-center mb-2">
          <Icon icon="solar:palette-bold" class="text-white text-xl" />
        </div>
        <h3 class="text-sm font-bold text-gray-800">老照片修复</h3>
        <p class="text-[10px] text-gray-500 mt-0.5">批量修复 & 上色</p>
      </button>
      <button
        class="flex-1 bg-gradient-to-br from-purple-100 to-purple-50 rounded-2xl p-4 text-left hover:shadow-md transition-shadow"
        @click="openGenerationSubmit"
      >
        <div class="w-10 h-10 bg-purple-500 rounded-xl flex items-center justify-center mb-2">
          <Icon icon="solar:magic-stick-3-bold" class="text-white text-xl" />
        </div>
        <h3 class="text-sm font-bold text-gray-800">AI场景生成</h3>
        <p class="text-[10px] text-gray-500 mt-0.5">数字人 & 影像</p>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto px-4 pb-4">
      <TaskList
        ref="taskListRef"
        @task-click="handleTaskClick"
        @task-retry="handleTaskRetry"
        @task-cancel="handleTaskCancel"
      />
    </div>

    <div
      v-if="selectedTaskId"
      class="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm flex items-end justify-center"
      @click.self="handleTaskDetailClose"
    >
      <div class="w-full max-w-md h-[85vh] animate-slide-up">
        <TaskDetail
          :task-id="selectedTaskId"
          @back="handleTaskDetailBack"
          @close="handleTaskDetailClose"
          @retry="handleTaskRetry"
          @cancel="handleTaskCancel"
        />
      </div>
    </div>

    <MessageCenter
      :show="showMessageCenter"
      @close="showMessageCenter = false"
      @task-click="(id) => { selectedTaskId = id; showMessageCenter = false; }"
    />

    <div
      v-if="showSubmitType !== 'none'"
      class="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm flex items-end justify-center"
      @click.self="closeSubmit"
    >
      <div class="w-full max-w-md bg-white rounded-t-3xl p-5 animate-slide-up">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-800">
            {{ showSubmitType === 'repair' ? '提交照片修复' : '提交AI生成' }}
          </h3>
          <button
            class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500"
            @click="closeSubmit"
          >
            <Icon icon="solar:close-linear" />
          </button>
        </div>

        <div v-if="showSubmitType === 'repair'" class="space-y-4">
          <div class="bg-gray-50 rounded-2xl p-4">
            <p class="text-sm text-gray-600">
              演示模式：将提交5张模拟老照片进行修复
            </p>
            <ul class="mt-3 space-y-2">
              <li class="flex items-center gap-2 text-xs text-gray-500">
                <Icon icon="solar:check-circle-linear" class="text-emerald-500" />
                智能划痕修复
              </li>
              <li class="flex items-center gap-2 text-xs text-gray-500">
                <Icon icon="solar:check-circle-linear" class="text-emerald-500" />
                AI自动上色
              </li>
              <li class="flex items-center gap-2 text-xs text-gray-500">
                <Icon icon="solar:check-circle-linear" class="text-emerald-500" />
                人脸增强
              </li>
              <li class="flex items-center gap-2 text-xs text-gray-500">
                <Icon icon="solar:check-circle-linear" class="text-emerald-500" />
                自动加入相册
              </li>
              <li class="flex items-center gap-2 text-xs text-gray-500">
                <Icon icon="solar:check-circle-linear" class="text-emerald-500" />
                创建家族记忆
              </li>
            </ul>
          </div>

          <button
            class="w-full py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-shadow"
            @click="handleRepairSubmit"
          >
            提交修复任务
          </button>
        </div>

        <div v-else-if="showSubmitType === 'generation'" class="space-y-4">
          <div class="bg-gray-50 rounded-2xl p-4">
            <p class="text-sm text-gray-600">
              演示模式：将生成3张AI场景图
            </p>
            <div class="mt-3 p-3 bg-white rounded-xl">
              <p class="text-xs text-gray-500 mb-1">提示词</p>
              <p class="text-sm text-gray-700">1980年代中国家庭春节团圆场景，温馨怀旧风格</p>
            </div>
            <div class="mt-3 grid grid-cols-2 gap-2">
              <div class="p-2 bg-white rounded-lg text-center">
                <p class="text-[10px] text-gray-400">风格</p>
                <p class="text-xs text-gray-700">复古</p>
              </div>
              <div class="p-2 bg-white rounded-lg text-center">
                <p class="text-[10px] text-gray-400">数量</p>
                <p class="text-xs text-gray-700">3张</p>
              </div>
            </div>
          </div>

          <button
            class="w-full py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white font-medium rounded-xl shadow-lg hover:shadow-xl transition-shadow"
            @click="handleGenerationSubmit"
          >
            提交生成任务
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes slide-up {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-up {
  animation: slide-up 0.3s ease-out;
}
</style>
