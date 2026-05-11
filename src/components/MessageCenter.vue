<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="$router.back()" class="w-10 h-10 rounded-full hover:bg-[#E8D5C4] flex items-center justify-center transition-colors">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E]" />
          </button>
          <div>
            <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">消息中心</h1>
            <p class="text-xs text-gray-500">纪念日提醒和系统通知</p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <button v-if="unreadCount > 0" @click="markAllRead" class="px-3 py-1.5 bg-[#E8D5C4] text-[#8B6F4E] rounded-lg text-sm font-medium hover:bg-[#D4C4B0] transition-colors">
            全部已读
          </button>
          <button v-if="totalCount > 0" @click="showDeleteConfirm = true" class="px-3 py-1.5 bg-red-50 text-red-500 rounded-lg text-sm font-medium hover:bg-red-100 transition-colors">
            清空
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-6 py-6">
      <div class="flex border-b border-[#E8D5C4] mb-6">
        <button 
          v-for="tab in tabs" 
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'px-6 py-3 text-sm font-medium transition-colors relative',
            activeTab === tab.id ? 'text-[#8B6F4E]' : 'text-gray-500 hover:text-gray-700'
          ]">
          <span class="flex items-center space-x-2">
            <Icon :icon="tab.icon" class="text-lg" />
            <span>{{ tab.label }}</span>
            <span v-if="getTabCount(tab.id) > 0" class="w-5 h-5 rounded-full flex items-center justify-center text-xs"
              :class="tab.id === 'unread' ? 'bg-[#C84A3E] text-white' : 'bg-gray-200 text-gray-600'">
              {{ getTabCount(tab.id) }}
            </span>
          </span>
          <div v-if="activeTab === tab.id" class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#8B6F4E]"></div>
        </button>
      </div>

      <div v-if="filteredMessages.length > 0" class="space-y-3">
        <div v-for="message in filteredMessages" :key="message.id" 
          @click="viewMessage(message)"
          class="bg-white rounded-xl shadow-soft border cursor-pointer transition-all hover:shadow-md"
          :class="message.status === 'unread' ? 'border-[#E8D5C4] bg-[#FAF7F2]' : 'border-stone-100'">
          <div class="p-4">
            <div class="flex items-start justify-between">
              <div class="flex items-start space-x-3 flex-1 min-w-0">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  :class="messageTypeBg(message.type)">
                  <Icon :icon="messageTypeIcon(message.type)" class="text-lg" :class="messageTypeText(message.type)" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2 mb-1">
                    <h4 class="font-medium text-[#5C4A3A]" :class="message.status === 'unread' ? 'font-bold' : ''">
                      {{ message.title }}
                    </h4>
                    <span v-if="message.status === 'unread'" class="w-2 h-2 rounded-full bg-[#C84A3E] flex-shrink-0"></span>
                  </div>
                  <p class="text-sm text-gray-600 line-clamp-2">{{ message.content }}</p>
                  <p class="text-xs text-gray-400 mt-2">{{ formatDate(message.createdAt) }}</p>
                </div>
              </div>
              <div class="flex items-center space-x-1 ml-3 flex-shrink-0">
                <button v-if="message.status === 'unread'" 
                  @click.stop="markAsRead(message)"
                  class="w-8 h-8 rounded-full hover:bg-white/50 flex items-center justify-center transition-colors">
                  <Icon icon="solar:check-circle-bold" class="text-green-500 text-sm" />
                </button>
                <button @click.stop="deleteMessage(message)" class="w-8 h-8 rounded-full hover:bg-red-50 flex items-center justify-center transition-colors">
                  <Icon icon="solar:trash-bin-trash-bold" class="text-red-500 text-sm" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="bg-white rounded-2xl shadow-soft border border-stone-100 p-12 text-center">
        <Icon icon="solar:inbox-empty-bold" class="text-6xl text-gray-300 mx-auto mb-4" />
        <p class="text-gray-500 mb-2">暂无消息</p>
        <p class="text-gray-400 text-sm">
          {{ activeTab === 'unread' ? '您没有未读消息' : activeTab === 'read' ? '您没有已读消息' : '消息列表为空' }}
        </p>
      </div>
    </main>

    <div v-if="showDetailModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        <div class="border-b border-stone-100 px-6 py-4 flex items-center justify-between">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">消息详情</h3>
          <button @click="closeDetailModal" class="w-8 h-8 rounded-full hover:bg-gray-100 flex items-center justify-center transition-colors">
            <Icon icon="material-symbols:close" class="text-gray-500" />
          </button>
        </div>
        <div class="p-6" v-if="selectedMessage">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-12 h-12 rounded-xl flex items-center justify-center"
              :class="messageTypeBg(selectedMessage.type)">
              <Icon :icon="messageTypeIcon(selectedMessage.type)" class="text-2xl" :class="messageTypeText(selectedMessage.type)" />
            </div>
            <div>
              <h4 class="font-bold text-[#5C4A3A]">{{ selectedMessage.title }}</h4>
              <p class="text-sm text-gray-500">{{ formatDate(selectedMessage.createdAt) }}</p>
            </div>
          </div>

          <div class="bg-[#FAF7F2] rounded-xl p-4">
            <p class="text-sm text-[#5C4A3A] whitespace-pre-wrap">{{ selectedMessage.content }}</p>
          </div>

          <div class="mt-4 flex items-center justify-between text-sm">
            <span class="text-gray-500">
              状态: <span class="text-[#5C4A3A]">{{ selectedMessage.status === 'unread' ? '未读' : '已读' }}</span>
            </span>
            <span class="text-gray-500">
              类型: <span class="text-[#5C4A3A]">{{ messageTypeLabel(selectedMessage.type) }}</span>
            </span>
          </div>
        </div>
        <div class="border-t border-stone-100 px-6 py-4 flex justify-end space-x-3">
          <button v-if="selectedMessage?.status === 'unread'" @click="markSelectedAsRead" class="px-4 py-2 text-[#8B6F4E] bg-[#E8D5C4] rounded-xl text-sm font-medium hover:bg-[#D4C4B0] transition-colors">
            标记已读
          </button>
          <button @click="closeDetailModal" class="px-4 py-2 bg-[#8B6F4E] text-white rounded-xl text-sm font-medium hover:bg-[#A67B5B] transition-colors">
            关闭
          </button>
        </div>
      </div>
    </div>

    <div v-if="showDeleteConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm">
        <div class="p-6 text-center">
          <Icon icon="solar:warning-square-bold" class="text-5xl text-amber-500 mx-auto mb-4" />
          <h3 class="text-lg font-bold text-[#5C4A3A] mb-2">确认清空</h3>
          <p class="text-gray-600 text-sm">确定要清空所有消息吗？此操作不可撤销。</p>
        </div>
        <div class="border-t border-stone-100 px-6 py-4 flex justify-center space-x-3">
          <button @click="showDeleteConfirm = false" class="px-6 py-2 text-gray-600 bg-gray-100 rounded-xl text-sm font-medium hover:bg-gray-200 transition-colors">
            取消
          </button>
          <button @click="confirmDeleteAll" class="px-6 py-2 bg-red-500 text-white rounded-xl text-sm font-medium hover:bg-red-600 transition-colors">
            确认清空
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { 
  apiService, 
  Message,
  MessageType,
  MessageStatus,
  MessageListResponse
} from '../services/api'

