<template>
  <div class="min-h-screen paper-texture">
    <div class="max-w-7xl mx-auto px-6 py-6">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center space-x-4">
          <button 
            @click="showAvatarSelector = true"
            class="flex items-center space-x-3 px-4 py-2 bg-white rounded-lg shadow-sm hover:shadow-md transition-all border border-[#E8D5C4]"
          >
            <div class="w-10 h-10 rounded-full overflow-hidden bg-gray-200">
              <img v-if="currentAvatar?.avatar" :src="currentAvatar.avatar" class="w-full h-full object-cover" alt="">
              <Icon v-else icon="solar:user-rounded-bold" class="w-full h-full text-gray-400" />
            </div>
            <div class="text-left">
              <h2 class="text-lg font-bold text-[#5C4A3A] font-serif">{{ currentAvatar?.name || '语伴' }}</h2>
              <p class="text-xs text-gray-500">{{ currentAvatar?.relationship || '数字家人' }}</p>
            </div>
            <Icon icon="solar:alt-arrow-down-bold" class="text-[#8B6F4E] text-sm" />
          </button>
        </div>
        <div class="flex items-center space-x-2 text-sm text-gray-500">
          <div v-if="isSpeaking" class="flex items-center space-x-1 px-3 py-1 bg-green-50 text-green-600 rounded-full">
            <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>语音播报中</span>
          </div>
          <div v-else-if="isRecording" class="flex items-center space-x-1 px-3 py-1 bg-red-50 text-red-600 rounded-full animate-pulse">
            <div class="w-2 h-2 bg-red-500 rounded-full"></div>
            <span>录音中</span>
          </div>
          <div v-else-if="currentAvatar?.status === 'active'" class="flex items-center space-x-1 px-3 py-1 bg-[#E8D5C4] text-[#8B6F4E] rounded-full">
            <div class="w-2 h-2 bg-[#8B6F4E] rounded-full"></div>
            <span>已激活</span>
          </div>
        </div>
      </div>

      <div class="flex flex-col lg:flex-row overflow-hidden rounded-2xl border border-[#E8D5C4] shadow-soft bg-white">
        <div class="lg:w-1/2 h-[40vh] lg:h-[calc(100vh-280px)] relative bg-gradient-to-b from-[#FAF7F2] to-[#E8D5C4]/30">
          <div class="absolute inset-0 flex items-center justify-center">
            <ThreeDModelViewer 
              :key="currentAvatar?.id"
              :modelUrl="currentAvatar?.modelUrl"
              :autoRotate="!isSpeaking"
              fullHeight
            />
          </div>

          <div v-if="isSpeaking" class="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center space-x-1">
            <div v-for="i in 5" :key="i" 
                 class="w-1.5 bg-[#8B6F4E] rounded-full animate-speak-wave"
                 :style="{
                   height: speakWaveHeights[i - 1] + 'px',
                   animationDelay: (i * 0.1) + 's'
                 }">
            </div>
          </div>
        </div>

        <div class="lg:w-1/2 flex flex-col h-[60vh] lg:h-[calc(100vh-280px)] bg-white border-l border-[#E8D5C4]">
          <div class="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar" ref="messagesContainer">
            <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center">
              <div class="w-20 h-20 rounded-full bg-[#E8D5C4] flex items-center justify-center mb-4">
                <Icon icon="solar:chat-round-dots-bold" class="text-4xl text-[#8B6F4E]" />
              </div>
              <h3 class="text-lg font-semibold text-[#5C4A3A] mb-2">开始与{{ currentAvatar?.name || '数字家人' }}对话</h3>
              <p class="text-sm text-gray-500 max-w-xs">
                您可以通过文字或语音与数字家人交流。点击麦克风按钮开始语音对话，或直接在输入框中打字。
              </p>
            </div>

            <div v-for="(message, index) in messages" :key="index"
                 class="flex"
                 :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
              <div v-if="message.role === 'assistant'" class="w-8 h-8 rounded-full overflow-hidden bg-gray-200 mr-3 flex-shrink-0">
                <img v-if="currentAvatar?.avatar" :src="currentAvatar.avatar" class="w-full h-full object-cover" alt="">
                <Icon v-else icon="solar:user-rounded-bold" class="w-full h-full text-gray-400" />
              </div>

              <div class="max-w-[80%]"
                   :class="message.role === 'user' ? 'order-2' : 'order-1'">
                <div class="rounded-2xl px-4 py-3"
                     :class="message.role === 'user' 
                       ? 'bg-[#8B6F4E] text-white rounded-tr-sm' 
                       : 'bg-[#FAF7F2] text-gray-800 rounded-tl-sm border border-[#E8D5C4]'">
                  <p class="text-sm leading-relaxed" v-text="message.content"></p>
                </div>
                <div class="flex items-center mt-1 space-x-2"
                     :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
                  <span class="text-xs text-gray-400">{{ formatTime(message.timestamp) }}</span>
                  
                  <template v-if="message.role === 'assistant'">
                    <button v-if="message.isPlaying" @click="pauseAudio(message)"
                            class="text-xs text-[#8B6F4E] flex items-center space-x-1 hover:underline">
                      <Icon icon="solar:pause-circle-outline" />
                      <span>暂停</span>
                    </button>
                    <button v-else-if="message.audioReady && !message.isPlaying" @click="playAudio(message)"
                            class="text-xs text-[#8B6F4E] flex items-center space-x-1 hover:underline">
                      <Icon icon="solar:play-circle-outline" />
                      <span>播放</span>
                    </button>
                    <span v-else-if="message.isGeneratingAudio" 
                          class="text-xs text-gray-400 flex items-center space-x-1">
                      <Icon icon="solar:loading-outline" class="animate-spin" />
                      <span>语音生成中</span>
                    </span>
                  </template>
                </div>
              </div>

              <div v-if="message.role === 'user'" class="w-8 h-8 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] p-0.5 ml-3 flex-shrink-0">
                <div class="w-full h-full rounded-full overflow-hidden bg-gray-200">
                  <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face" 
                       class="w-full h-full object-cover" alt="用户头像">
                </div>
              </div>
            </div>

            <div v-if="isTyping" class="flex justify-start">
              <div class="w-8 h-8 rounded-full overflow-hidden bg-gray-200 mr-3 flex-shrink-0">
                <img v-if="currentAvatar?.avatar" :src="currentAvatar.avatar" class="w-full h-full object-cover" alt="">
                <Icon v-else icon="solar:user-rounded-bold" class="w-full h-full text-gray-400" />
              </div>
              <div class="bg-[#FAF7F2] border border-[#E8D5C4] rounded-2xl rounded-tl-sm px-4 py-3">
                <div class="flex space-x-1">
                  <div class="w-2 h-2 bg-[#8B6F4E] rounded-full animate-bounce"></div>
                  <div class="w-2 h-2 bg-[#8B6F4E] rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                  <div class="w-2 h-2 bg-[#8B6F4E] rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="showVoiceSettings" class="border-t border-[#E8D5C4] bg-[#FAF7F2] p-4">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-sm font-semibold text-[#5C4A3A]">语音设置</h4>
              <button @click="showVoiceSettings = false" class="text-gray-400 hover:text-gray-600">
                <Icon icon="solar:close-circle-bold" />
              </button>
            </div>
            
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">语音免打扰</span>
                <button @click="isDoNotDisturb = !isDoNotDisturb"
                        class="relative w-12 h-6 rounded-full transition-colors"
                        :class="isDoNotDisturb ? 'bg-[#8B6F4E]' : 'bg-gray-300'">
                  <div class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                       :class="isDoNotDisturb ? 'translate-x-6' : 'translate-x-0'">
                  </div>
                </button>
              </div>

              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-600">静音</span>
                <button @click="isMuted = !isMuted"
                        class="relative w-12 h-6 rounded-full transition-colors"
                        :class="isMuted ? 'bg-[#8B6F4E]' : 'bg-gray-300'">
                  <div class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
                       :class="isMuted ? 'translate-x-6' : 'translate-x-0'">
                  </div>
                </button>
              </div>

              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm text-gray-600">音量</span>
                  <span class="text-sm text-[#8B6F4E]">{{ volume }}%</span>
                </div>
                <input type="range" min="0" max="100" v-model="volume" 
                       class="w-full h-2 bg-[#E8D5C4] rounded-full appearance-none cursor-pointer accent-[#8B6F4E]" />
              </div>

              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm text-gray-600">语速</span>
                  <span class="text-sm text-[#8B6F4E]">{{ speechRate }}x</span>
                </div>
                <input type="range" min="0.5" max="2" step="0.1" v-model="speechRate" 
                       class="w-full h-2 bg-[#E8D5C4] rounded-full appearance-none cursor-pointer accent-[#8B6F4E]" />
              </div>
            </div>
          </div>

          <div class="border-t border-[#E8D5C4] bg-white p-4">
            <div class="flex items-end space-x-3">
              <button 
                @click="toggleVoiceInput"
                class="w-12 h-12 rounded-full flex items-center justify-center transition-all"
                :class="isRecording 
                  ? 'bg-red-500 text-white animate-pulse' 
                  : 'bg-[#E8D5C4] text-[#8B6F4E] hover:bg-[#D4A574]'">
                <Icon :icon="isRecording ? 'solar:microphone-off-bold' : 'solar:microphone-bold'" class="text-xl" />
              </button>

              <div class="flex-1 relative">
                <textarea 
                  v-model="inputText"
                  @keydown.enter.exact.prevent="sendMessage"
                  placeholder="输入您想说的话..."
                  rows="1"
                  class="w-full px-4 py-3 bg-[#FAF7F2] border border-[#E8D5C4] rounded-2xl resize-none focus:outline-none focus:border-[#8B6F4E] focus:ring-2 focus:ring-[#8B6F4E]/20 text-gray-700"
                ></textarea>
              </div>

              <button 
                @click="sendMessage"
                :disabled="!inputText.trim() && !isRecording"
                class="w-12 h-12 rounded-full flex items-center justify-center transition-all"
                :class="inputText.trim() 
                  ? 'bg-[#8B6F4E] text-white hover:bg-[#6B5342]' 
                  : 'bg-gray-200 text-gray-400 cursor-not-allowed'">
                <Icon icon="solar:paper-plane-bold" class="text-xl" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAvatarSelector" class="fixed inset-0 z-50 flex items-end lg:items-center justify-center">
      <div class="absolute inset-0 bg-black/50" @click="showAvatarSelector = false"></div>
      <div class="relative w-full max-w-lg bg-white rounded-t-3xl lg:rounded-3xl max-h-[80vh] overflow-hidden">
        <div class="sticky top-0 bg-white border-b border-[#E8D5C4] px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold text-[#5C4A3A]">选择数字家人</h3>
            <button @click="showAvatarSelector = false" class="text-gray-400 hover:text-gray-600">
              <Icon icon="solar:close-circle-bold" class="text-2xl" />
            </button>
          </div>
        </div>
        
        <div class="p-6 overflow-y-auto max-h-[60vh]">
          <div v-if="loadingAvatars" class="flex items-center justify-center py-8">
            <Icon icon="solar:loading-outline" class="text-3xl text-[#8B6F4E] animate-spin" />
          </div>
          
          <div v-else-if="availableAvatars.length === 0" class="text-center py-8">
            <Icon icon="solar:user-outline" class="text-5xl text-gray-300 mx-auto mb-3" />
            <p class="text-gray-500">暂无可用的数字家人</p>
            <p class="text-sm text-gray-400 mt-2">请先在「生境」页面创建数字人形象</p>
          </div>
          
          <div v-else class="space-y-3">
            <div v-for="avatar in availableAvatars" :key="avatar.id"
                 @click="selectAvatar(avatar)"
                 class="flex items-center space-x-4 p-4 rounded-2xl cursor-pointer transition-all hover:bg-[#FAF7F2]"
                 :class="currentAvatar?.id === avatar.id ? 'bg-[#FAF7F2] border-2 border-[#8B6F4E]' : 'border border-[#E8D5C4]'">
              <div class="w-14 h-14 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] p-0.5 flex-shrink-0">
                <div class="w-full h-full rounded-full bg-gray-200 overflow-hidden">
                  <img v-if="avatar.avatar" :src="avatar.avatar" class="w-full h-full object-cover" :alt="avatar.name">
                  <Icon v-else icon="solar:user-rounded-bold" class="w-full h-full text-gray-400" />
                </div>
              </div>
              
              <div class="flex-1 min-w-0">
                <div class="flex items-center space-x-2">
                  <h4 class="font-semibold text-gray-800 truncate">{{ avatar.name }}</h4>
                  <span class="px-2 py-0.5 text-[10px] rounded-full"
                        :class="avatar.status === 'active' 
                          ? 'bg-[#E8D5C4] text-[#8B6F4E]' 
                          : 'bg-gray-100 text-gray-500'">
                    {{ avatar.status === 'active' ? '已激活' : '训练中' }}
                  </span>
                </div>
                <p class="text-sm text-gray-500 mt-1">{{ avatar.relationship }} · {{ avatar.birthYear }}-{{ avatar.deathYear || '在世' }}</p>
                
                <div v-if="avatar.voiceEnabled" class="flex items-center mt-2 text-xs text-[#8B6F4E]">
                  <Icon icon="solar:volume-high-bold-duotone" class="mr-1" />
                  <span>专属声线已配置</span>
                </div>
              </div>
              
              <div v-if="currentAvatar?.id === avatar.id" class="flex-shrink-0">
                <Icon icon="solar:check-circle-bold" class="text-[#8B6F4E] text-2xl" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { apiService, type Avatar } from '../services/api'
import ThreeDModelViewer from './ThreeDModelViewer.vue'

const router = useRouter()

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  isPlaying?: boolean
  audioReady?: boolean
  isGeneratingAudio?: boolean
  audioUrl?: string
}

