<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { Icon } from '@iconify/vue';
import type { Message } from '../../types/task';
import { MessageType } from '../../types/task';
import { messageApi } from '../../api';

interface Props {
  show?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
});

const emit = defineEmits<{
  close: [];
  'message-click': [message: Message];
  'task-click': [taskId: string];
}>(); 

const messages = ref<Message[]>([]);
const loading = ref(false);
const unreadCount = ref(0);
const activeFilter = ref<'all' | 'unread'>('all');

const filteredMessages = computed(() => {
  if (activeFilter.value === 'unread') {
    return messages.value.filter((m) => !m.isRead);
  }
  return messages.value;
});

async function loadMessages() {
  loading.value = true;
  try {
    const response = await messageApi.list({ limit: 50 });
    if (response.success) {
      messages.value = response.data.items;
    }
  } catch (err) {
    console.error('Load messages error:', err);
  } finally {
    loading.value = false;
  }
}

async function loadUnreadCount() {
  try {
    const response = await messageApi.getUnreadCount();
    if (response.success) {
      unreadCount.value = response.data.count;
    }
  } catch (err) {
    console.error('Load unread count error:', err);
  }
}

async function handleMessageClick(message: Message) {
  if (!message.isRead) {
    try {
      await messageApi.markRead(message.id);
      message.isRead = true;
      unreadCount.value = Math.max(0, unreadCount.value - 1);
    } catch (err) {
      console.error('Mark message read error:', err);
    }
  }

  emit('message-click', message);

  if (message.taskId) {
    emit('task-click', message.taskId);
  }
}

async function handleMarkAllRead() {
  try {
    const response = await messageApi.markAllRead();
    if (response.success) {
      messages.value.forEach((m) => (m.isRead = true));
      unreadCount.value = 0;
    }
  } catch (err) {
    console.error('Mark all read error:', err);
  }
}

function getMessageIcon(type: MessageType) {
  switch (type) {
    case MessageType.SUCCESS:
      return 'solar:check-circle-bold';
    case MessageType.ERROR:
      return 'solar:close-circle-bold';
    case MessageType.WARNING:
      return 'solar:alert-triangle-bold';
    default:
      return 'solar:info-circle-bold';
  }
}

function getMessageIconColor(type: MessageType) {
  switch (type) {
    case MessageType.SUCCESS:
      return 'text-emerald-500 bg-emerald-50';
    case MessageType.ERROR:
      return 'text-red-500 bg-red-50';
    case MessageType.WARNING:
      return 'text-amber-500 bg-amber-50';
    default:
      return 'text-blue-500 bg-blue-50';
  }
}

function formatTime(timestamp: string) {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;

  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

watch(
  () => props.show,
  (val) => {
    if (val) {
      loadMessages();
    }
  }
);

onMounted(() => {
  loadUnreadCount();
});

defineExpose({
  loadMessages,
  loadUnreadCount,
  unreadCount,
});
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-end justify-center bg-black/30 backdrop-blur-sm"
    @click.self="emit('close')"
  >
    <div class="w-full max-w-md bg-white rounded-t-3xl max-h-[85vh] flex flex-col animate-slide-up">
      <div class="flex items-center justify-between p-4 border-b border-stone-100 flex-shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-9 h-9 rounded-full bg-[#8B6F4E]/10 flex items-center justify-center">
            <Icon icon="solar:bell-bing-bold" class="text-[#8B6F4E] text-lg" />
          </div>
          <div>
            <h3 class="text-base font-bold text-gray-800">消息中心</h3>
            <p v-if="unreadCount > 0" class="text-[10px] text-gray-400">
              {{ unreadCount }} 条未读
            </p>
          </div>
        </div>
        <button
          class="w-9 h-9 rounded-full bg-gray-50 flex items-center justify-center text-gray-600 hover:bg-gray-100 transition-colors"
          @click="emit('close')"
        >
          <Icon icon="solar:close-linear" class="text-lg" />
        </button>
      </div>

      <div class="flex items-center gap-1 px-4 py-2 bg-gray-50/50 border-b border-stone-100 flex-shrink-0">
        <button
          class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all"
          :class="{
            'bg-white shadow-sm text-[#8B6F4E]': activeFilter === 'all',
            'text-gray-500': activeFilter !== 'all',
          }"
          @click="activeFilter = 'all'"
        >
          全部
        </button>
        <button
          class="px-4 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1"
          :class="{
            'bg-white shadow-sm text-[#8B6F4E]': activeFilter === 'unread',
            'text-gray-500': activeFilter !== 'unread',
          }"
          @click="activeFilter = 'unread'"
        >
          未读
          <span
            v-if="unreadCount > 0"
            class="w-4 h-4 rounded-full bg-red-500 text-white text-[9px] flex items-center justify-center"
          >
            {{ unreadCount }}
          </span>
        </button>
        <button
          v-if="unreadCount > 0"
          class="ml-auto text-xs text-[#8B6F4E] font-medium"
          @click="handleMarkAllRead"
        >
          全部已读
        </button>
      </div>

      <div class="flex-1 overflow-y-auto">
        <div v-if="loading && messages.length === 0" class="py-12 text-center">
          <div class="w-8 h-8 border-2 border-[#8B6F4E]/20 border-t-[#8B6F4E] rounded-full animate-spin mx-auto mb-3"></div>
          <p class="text-xs text-gray-500">加载中...</p>
        </div>

        <div v-else-if="filteredMessages.length === 0" class="py-16 text-center">
          <Icon icon="solar:inbox-line-duotone" class="text-4xl text-gray-300 mx-auto mb-3" />
          <p class="text-sm text-gray-400">暂无消息</p>
        </div>

        <div v-else class="divide-y divide-stone-50">
          <div
            v-for="message in filteredMessages"
            :key="message.id"
            class="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
            :class="{ 'bg-blue-50/30': !message.isRead }"
            @click="handleMessageClick(message)"
          >
            <div class="flex items-start gap-3">
              <div
                class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                :class="getMessageIconColor(message.type as MessageType)"
              >
                <Icon :icon="getMessageIcon(message.type as MessageType)" class="text-lg" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-2">
                  <h4 class="text-sm font-semibold text-gray-800 truncate">
                    {{ message.title }}
                  </h4>
                  <span class="text-[10px] text-gray-400 flex-shrink-0">
                    {{ formatTime(message.createdAt) }}
                  </span>
                </div>
                <p class="text-xs text-gray-500 mt-1 line-clamp-2">
                  {{ message.content }}
                </p>
                <div
                  v-if="message.actionText"
                  class="mt-2 inline-flex items-center gap-1 text-xs text-[#8B6F4E] font-medium"
                >
                  {{ message.actionText }}
                  <Icon icon="solar:arrow-right-linear" class="text-sm" />
                </div>
              </div>
              <div v-if="!message.isRead" class="w-2 h-2 rounded-full bg-[#8B6F4E] flex-shrink-0 mt-2"></div>
            </div>
          </div>
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