const activeTab = ref<'all' | 'unread' | 'read'>('all')
const messages = ref<Message[]>([])
const unreadCount = ref(0)
const totalCount = ref(0)

const showDetailModal = ref(false)
const selectedMessage = ref<Message | null>(null)
const showDeleteConfirm = ref(false)

const tabs = computed(() => [
  { id: 'all', label: '全部', icon: 'solar:archive-bold' },
  { id: 'unread', label: '未读', icon: 'solar:bell-bold' },
  { id: 'read', label: '已读', icon: 'solar:check-circle-bold' }
])

const filteredMessages = computed(() => {
  if (activeTab.value === 'unread') {
    return messages.value.filter(m => m.status === 'unread')
  } else if (activeTab.value === 'read') {
    return messages.value.filter(m => m.status === 'read')
  }
  return messages.value
})

const getTabCount = (tabId: string): number => {
  if (tabId === 'unread') return unreadCount.value
  if (tabId === 'read') return totalCount.value - unreadCount.value
  return totalCount.value
}

const messageTypeIcon = (type: MessageType): string => {
  const icons: Record<MessageType, string> = {
    anniversary_reminder: 'solar:calendar-bold',
    system_notification: 'solar:info-circle-bold'
  }
  return icons[type] || 'solar:bell-bold'
}