const currentAvatar = ref<Avatar | null>(null)
const availableAvatars = ref<Avatar[]>([])
const loadingAvatars = ref(false)
const showAvatarSelector = ref(false)
const showVoiceSettings = ref(false)

const inputText = ref('')
const messages = ref<ChatMessage[]>([])
const isTyping = ref(false)
const messagesContainer = ref<HTMLDivElement | null>(null)

const isRecording = ref(false)
const isSpeaking = ref(false)
const speakWaveHeights = computed(() => {
  if (!isSpeaking.value) return [8, 8, 8, 8, 8]
  return Array.from({ length: 5 }, () => 10 + Math.random() * 20)
})

const isDoNotDisturb = ref(false)
const isMuted = ref(false)
const volume = ref(80)
const speechRate = ref(1.0)

let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let currentAudio: HTMLAudioElement | null = null
let speechRecognition: any = null

const formatTime = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

watch(messages, () => {
  scrollToBottom()
}, { deep: true })

const loadAvatars = async () => {
  loadingAvatars.value = true
  try {
    const result = await apiService.getAvatars()
    if (result.success && result.data && result.data.avatars.length > 0) {
      availableAvatars.value = result.data.avatars
      const activeAvatars = availableAvatars.value.filter(a => a.status === 'active')
      if (activeAvatars.length > 0 && !currentAvatar.value) {
        currentAvatar.value = activeAvatars[0]
      }
    } else {
      availableAvatars.value = [
        {
          id: 'demo-1',
          name: '张爷爷',
          gender: 'male',
          relationship: '祖父',
          birthYear: '1938',
          deathYear: '2020',
          status: 'active',
          avatar: 'https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=200&h=200&fit=crop&crop=face',
          description: '一位慈祥的老人，总是面带微笑，喜欢讲年轻时的故事',
          voiceEnabled: true,
          modelUrl: undefined,
          modelConfig: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        },
        {
          id: 'demo-2',
          name: '李奶奶',
          gender: 'female',
          relationship: '祖母',
          birthYear: '1942',
          deathYear: '2018',
          status: 'active',
          avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&h=200&fit=crop&crop=face',
          description: '温柔善良的祖母，擅长做家常菜，喜欢种花养草',
          voiceEnabled: true,
          modelUrl: undefined,
          modelConfig: undefined,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      ]
      currentAvatar.value = availableAvatars.value[0]
    }
  } catch (error) {
    console.error('加载数字人列表失败:', error)
    availableAvatars.value = [
      {
        id: 'demo-1',
        name: '张爷爷',
        gender: 'male',
        relationship: '祖父',
        birthYear: '1938',
        deathYear: '2020',
        status: 'active',
        avatar: 'https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=200&h=200&fit=crop&crop=face',
        description: '一位慈祥的老人，总是面带微笑，喜欢讲年轻时的故事',
        voiceEnabled: true,
        modelUrl: undefined,
        modelConfig: undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 'demo-2',
        name: '李奶奶',
        gender: 'female',
        relationship: '祖母',
        birthYear: '1942',
        deathYear: '2018',
        status: 'active',
        avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200&h=200&fit=crop&crop=face',
        description: '温柔善良的祖母，擅长做家常菜，喜欢种花养草',
        voiceEnabled: true,
        modelUrl: undefined,
        modelConfig: undefined,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]
    currentAvatar.value = availableAvatars.value[0]
  } finally {
    loadingAvatars.value = false
  }
}

const selectAvatar = (avatar: Avatar) => {
  if (avatar.status !== 'active') return
  currentAvatar.value = avatar
  showAvatarSelector.value = false
  messages.value = []
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text) return

  const userMessage: ChatMessage = {
    role: 'user',
    content: text,
    timestamp: new Date()
  }
  messages.value.push(userMessage)
  inputText.value = ''

  isTyping.value = true

  try {
    const response = await simulateAIResponse(text)
    
    isTyping.value = false
    
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: response,
      timestamp: new Date(),
      audioReady: false,
      isGeneratingAudio: !isMuted.value && !isDoNotDisturb.value
    }
    messages.value.push(assistantMessage)

    if (!isMuted.value && !isDoNotDisturb.value) {
      await generateAndPlayAudio(assistantMessage)
    }
  } catch (error) {
    isTyping.value = false
    console.error('发送消息失败:', error)
  }
}

