<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <button @click="goBack" class="w-10 h-10 rounded-full bg-white/80 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow">
            <Icon icon="material-symbols:arrow-back" class="text-gray-600 text-lg" />
          </button>
          <div class="w-12 h-12 bg-[#C84A3E] rounded-sm flex items-center justify-center shadow-md relative overflow-hidden">
            <span class="text-white font-serif text-xl font-bold tracking-widest relative z-10">存</span>
          </div>
          <div>
            <h1 class="text-2xl font-bold text-[#5C4A3A] font-serif tracking-wider">记忆管理</h1>
            <p class="text-xs text-gray-500 tracking-[0.15em] uppercase font-medium">Family Memories</p>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <button 
            @click="goToCreate" 
            class="px-6 py-2.5 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors shadow-md flex items-center space-x-2"
          >
            <Icon icon="material-symbols:add" class="text-lg" />
            <span>上传新记忆</span>
          </button>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-6 py-8">
      <section class="mb-8">
        <div class="bg-gradient-to-br from-[#8B6F4E] to-[#6B5342] rounded-2xl p-8 text-white shadow-warm">
          <h3 class="text-xl font-bold mb-6">记忆统计</h3>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div class="text-center p-4 bg-white/10 rounded-xl">
              <p class="text-4xl font-bold">{{ memories.length }}</p>
              <p class="text-sm text-white/70 mt-1">总记忆</p>
            </div>
            <div class="text-center p-4 bg-white/10 rounded-xl">
              <p class="text-4xl font-bold">{{ textCount }}</p>
              <p class="text-sm text-white/70 mt-1">文字</p>
            </div>
            <div class="text-center p-4 bg-white/10 rounded-xl">
              <p class="text-4xl font-bold">{{ imageCount }}</p>
              <p class="text-sm text-white/70 mt-1">图片</p>
            </div>
            <div class="text-center p-4 bg-white/10 rounded-xl">
              <p class="text-4xl font-bold">{{ videoCount }}</p>
              <p class="text-sm text-white/70 mt-1">视频</p>
            </div>
          </div>
        </div>
      </section>

      <section class="mb-6">
        <div class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif mb-4">筛选条件</h3>
          <div class="flex flex-col md:flex-row gap-6">
            <div class="flex-1">
              <label class="block text-sm font-medium text-[#5C4A3A] mb-2">筛选数字人</label>
              <select 
                v-model="selectedAvatarId" 
                @change="loadMemories"
                class="w-full px-4 py-3 bg-[#FAF7F2] rounded-xl border border-[#E8D5C4] text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30 transition-all"
              >
                <option value="">全部数字人</option>
                <option v-for="avatar in avatars" :key="avatar.id" :value="avatar.id">
                  {{ avatar.name }} ({{ avatar.relationship }})
                </option>
              </select>
            </div>
            <div class="flex-1">
              <label class="block text-sm font-medium text-[#5C4A3A] mb-2">筛选类型</label>
              <div class="flex space-x-3">
                <button 
                  v-for="filter in typeFilters" 
                  :key="filter.value"
                  @click="selectedType = filter.value; loadMemories()"
                  :class="[
                    'flex-1 py-3 rounded-xl font-medium transition-all',
                    selectedType === filter.value 
                      ? 'bg-[#8B6F4E] text-white shadow-md' 
                      : 'bg-[#FAF7F2] text-gray-600 border border-[#E8D5C4] hover:border-[#D4A574]'
                  ]"
                >
                  {{ filter.label }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div v-if="loading" class="flex flex-col items-center justify-center py-20">
          <div class="w-16 h-16 border-4 border-[#E8D5C4] border-t-[#8B6F4E] rounded-full animate-spin mb-6"></div>
          <p class="text-gray-500 text-lg">加载中...</p>
        </div>

        <div v-else-if="memories.length === 0" class="flex flex-col items-center justify-center py-20">
          <div class="w-32 h-32 bg-[#FAF7F2] rounded-full flex items-center justify-center mb-6">
            <Icon icon="material-symbols:folder-open-outline" class="text-6xl text-gray-300" />
          </div>
          <h3 class="text-2xl font-medium text-gray-600 mb-2">暂无记忆</h3>
          <p class="text-gray-400 mb-8">点击右上角按钮添加第一个记忆</p>
          <button 
            @click="goToCreate" 
            class="px-8 py-4 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors shadow-md flex items-center space-x-2"
          >
            <Icon icon="material-symbols:add" class="text-xl" />
            <span>添加记忆</span>
          </button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div 
            v-for="memory in memories" 
            :key="memory.id"
            class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100 hover:shadow-lg transition-shadow cursor-pointer group"
            @click="viewMemory(memory.id)"
          >
            <div class="flex items-start space-x-4 mb-4">
              <div 
                :class="[
                  'w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0',
                  memory.type === 'text' ? 'bg-blue-50' :
                  memory.type === 'image' ? 'bg-purple-50' :
                  'bg-red-50'
                ]"
              >
                <Icon 
                  :icon="getTypeIcon(memory.type)" 
                  :class="[
                    'text-2xl',
                    memory.type === 'text' ? 'text-blue-500' :
                    memory.type === 'image' ? 'text-purple-500' :
                    'text-red-500'
                  ]"
                />
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="font-bold text-gray-800 text-lg truncate group-hover:text-[#8B6F4E] transition-colors">{{ memory.title }}</h4>
                <p class="text-xs text-gray-400 mt-1">
                  {{ getAvatarName(memory.avatarId) }} · {{ formatDate(memory.createdAt) }}
                </p>
              </div>
            </div>
            
            <p v-if="memory.description" class="text-sm text-gray-500 mb-4 line-clamp-2">
              {{ memory.description }}
            </p>
            
            <div v-if="memory.tags && memory.tags.length > 0" class="flex flex-wrap gap-1.5 mb-4">
              <span 
                v-for="(tag, index) in memory.tags.slice(0, 4)" 
                :key="index"
                class="px-3 py-1 bg-[#F5E6D3] text-[#8B6F4E] rounded-full text-xs font-medium"
              >
                {{ tag }}
              </span>
              <span v-if="memory.tags.length > 4" class="px-3 py-1 text-gray-400 text-xs">
                +{{ memory.tags.length - 4 }}
              </span>
            </div>

            <div class="flex items-center justify-end space-x-2 pt-4 border-t border-stone-100 opacity-0 group-hover:opacity-100 transition-opacity">
              <button 
                @click.stop="editMemory(memory.id)" 
                class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                title="编辑"
              >
                <Icon icon="material-symbols:edit-outline" class="text-gray-500" />
              </button>
              <button 
                @click.stop="confirmDelete(memory.id)" 
                class="p-2 rounded-lg hover:bg-red-50 transition-colors"
                title="删除"
              >
                <Icon icon="material-symbols:delete-outline" class="text-red-400" />
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>

    <div v-if="showDeleteModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-8 mx-4 max-w-md w-full shadow-2xl">
        <div class="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
          <Icon icon="material-symbols:delete-forever" class="text-4xl text-red-500" />
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-2 text-center">确认删除</h3>
        <p class="text-gray-600 mb-6 text-center">确定要删除这个记忆吗？此操作无法撤销。</p>
        <div class="flex space-x-4">
          <button 
            @click="showDeleteModal = false" 
            class="flex-1 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors"
          >
            取消
          </button>
          <button 
            @click="deleteMemory" 
            class="flex-1 py-3 bg-red-600 text-white rounded-xl font-medium hover:bg-red-700 transition-colors"
          >
            确认删除
          </button>
        </div>
      </div>
    </div>

    <div v-if="showToast" class="fixed top-24 left-1/2 -translate-x-1/2 z-50">
      <div :class="[
        'px-8 py-4 rounded-2xl shadow-2xl flex items-center space-x-3 animate-bounce',
        toastType === 'success' ? 'bg-green-500' : 'bg-red-500',
        'text-white'
      ]">
        <Icon :icon="toastType === 'success' ? 'material-symbols:check-circle' : 'material-symbols:error'" class="text-2xl" />
        <span class="font-medium">{{ toastMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { apiService, type Avatar, type MemoryListItem, type MemoryType } from '../services/api'

const router = useRouter()

const avatars = ref<Avatar[]>([])
const memories = ref<MemoryListItem[]>([])
const loading = ref(false)
const selectedAvatarId = ref('')
const selectedType = ref<string>('all')

const showDeleteModal = ref(false)
const deleteMemoryId = ref('')
const showToast = ref(false)
const toastType = ref<'success' | 'error'>('success')
const toastMessage = ref('')

const typeFilters = [
  { value: 'all', label: '全部' },
  { value: 'text', label: '文字' },
  { value: 'image', label: '图片' },
  { value: 'video', label: '视频' }
]

const textCount = computed(() => memories.value.filter(m => m.type === 'text').length)
const imageCount = computed(() => memories.value.filter(m => m.type === 'image').length)
const videoCount = computed(() => memories.value.filter(m => m.type === 'video').length)

const getTypeIcon = (type: MemoryType) => {
  const icons = {
    text: 'material-symbols:edit-note-outline',
    image: 'material-symbols:image-outline',
    video: 'material-symbols:videocam-outline'
  }
  return icons[type] || icons.text
}

const getAvatarName = (avatarId: string) => {
  const avatar = avatars.value.find(a => a.id === avatarId)
  return avatar ? avatar.name : '未知数字人'
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const goBack = () => {
  router.back()
}

const showToastMessage = (type: 'success' | 'error', message: string) => {
  toastType.value = type
  toastMessage.value = message
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

const loadAvatars = async () => {
  const response = await apiService.getAvatars()
  if (response.success && response.data) {
    avatars.value = response.data.avatars
  }
}

const loadMemories = async () => {
  loading.value = true
  try {
    const options: { avatarId?: string; type?: MemoryType } = {}
    
    if (selectedAvatarId.value) {
      options.avatarId = selectedAvatarId.value
    }
    
    if (selectedType.value !== 'all') {
      options.type = selectedType.value as MemoryType
    }

    const response = await apiService.getMemories(options)
    if (response.success && response.data) {
      memories.value = response.data.memories
    } else {
      memories.value = []
    }
  } catch (error) {
    memories.value = []
  } finally {
    loading.value = false
  }
}

const goToCreate = () => {
  router.push('/memory/create')
}

const viewMemory = (memoryId: string) => {
  router.push(`/memory/edit/${memoryId}`)
}

const editMemory = (memoryId: string) => {
  router.push(`/memory/edit/${memoryId}`)
}

const confirmDelete = (memoryId: string) => {
  deleteMemoryId.value = memoryId
  showDeleteModal.value = true
}

const deleteMemory = async () => {
  try {
    const response = await apiService.deleteMemory(deleteMemoryId.value)
    if (response.success) {
      showDeleteModal.value = false
      showToastMessage('success', '记忆删除成功')
      loadMemories()
    } else {
      showToastMessage('error', response.error || '删除失败')
    }
  } catch (error) {
    showToastMessage('error', '删除失败，请重试')
  }
}

onMounted(() => {
  loadAvatars()
  loadMemories()
})
</script>