const messageTypeLabel = (type: MessageType): string => {
  const labels: Record<MessageType, string> = {
    anniversary_reminder: '纪念日提醒',
    system_notification: '系统通知'
  }
  return labels[type] || type
}

const messageTypeBg = (type: MessageType): string => {
  const bgs: Record<MessageType, string> = {
    anniversary_reminder: 'bg-pink-100',
    system_notification: 'bg-blue-100'
  }
  return bgs[type] || 'bg-gray-100'
}

const messageTypeText = (type: MessageType): string => {
  const texts: Record<MessageType, string> = {
    anniversary_reminder: 'text-pink-600',
    system_notification: 'text-blue-600'
  }
  return texts[type] || 'text-gray-600'
}

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    if (diffHours === 0) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60))
      return diffMinutes <= 1 ? '刚刚' : `${diffMinutes}分钟前`
    }
    return `${diffHours}小时前`
  } else if (diffDays === 1) {
    return '昨天'
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  }
  
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const loadMessages = async () => {
  try {
    const response = await apiService.getMessages({ limit: 100 })
    if (response.success && response.data) {
      messages.value = response.data.messages
      unreadCount.value = response.data.unreadCount
      totalCount.value = response.data.total
    }
  } catch (error) {
    console.error('加载消息失败:', error)
  }
}

const viewMessage = async (message: Message) => {
  selectedMessage.value = message
  showDetailModal.value = true
  
  if (message.status === 'unread') {
    try {
      const response = await apiService.markMessagesRead({
        messageIds: [message.id]
      })
      if (response.success) {
        const index = messages.value.findIndex(m => m.id === message.id)
        if (index > -1) {
          messages.value[index].status = 'read'
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
      }
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedMessage.value = null
}

const markAsRead = async (message: Message) => {
  try {
    const response = await apiService.markMessagesRead({
      messageIds: [message.id]
    })
    if (response.success) {
      const index = messages.value.findIndex(m => m.id === message.id)
      if (index > -1) {
        messages.value[index].status = 'read'
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
    }
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

const markSelectedAsRead = async () => {
  if (selectedMessage.value) {
    await markAsRead(selectedMessage.value)
    closeDetailModal()
  }
}

const markAllRead = async () => {
  try {
    const response = await apiService.markMessagesRead({
      markAll: true
    })
    if (response.success) {
      messages.value.forEach(m => {
        if (m.status === 'unread') {
          m.status = 'read'
        }
      })
      unreadCount.value = 0
    }
  } catch (error) {
    console.error('全部标记已读失败:', error)
  }
}

const deleteMessage = async (message: Message) => {
  if (confirm('确定要删除这条消息吗？')) {
    try {
      const response = await apiService.deleteMessage(message.id)
      if (response.success) {
        const index = messages.value.findIndex(m => m.id === message.id)
        if (index > -1) {
          messages.value.splice(index, 1)
          totalCount.value = Math.max(0, totalCount.value - 1)
          if (message.status === 'unread') {
            unreadCount.value = Math.max(0, unreadCount.value - 1)
          }
        }
      } else {
        alert(`删除失败: ${response.error || '未知错误'}`)
      }
    } catch (error) {
      console.error('删除消息失败:', error)
      alert('删除失败')
    }
  }
}

const confirmDeleteAll = async () => {
  try {
    const response = await apiService.deleteAllMessages()
    if (response.success) {
      messages.value = []
      totalCount.value = 0
      unreadCount.value = 0
      showDeleteConfirm.value = false
    } else {
      alert(`清空失败: ${response.error || '未知错误'}`)
    }
  } catch (error) {
    console.error('清空消息失败:', error)
    alert('清空失败')
  }
}

onMounted(() => {
  loadMessages()
})
</script>