const simulateAIResponse = async (userMessage: string): Promise<string> => {
  await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000))

  const avatarName = currentAvatar.value?.name || '数字家人'
  const relationship = currentAvatar.value?.relationship || '亲人'

  const responses = [
    `孩子，你说的这件事让我想起了很多过去的时光。记得你小时候总是追着问这问那，现在你都长大了，有了自己的思考方式。我很高兴能在这里陪你聊聊。`,
    `嗯，这个问题问得好。其实人生中有很多事情，当时觉得过不去，现在回头看也不过如此。你要记住，无论遇到什么困难，都要有一颗平静的心。`,
    `听到你说这些，我心里很欣慰。你一直都是个懂事的孩子，知道体谅他人，也知道珍惜眼前人。继续保持这份真诚，生活会回报你的。`,
    `这个话题让我想起了很多往事。那时候的生活虽然艰苦，但大家都很知足。现在条件好了，更要懂得感恩，珍惜身边的人。`,
    `孩子，你有什么心事都可以跟我说。虽然我已经不在你身边，但我的心一直牵挂着你。无论发生什么，都要记住：家人永远是你最坚强的后盾。`,
    `${avatarName}想跟你说，无论什么时候，都要好好照顾自己。记得你小时候最喜欢听我讲${relationship}的故事了，现在你想听什么，我都可以跟你聊聊。`,
    `孩子啊，时间过得真快。记得你上次问起这个问题的时候，还是个小孩子。现在你长大了，有自己的想法了，真好。你想知道什么，尽管问吧。`,
    `说起这个，我想起了很多${relationship}的故事。那时候大家的生活虽然简单，但都很快乐。你想听听那时候的事情吗？`
  ]

  return responses[Math.floor(Math.random() * responses.length)]
}

