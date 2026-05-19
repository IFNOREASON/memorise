<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-200 p-4">
    <div class="w-[393px] h-[852px] paper-texture overflow-hidden relative shadow-2xl rounded-[50px] border-[12px] border-gray-900">
      
      <div class="h-12 flex justify-between items-center px-8 pt-3 pb-1">
        <span class="text-sm font-semibold text-gray-800">09:41</span>
        <div class="flex items-center space-x-1.5">
          <Icon icon="material-symbols:signal-cellular-4-bar" class="text-gray-800" style="font-size: 16px;" />
          <Icon icon="material-symbols:wifi" class="text-gray-800" style="font-size: 16px;" />
          <Icon icon="material-symbols:battery-full" class="text-gray-800" style="font-size: 16px;" />
        </div>
      </div>

      <div class="h-[calc(100%-90px)] overflow-y-auto no-scrollbar pb-20">
        
        <header class="px-6 py-4 flex items-center justify-between sticky top-0 z-50 glass-warm">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-[#C84A3E] rounded-sm flex items-center justify-center shadow-md relative overflow-hidden">
              <div class="absolute inset-0 opacity-30" :style="noisePatternStyle"></div>
              <span class="text-white font-serif text-lg font-bold tracking-widest relative z-10">存</span>
            </div>
            <div>
              <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">memorise</h1>
              <p class="text-[9px] text-gray-500 tracking-[0.15em] uppercase font-medium">Family Memorial</p>
            </div>
          </div>
          <button class="w-9 h-9 rounded-full bg-white/80 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow">
            <Icon icon="material-symbols:menu" class="text-gray-600 text-lg" />
          </button>
        </header>

        <section class="px-6 mt-2 relative">
          <div class="absolute top-10 right-0 w-32 h-32 bg-[#E8D5C4] rounded-full blur-3xl opacity-40"></div>
          <div class="absolute bottom-0 left-0 w-24 h-24 bg-[#D4A574] rounded-full blur-2xl opacity-20"></div>
          
          <div class="relative bg-gradient-to-br from-[#8B6F4E] to-[#6B5342] rounded-[32px] p-6 text-white shadow-warm overflow-hidden">
            <div class="absolute inset-0 opacity-10" :style="dotPatternStyle"></div>
            
            <div class="relative z-10">
              <div class="flex items-center space-x-2 mb-4">
                <span class="px-3 py-1 bg-white/20 backdrop-blur rounded-full text-[10px] font-medium border border-white/10">
                  家族精神纪念馆
                </span>
                <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              </div>
              
              <h2 class="text-2xl font-serif font-medium leading-relaxed mb-3">
                数字生命<br>
                <span class="text-[#E8D5C4]">世代相传</span>
              </h2>
              
              <p class="text-xs text-white/80 leading-relaxed mb-6 max-w-[280px]">
                打破时空限制，让逝去的亲人"可陪伴"、家族智慧"可传承"、思念情感"可寄托"
              </p>
              
              <div class="flex items-center space-x-6 border-t border-white/20 pt-4">
                <div>
                  <p class="text-lg font-bold">{{ memberCount }}</p>
                  <p class="text-[10px] text-white/60">家族成员</p>
                </div>
                <div>
                  <p class="text-lg font-bold">{{ galleryCount }}</p>
                  <p class="text-[10px] text-white/60">珍贵影像</p>
                </div>
                <div>
                  <p class="text-lg font-bold">{{ avatarCount }}</p>
                  <p class="text-[10px] text-white/60">数字生命</p>
                </div>
              </div>
            </div>
            
            <div class="absolute -right-4 -bottom-4 w-32 h-32 opacity-20">
              <Icon icon="solar:tree-bold" class="text-white text-8xl" />
            </div>
          </div>
        </section>

        <section class="px-6 mt-8">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-[#5C4A3A] font-serif">五大传承模块</h3>
            <span class="text-xs text-gray-400">滑动查看</span>
          </div>
          
          <div class="grid grid-cols-5 gap-2">
            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-2 shadow-soft border border-[#E8D5C4] group-active:scale-90 transition-all relative">
                <div class="absolute inset-0 bg-[#E8D5C4] rounded-2xl opacity-0 group-hover:opacity-20 transition-opacity"></div>
                <Icon icon="solar:tree-bold-duotone" class="text-[#8B6F4E] text-xl" />
              </div>
              <span class="text-xs font-semibold text-[#5C4A3A]">家承</span>
              <span class="text-[8px] text-gray-400 mt-0.5">族谱</span>
            </div>

            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-2 shadow-soft border border-orange-100 group-active:scale-90 transition-all">
                <Icon icon="solar:gallery-wide-bold-duotone" class="text-orange-600 text-xl" />
              </div>
              <span class="text-xs font-semibold text-[#5C4A3A]">影集</span>
              <span class="text-[8px] text-gray-400 mt-0.5">影像</span>
            </div>

            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-14 h-14 bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] rounded-2xl flex items-center justify-center mb-2 shadow-glow border-2 border-white group-active:scale-90 transition-all relative -mt-1">
                <Icon icon="solar:magic-stick-3-bold-duotone" class="text-white text-2xl" />
                <div class="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full border-2 border-white"></div>
              </div>
              <span class="text-xs font-bold text-[#8B6F4E]">生境</span>
              <span class="text-[8px] text-[#D4A574] font-medium">数字生命</span>
            </div>

            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-2 shadow-soft border border-emerald-100 group-active:scale-90 transition-all">
                <Icon icon="solar:chat-round-dots-bold-duotone" class="text-emerald-600 text-xl" />
              </div>
              <span class="text-xs font-semibold text-[#5C4A3A]">语伴</span>
              <span class="text-[8px] text-gray-400 mt-0.5">AI对话</span>
            </div>

            <div class="flex flex-col items-center group cursor-pointer">
              <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center mb-2 shadow-soft border border-blue-100 group-active:scale-90 transition-all">
                <Icon icon="solar:heart-lock-bold-duotone" class="text-blue-500 text-xl" />
              </div>
              <span class="text-xs font-semibold text-[#5C4A3A]">念境</span>
              <span class="text-[8px] text-gray-400 mt-0.5">3D空间</span>
            </div>
          </div>
        </section>

        <section class="px-6 mt-8">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-[#5C4A3A] font-serif">我的数字家人</h3>
            <button class="text-xs text-[#8B6F4E] font-medium flex items-center">
              查看全部
              <Icon icon="material-symbols:chevron-right" class="ml-1" style="font-size: 16px;" />
            </button>
          </div>
          
          <div class="space-y-3">
            <div v-if="avatars.length === 0" class="text-center py-8 text-gray-400">
              <p class="text-xs">暂无数字家人</p>
            </div>
            <div v-for="avatar in avatars" :key="avatar.id" 
                 class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100 hover-lift cursor-pointer flex items-center space-x-4"
                 :class="{ 'opacity-80': avatar.status !== 'active' }">
              <div class="relative">
                <div class="w-16 h-16 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] p-0.5">
                  <div class="w-full h-full rounded-full bg-gray-200 overflow-hidden flex items-center justify-center">
                    <img v-if="avatar.avatar" :src="getFullMediaUrl(avatar.avatar)" class="w-full h-full object-cover" :alt="avatar.name">
                    <Icon v-else icon="solar:user-bold" class="text-3xl text-gray-400" />
                  </div>
                </div>
                <div v-if="avatar.status === 'active'" class="absolute bottom-0 right-0 w-5 h-5 bg-green-500 rounded-full border-2 border-white flex items-center justify-center">
                  <Icon icon="solar:check-bold" class="text-white text-xs" />
                </div>
                <div v-else-if="avatar.status === 'training'" class="absolute bottom-0 right-0 w-5 h-5 bg-amber-400 rounded-full border-2 border-white flex items-center justify-center">
                  <Icon icon="solar:pause-bold" class="text-white text-xs" />
                </div>
              </div>
              <div class="flex-1">
                <div class="flex items-center space-x-2">
                  <h4 class="font-bold text-gray-800">{{ avatar.relationship }} · {{ avatar.name }}</h4>
                  <span v-if="avatar.status === 'active'" class="px-2 py-0.5 bg-[#E8D5C4] text-[#8B6F4E] text-[10px] rounded-full">已激活</span>
                  <span v-else-if="avatar.status === 'training'" class="px-2 py-0.5 bg-gray-100 text-gray-500 text-[10px] rounded-full">训练中</span>
                  <span v-else class="px-2 py-0.5 bg-gray-100 text-gray-500 text-[10px] rounded-full">{{ avatar.status }}</span>
                </div>
                <p class="text-xs text-gray-500 mt-1">
                  {{ avatar.birthYear }}{{ avatar.deathYear ? '-' + avatar.deathYear : '' }} · 训练度 {{ avatar.progress }}%
                </p>
                <div v-if="avatar.status === 'active'" class="flex items-center mt-2 space-x-3">
                  <span class="text-[10px] text-gray-400 flex items-center">
                    <Icon icon="solar:chat-dots-linear" class="mr-1" style="font-size: 12px;" />
                    {{ avatar.chatCount || 0 }} 对话
                  </span>
                </div>
                <div v-else-if="avatar.status === 'training'" class="w-full bg-gray-100 rounded-full h-1.5 mt-2">
                  <div class="bg-amber-400 h-1.5 rounded-full" :style="{ width: avatar.progress + '%' }"></div>
                </div>
              </div>
              <button v-if="avatar.status === 'active'" class="w-10 h-10 rounded-full bg-[#8B6F4E] flex items-center justify-center shadow-md hover:shadow-lg transition-shadow">
                <Icon icon="solar:phone-bold" class="text-white text-xl" />
              </button>
            </div>
          </div>
        </section>

        <section class="px-6 mt-8">
          <h3 class="text-base font-bold text-[#5C4A3A] font-serif mb-4">家族记忆轴</h3>
          
          <div class="relative">
            <div v-if="familyMemories.length === 0" class="text-center py-8 text-gray-400">
              <p class="text-xs">暂无家族记忆</p>
            </div>

            <div v-else class="flex items-start space-x-4 overflow-x-auto pb-4 no-scrollbar" style="scroll-snap-type: x mandatory;">
              <div v-for="(memory, index) in familyMemories.slice(0, 8)" :key="memory.id" 
                   class="flex-shrink-0 flex flex-col items-center" style="scroll-snap-align: start; width: 160px;">
                <div class="w-40 h-32 rounded-xl overflow-hidden shadow-soft border border-stone-100 mb-2 flex-shrink-0">
                  <img v-if="memory.mediaUrl" 
                       :src="getFullMediaUrl(memory.mediaUrl)" 
                       class="w-full h-full object-contain bg-gray-50" 
                       :alt="memory.title">
                  <div v-else class="w-full h-full flex flex-col items-center justify-center"
                       :class="getMemoryTypeBgColor(memory.type)">
                    <Icon :icon="getMemoryTypeIcon(memory.type)" class="text-2xl" :class="getMemoryTypeIconColor(memory.type)" />
                    <span class="text-xs mt-1" :class="getMemoryTypeIconColor(memory.type)">{{ getMemoryTypeLabel(memory.type) }}</span>
                  </div>
                </div>
                <div class="w-full text-center">
                  <p class="text-[10px] text-gray-400 mb-1">{{ formatMemoryDate(memory.eventDate || memory.createdAt) }}</p>
                  <h4 class="text-xs font-bold text-gray-800 truncate">{{ memory.title }}</h4>
                  <p v-if="memory.description" class="text-[10px] text-gray-500 mt-1 line-clamp-2">{{ memory.description }}</p>
                </div>
                <div class="w-4 h-4 rounded-full border-2 border-white shadow-sm mt-2"
                     :class="getMemoryTypeColor(memory.type)"></div>
              </div>
            </div>
            
            <div class="absolute left-0 right-0 top-36 h-0.5 bg-gradient-to-r from-transparent via-[#E8D5C4] to-transparent pointer-events-none"></div>
          </div>
        </section>

        <section class="px-6 mt-8 mb-8">
          <div class="grid grid-cols-2 gap-3">
            <button class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100 flex flex-col items-center space-y-2 hover-lift">
              <div class="w-12 h-12 bg-[#E8D5C4] rounded-full flex items-center justify-center">
                <Icon icon="solar:upload-minimalistic-bold" class="text-[#8B6F4E] text-2xl" />
              </div>
              <span class="text-sm font-medium text-gray-700">上传老照片</span>
              <span class="text-[10px] text-gray-400">修复 & 上色</span>
            </button>
            
            <button class="bg-white rounded-2xl p-4 shadow-soft border border-stone-100 flex flex-col items-center space-y-2 hover-lift">
              <div class="w-12 h-12 bg-[#F5E6D3] rounded-full flex items-center justify-center">
                <Icon icon="solar:video-frame-play-horizontal-bold" class="text-[#D4A574] text-2xl" />
              </div>
              <span class="text-sm font-medium text-gray-700">生成影像</span>
              <span class="text-[10px] text-gray-400">动态回忆</span>
            </button>
          </div>
        </section>

        <div class="px-6 mb-8 text-center">
          <div class="inline-block seal-stamp px-3 py-1.5 mb-3">
            <span class="text-xs font-serif font-bold tracking-widest">精神永存</span>
          </div>
          <p class="text-xs text-gray-400 tracking-widest uppercase">Digital Life, Eternal Legacy</p>
        </div>
      </div>

      <nav class="absolute bottom-0 w-full h-[84px] bg-white/95 backdrop-blur-xl border-t border-stone-100 px-2 flex justify-between items-start pt-2 safe-area-inset-bottom z-50">
        <div class="flex flex-col items-center flex-1 py-2 cursor-pointer">
          <div class="w-10 h-10 rounded-full bg-[#8B6F4E]/10 flex items-center justify-center">
            <Icon icon="solar:home-2-bold" class="text-xl text-[#8B6F4E]" />
          </div>
          <span class="text-[10px] mt-1 font-bold text-[#8B6F4E]">首页</span>
        </div>
        
        <div class="flex flex-col items-center flex-1 py-2 cursor-pointer opacity-60 hover:opacity-100 transition-opacity">
          <div class="w-10 h-10 rounded-full flex items-center justify-center">
            <Icon icon="solar:tree-bold-duotone" class="text-xl text-gray-400" />
          </div>
          <span class="text-[10px] mt-1 text-gray-400">家承</span>
        </div>
        
        <div class="flex flex-col items-center flex-1 -mt-5 relative">
          <div class="w-16 h-16 bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] rounded-full border-4 border-[#FAF7F2] shadow-warm flex items-center justify-center cursor-pointer active:scale-90 transition-transform animate-pulse-glow">
            <Icon icon="solar:magic-stick-3-bold-duotone" class="text-white text-3xl" />
          </div>
          <span class="text-[10px] mt-1 text-[#8B6F4E] font-bold">创建</span>
        </div>
        
        <div class="flex flex-col items-center flex-1 py-2 cursor-pointer opacity-60 hover:opacity-100 transition-opacity">
          <div class="w-10 h-10 rounded-full flex items-center justify-center">
            <Icon icon="solar:chat-round-dots-bold-duotone" class="text-xl text-gray-400" />
          </div>
          <span class="text-[10px] mt-1 text-gray-400">语伴</span>
        </div>
        
        <div class="flex flex-col items-center flex-1 py-2 cursor-pointer opacity-60 hover:opacity-100 transition-opacity">
          <div class="w-10 h-10 rounded-full flex items-center justify-center">
            <Icon icon="solar:user-bold" class="text-xl text-gray-400" />
          </div>
          <span class="text-[10px] mt-1 text-gray-400">我的</span>
        </div>
      </nav>

      <div class="absolute bottom-2 left-1/2 -translate-x-1/2 w-32 h-1 bg-gray-900/20 rounded-full z-50"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { apiService } from '@/services/api'

interface FamilyMemoryItem {
  id: string
  familyId: string
  title: string
  type: 'text' | 'image' | 'video'
  description?: string
  content?: string
  eventDate?: string
  location?: string
  mediaUrl?: string
  mediaType?: string
  tags?: string[]
  createdAt: string
  updatedAt: string
}

interface AvatarItem {
  id: string
  name: string
  relationship: string
  gender: 'male' | 'female'
  birthYear?: string
  deathYear?: string
  status: 'active' | 'training' | 'generating' | 'inactive' | 'failed' | 'retry_pending' | 'pending'
  progress: number
  avatar?: string
  chatCount?: number
}

const familyMemories = ref<FamilyMemoryItem[]>([])
const memberCount = ref(0)
const galleryCount = ref(0)
const avatarCount = ref(0)
const avatars = ref<AvatarItem[]>([])

const noisePatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22 opacity=%220.3%22/%3E%3C/svg%3E")`
}))

const dotPatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23ffffff%22 fill-opacity=%220.4%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
}))

const getMemoryTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    text: 'bg-[#8B6F4E]',
    image: 'bg-[#D4A574]',
    video: 'bg-emerald-500'
  }
  return colors[type] || colors.text
}

const getMemoryTypeBgColor = (type: string) => {
  const colors: Record<string, string> = {
    text: 'bg-[#E8D5C4]',
    image: 'bg-[#F5E6D3]',
    video: 'bg-emerald-50'
  }
  return colors[type] || colors.text
}

const getMemoryTypeIcon = (type: string) => {
  const icons: Record<string, string> = {
    text: 'solar:note-book-bold',
    image: 'solar:gallery-wide-bold',
    video: 'solar:video-camera-bold'
  }
  return icons[type] || icons.text
}

const getMemoryTypeIconColor = (type: string) => {
  const colors: Record<string, string> = {
    text: 'text-[#8B6F4E]',
    image: 'text-[#D4A574]',
    video: 'text-emerald-600'
  }
  return colors[type] || colors.text
}

const getMemoryTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    text: '文字记忆',
    image: '照片记忆',
    video: '视频记忆'
  }
  return labels[type] || '文字记忆'
}

const getFullMediaUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) {
    return url
  }
  return `http://localhost:8000${url}`
}