const generateAndPlayAudio = async (message: ChatMessage) => {
  if (!currentAvatar.value) return

  try {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(message.content)
      utterance.lang = 'zh-CN'
      utterance.rate = speechRate.value
      utterance.volume = volume.value / 100

      utterance.onstart = () => {
        isSpeaking.value = true
        message.isPlaying = true
      }
      utterance.onend = () => {
        isSpeaking.value = false
        message.isPlaying = false
        message.audioReady = true
      }
      utterance.onerror = () => {
        isSpeaking.value = false
        message.isPlaying = false
        message.isGeneratingAudio = false
      }

      speechSynthesis.speak(utterance)
      message.isGeneratingAudio = false
    }
  } catch (error) {
    console.error('语音合成失败:', error)
    message.isGeneratingAudio = false
  }
}

const playAudio = (message: ChatMessage) => {
  if (!message.content) return
  
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel()
    
    const utterance = new SpeechSynthesisUtterance(message.content)
    utterance.lang = 'zh-CN'
    utterance.rate = speechRate.value
    utterance.volume = volume.value / 100

    utterance.onstart = () => {
      isSpeaking.value = true
      message.isPlaying = true
    }
    utterance.onend = () => {
      isSpeaking.value = false
      message.isPlaying = false
    }

    speechSynthesis.speak(utterance)
  }
}