const formatMemoryDate = (dateStr: string) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const now = new Date()
    const diffTime = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return '今天'
    if (diffDays === 1) return '昨天'
    if (diffDays < 7) return `${diffDays}天前`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}个月前`
    
    return `${date.getFullYear()}年${date.getMonth() + 1}月`
  } catch {
    return dateStr
  }
}

const loadHomeStats = async () => {
  try {
    const response = await apiService.getHomeStats()
    if (response.success && response.data) {
      memberCount.value = response.data.memberCount
      galleryCount.value = response.data.galleryCount
      avatarCount.value = response.data.avatarCount
    }
  } catch (error) {
    console.error('加载首页统计数据失败:', error)
  }
}

const loadAvatars = async () => {
  try {
    const response = await apiService.getAvatars()
    if (response.success && response.data) {
      avatars.value = response.data.avatars
    }
  } catch (error) {
    console.error('加载数字家人失败:', error)
  }
}

const loadFamilyMemories = async () => {
  try {
    const response = await apiService.getFamilyMemories()
    if (response.success && response.data) {
      familyMemories.value = response.data.memories.sort((a, b) => {
        const dateA = a.eventDate || a.createdAt
        const dateB = b.eventDate || b.createdAt
        return new Date(dateB).getTime() - new Date(dateA).getTime()
      })
    }
  } catch (error) {
    console.error('加载家族记忆失败:', error)
  }
}

onMounted(() => {
  loadHomeStats()
  loadAvatars()
  loadFamilyMemories()
})
</script>