const pauseAudio = (message: ChatMessage) => {
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel()
    isSpeaking.value = false
    message.isPlaying = false
  }
}

const toggleVoiceInput = async () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = async () => {
  try {
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      speechRecognition = new SpeechRecognition()
      speechRecognition.lang = 'zh-CN'
      speechRecognition.continuous = false
      speechRecognition.interimResults = false

      speechRecognition.onstart = () => {
        isRecording.value = true
      }

      speechRecognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        inputText.value = transcript
        isRecording.value = false
      }

      speechRecognition.onerror = () => {
        isRecording.value = false
      }

      speechRecognition.onend = () => {
        isRecording.value = false
      }

      speechRecognition.start()
    } else {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder = new MediaRecorder(stream)
      audioChunks = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data)
      }

      mediaRecorder.onstop = () => {
        isRecording.value = false
        inputText.value = '[语音消息]'
      }

      mediaRecorder.start()
      isRecording.value = true
    }
  } catch (error) {
    console.error('无法访问麦克风:', error)
  }
}

const stopRecording = () => {
  if (speechRecognition) {
    speechRecognition.stop()
  }
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    mediaRecorder.stream.getTracks().forEach(track => track.stop())
  }
}

onMounted(() => {
  loadAvatars()
})

onUnmounted(() => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  if ('speechSynthesis' in window) {
    speechSynthesis.cancel()
  }
})
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

@keyframes speak-wave {
  0%, 100% {
    height: 8px;
  }
  50% {
    height: 28px;
  }
}

.animate-speak-wave {
  animation: speak-wave 0.5s ease-in-out infinite;
}

textarea::-webkit-scrollbar {
  display: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #8B6F4E;
  border-radius: 50%;
  cursor: pointer;
}
</style>
