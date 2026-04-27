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
            <h1 class="text-2xl font-bold text-[#5C4A3A] font-serif tracking-wider">
              {{ isEdit ? '编辑记忆' : '创建记忆' }}
            </h1>
            <p class="text-xs text-gray-500 tracking-[0.15em] uppercase font-medium">Memory Editor</p>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <button @click="saveMemory" :disabled="!canSave" 
                  class="px-6 py-2.5 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2">
            <Icon icon="material-symbols:check" class="text-lg" />
            <span>保存</span>
          </button>
        </div>
      </div>
    </header>

    <div class="max-w-5xl mx-auto px-6 py-8">
      <section class="space-y-6">
        <div v-if="!isEdit" class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif mb-4">选择创建方式</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <button 
              @click="createMode = 'upload'"
              :class="[
                'p-6 rounded-2xl border-2 transition-all cursor-pointer',
                createMode === 'upload' 
                  ? 'bg-[#FAF7F2] border-[#8B6F4E] shadow-md' 
                  : 'bg-white border-[#E8D5C4] hover:border-[#D4A574]'
              ]"
            >
              <div class="flex items-start space-x-4">
                <div :class="[
                  'w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0',
                  createMode === 'upload' ? 'bg-[#8B6F4E]' : 'bg-[#E8D5C4]'
                ]">
                  <Icon 
                    icon="material-symbols:cloud-upload-outline" 
                    :class="[
                      'text-3xl',
                      createMode === 'upload' ? 'text-white' : 'text-[#8B6F4E]'
                    ]"
                  />
                </div>
                <div class="text-left">
                  <h4 :class="[
                    'font-bold text-lg mb-1',
                    createMode === 'upload' ? 'text-[#8B6F4E]' : 'text-gray-700'
                  ]">上传记忆</h4>
                  <p class="text-sm text-gray-500">上传已有的图片或视频文件，作为记忆存储</p>
                </div>
              </div>
            </button>

            <button 
              @click="createMode = 'richtext'"
              :class="[
                'p-6 rounded-2xl border-2 transition-all cursor-pointer',
                createMode === 'richtext' 
                  ? 'bg-[#FAF7F2] border-[#8B6F4E] shadow-md' 
                  : 'bg-white border-[#E8D5C4] hover:border-[#D4A574]'
              ]"
            >
              <div class="flex items-start space-x-4">
                <div :class="[
                  'w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0',
                  createMode === 'richtext' ? 'bg-[#8B6F4E]' : 'bg-[#E8D5C4]'
                ]">
                  <Icon 
                    icon="material-symbols:edit-document-outline" 
                    :class="[
                      'text-3xl',
                      createMode === 'richtext' ? 'text-white' : 'text-[#8B6F4E]'
                    ]"
                  />
                </div>
                <div class="text-left">
                  <h4 :class="[
                    'font-bold text-lg mb-1',
                    createMode === 'richtext' ? 'text-[#8B6F4E]' : 'text-gray-700'
                  ]">在线创建记忆</h4>
                  <p class="text-sm text-gray-500">使用富文本编辑器，可同时插入文字、图片、视频</p>
                </div>
              </div>
            </button>
          </div>
        </div>

        <div class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif mb-4">基本信息</h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-2">关联数字人 <span class="text-red-500">*</span></label>
              <select v-model="form.avatarId" 
                      class="w-full px-4 py-3 bg-[#FAF7F2] rounded-xl border border-[#E8D5C4] text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30 transition-all">
                <option value="">请选择关联的数字人</option>
                <option v-for="avatar in avatars" :key="avatar.id" :value="avatar.id">
                  {{ avatar.name }} ({{ avatar.relationship }})
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-[#5C4A3A] mb-2">记忆标题 <span class="text-red-500">*</span></label>
              <input 
                v-model="form.title" 
                type="text" 
                placeholder="请输入记忆标题"
                class="w-full px-4 py-3 bg-[#FAF7F2] rounded-xl border border-[#E8D5C4] text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30 transition-all"
              />
            </div>
          </div>

          <div class="mt-6">
            <label class="block text-sm font-medium text-[#5C4A3A] mb-2">记忆描述</label>
            <textarea 
              v-model="form.description" 
              placeholder="请输入记忆描述（可选）"
              rows="2"
              class="w-full px-4 py-3 bg-[#FAF7F2] rounded-xl border border-[#E8D5C4] text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30 resize-none transition-all"
            ></textarea>
          </div>
        </div>

        <div v-if="createMode === 'upload'" class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif mb-4">上传文件</h3>
          <p class="text-sm text-gray-500 mb-4">支持上传图片、视频、文档（Word、PDF、PPT 等）多种类型的文件</p>
          
          <div v-if="uploadedFile">
            <div class="border-2 border-[#E8D5C4] rounded-2xl p-6 bg-[#FAF7F2]">
              <div class="flex items-start space-x-4">
                <div :class="[
                  'w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0',
                  uploadedFileCategory === 'image' ? 'bg-blue-50' :
                  uploadedFileCategory === 'video' ? 'bg-red-50' :
                  'bg-amber-50'
                ]">
                  <Icon 
                    :icon="getUploadedFileIcon()" 
                    :class="[
                      'text-3xl',
                      uploadedFileCategory === 'image' ? 'text-blue-500' :
                      uploadedFileCategory === 'video' ? 'text-red-500' :
                      'text-amber-600'
                    ]"
                  />
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="font-bold text-gray-800 truncate">{{ uploadedFile.name }}</h4>
                  <p class="text-sm text-gray-500 mt-1">
                    {{ formatFileSize(uploadedFile.size) }} · {{ getUploadedFileTypeLabel() }}
                  </p>
                  <p class="text-xs text-gray-400 mt-1">
                    上传时间：{{ new Date().toLocaleString('zh-CN') }}
                  </p>
                </div>
                <button 
                  @click="clearUploadedFile" 
                  class="w-8 h-8 rounded-full hover:bg-gray-200 flex items-center justify-center transition-colors"
                >
                  <Icon icon="material-symbols:close" class="text-gray-500" />
                </button>
              </div>
              
              <div v-if="uploadedFileCategory === 'image' && imagePreview" class="mt-6 relative rounded-xl overflow-hidden shadow-md">
                <img :src="imagePreview" class="w-full max-h-80 object-contain bg-gray-100" alt="预览" />
              </div>
              
              <div v-else-if="uploadedFileCategory === 'video' && videoPreview" class="mt-6 relative rounded-xl overflow-hidden shadow-md bg-black">
                <video :src="videoPreview" class="w-full max-h-80" controls></video>
              </div>
              
              <div v-else-if="uploadedFileCategory === 'document'" class="mt-6 text-center py-8 bg-white rounded-xl border border-dashed border-[#E8D5C4]">
                <Icon icon="material-symbols:description-outline" class="text-5xl text-gray-300 mx-auto mb-3" />
                <p class="text-sm text-gray-500">文档预览不可用</p>
                <p class="text-xs text-gray-400 mt-1">下载后可使用相应软件打开查看</p>
              </div>
            </div>
          </div>
          
          <div v-else class="border-2 border-dashed border-[#E8D5C4] rounded-2xl p-12 text-center hover:border-[#D4A574] transition-colors cursor-pointer" @click="triggerFileUpload">
            <Icon icon="material-symbols:cloud-upload-outline" class="text-6xl text-gray-300 mx-auto mb-4" />
            <p class="text-lg text-gray-500 mb-2">点击上传或拖拽文件到此处</p>
            <p class="text-sm text-gray-400">支持 PDF、Word、PPT、Excel、图片、视频 等多种格式</p>
          </div>
          
          <input 
            ref="fileInput" 
            type="file" 
            @change="handleFileUpload"
            class="hidden"
          />
          
          <button 
            @click="triggerFileUpload" 
            class="w-full mt-4 py-3 bg-[#E8D5C4] text-[#8B6F4E] rounded-xl font-medium hover:bg-[#D4A574] transition-colors flex items-center justify-center space-x-2"
          >
            <Icon icon="material-symbols:upload" class="text-lg" />
            <span>选择文件</span>
          </button>
        </div>

        <div v-if="createMode === 'richtext'" class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif mb-4">富文本编辑</h3>
          <p class="text-sm text-gray-500 mb-4">在此编辑器中，您可以同时编辑文字、插入图片和视频</p>
          
          <div class="border border-[#E8D5C4] rounded-xl overflow-hidden">
            <div class="px-4 py-3 border-b border-[#E8D5C4] bg-[#FAF7F2] flex flex-wrap items-center gap-2">
              <div class="flex items-center space-x-1 border-r border-[#E8D5C4] pr-2">
                <button @click="formatText('bold')" class="p-2 rounded-lg hover:bg-white transition-colors" title="加粗">
                  <Icon icon="material-symbols:format-bold" class="text-gray-600" />
                </button>
                <button @click="formatText('italic')" class="p-2 rounded-lg hover:bg-white transition-colors" title="斜体">
                  <Icon icon="material-symbols:format-italic" class="text-gray-600" />
                </button>
                <button @click="formatText('underline')" class="p-2 rounded-lg hover:bg-white transition-colors" title="下划线">
                  <Icon icon="material-symbols:format-underline" class="text-gray-600" />
                </button>
              </div>
              
              <div class="flex items-center space-x-1 border-r border-[#E8D5C4] pr-2">
                <button @click="formatText('insertUnorderedList')" class="p-2 rounded-lg hover:bg-white transition-colors" title="无序列表">
                  <Icon icon="material-symbols:format-list-bulleted" class="text-gray-600" />
                </button>
                <button @click="formatText('insertOrderedList')" class="p-2 rounded-lg hover:bg-white transition-colors" title="有序列表">
                  <Icon icon="material-symbols:format-list-numbered" class="text-gray-600" />
                </button>
              </div>

              <div class="flex items-center space-x-1 border-r border-[#E8D5C4] pr-2">
                <select @change="formatHeading($event)" class="p-2 rounded-lg bg-white border border-[#E8D5C4] text-gray-600 text-sm focus:outline-none">
                  <option value="">标题</option>
                  <option value="h1">标题 1</option>
                  <option value="h2">标题 2</option>
                  <option value="h3">标题 3</option>
                  <option value="p">正文</option>
                </select>
              </div>

              <div class="flex items-center space-x-1">
                <button @click="insertImageFromFile" class="p-2 rounded-lg hover:bg-white transition-colors flex items-center space-x-1" title="插入图片">
                  <Icon icon="material-symbols:image-outline" class="text-gray-600" />
                  <span class="text-sm text-gray-600 hidden sm:inline">插入图片</span>
                </button>
                <button @click="insertVideoFromFile" class="p-2 rounded-lg hover:bg-white transition-colors flex items-center space-x-1" title="插入视频">
                  <Icon icon="material-symbols:videocam-outline" class="text-gray-600" />
                  <span class="text-sm text-gray-600 hidden sm:inline">插入视频</span>
                </button>
              </div>

              <input 
                ref="richTextImageInput" 
                type="file" 
                accept="image/*" 
                @change="handleRichTextImageInsert"
                class="hidden"
              />
              <input 
                ref="richTextVideoInput" 
                type="file" 
                accept="video/*" 
                @change="handleRichTextVideoInsert"
                class="hidden"
              />
            </div>

            <div 
              ref="richTextEditor"
              contenteditable="true"
              @input="handleRichTextInput"
              @blur="handleRichTextBlur"
              class="min-h-[400px] p-6 focus:outline-none prose prose-sm max-w-none"
              placeholder="开始编辑您的记忆..."
            ></div>
          </div>

          <div class="mt-4 flex items-center justify-between text-sm text-gray-500">
            <span>提示：点击工具栏中的按钮可以插入图片或视频</span>
            <span>{{ richTextCharacterCount }} 字符</span>
          </div>
        </div>

        <div class="bg-white rounded-2xl p-6 shadow-soft border border-stone-100">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif mb-4">标签（可选）</h3>
          <div class="flex flex-wrap gap-2 mb-4">
            <span 
              v-for="(tag, index) in form.tags" 
              :key="index"
              class="inline-flex items-center px-4 py-2 bg-[#F5E6D3] text-[#8B6F4E] rounded-full font-medium"
            >
              {{ tag }}
              <button @click="removeTag(index)" class="ml-2 hover:text-[#6B5342] transition-colors">
                <Icon icon="material-symbols:close" class="text-sm" />
              </button>
            </span>
          </div>
          <div class="flex space-x-3">
            <input 
              v-model="newTag" 
              @keyup.enter="addTag"
              type="text" 
              placeholder="输入标签后按回车添加"
              class="flex-1 px-4 py-3 bg-[#FAF7F2] rounded-xl border border-[#E8D5C4] text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#8B6F4E]/30 transition-all"
            />
            <button 
              @click="addTag" 
              class="px-6 py-3 bg-[#8B6F4E] text-white rounded-xl font-medium hover:bg-[#6B5342] transition-colors"
            >
              添加
            </button>
          </div>
        </div>

        <div v-if="isEdit" class="flex justify-end">
          <button 
            @click="confirmDelete" 
            class="px-6 py-3 bg-red-50 text-red-600 rounded-xl font-medium border border-red-200 hover:bg-red-100 transition-colors flex items-center space-x-2"
          >
            <Icon icon="material-symbols:delete" class="text-lg" />
            <span>删除此记忆</span>
          </button>
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import { apiService, type Avatar, type Memory, type CreateMemoryRequest, type UpdateMemoryRequest, type MemoryType } from '../services/api'

const router = useRouter()
const route = useRoute()

const avatars = ref<Avatar[]>([])
const isEdit = computed(() => !!route.params.id)
const memoryId = computed(() => route.params.id as string)

type CreateMode = 'upload' | 'richtext'
type FileCategory = 'image' | 'video' | 'document'

const createMode = ref<CreateMode>('richtext')

const form = ref<{
  avatarId: string
  title: string
  description: string
  tags: string[]
}>({
  avatarId: '',
  title: '',
  description: '',
  tags: []
})

const newTag = ref('')

const fileInput = ref<HTMLInputElement | null>(null)
const uploadedFile = ref<File | null>(null)
const uploadedFileCategory = ref<FileCategory>('document')
const imagePreview = ref<string>('')
const videoPreview = ref<string>('')
const fileContent = ref<string>('')

const richTextEditor = ref<HTMLDivElement | null>(null)
const richTextImageInput = ref<HTMLInputElement | null>(null)
const richTextVideoInput = ref<HTMLInputElement | null>(null)
const richTextContent = ref<string>('')
const richTextCharacterCount = ref<number>(0)

const showDeleteModal = ref(false)
const showToast = ref(false)
const toastType = ref<'success' | 'error'>('success')
const toastMessage = ref('')

const canSave = computed(() => {
  if (!form.value.avatarId || !form.value.title) return false
  
  if (isEdit.value) {
    return true
  }
  
  if (createMode.value === 'upload') {
    if (!uploadedFile.value) return false
  } else {
    if (!richTextContent.value.trim()) return false
  }
  
  return true
})

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

const loadMemory = async () => {
  if (!isEdit.value) return
  
  const response = await apiService.getMemory(memoryId.value)
  if (response.success && response.data) {
    const memory = response.data
    form.value = {
      avatarId: memory.avatarId,
      title: memory.title,
      description: memory.description || '',
      tags: memory.tags || []
    }
    
    if (memory.type === 'richtext') {
      createMode.value = 'richtext'
      richTextContent.value = memory.content
      await nextTick()
      if (richTextEditor.value) {
        richTextEditor.value.innerHTML = memory.content
        updateRichTextCharacterCount()
      }
    } else {
      createMode.value = 'upload'
      fileContent.value = memory.content
      
      if (memory.type === 'image') {
        uploadedFileCategory.value = 'image'
        imagePreview.value = memory.content
      } else if (memory.type === 'video') {
        uploadedFileCategory.value = 'video'
        videoPreview.value = memory.content
      } else {
        uploadedFileCategory.value = 'document'
      }
    }
  }
}

const addTag = () => {
  if (newTag.value.trim() && !form.value.tags.includes(newTag.value.trim())) {
    form.value.tags.push(newTag.value.trim())
    newTag.value = ''
  }
}

const removeTag = (index: number) => {
  form.value.tags.splice(index, 1)
}

const getFileCategory = (fileName: string): FileCategory => {
  const ext = fileName.toLowerCase().split('.').pop() || ''
  
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico']
  const videoExtensions = ['mp4', 'mov', 'avi', 'mkv', 'webm', 'flv', 'wmv', 'm4v']
  
  if (imageExtensions.includes(ext)) {
    return 'image'
  } else if (videoExtensions.includes(ext)) {
    return 'video'
  } else {
    return 'document'
  }
}

const getUploadedFileIcon = (): string => {
  if (!uploadedFile.value) return 'material-symbols:description-outline'
  
  const icons: Record<FileCategory, string> = {
    image: 'material-symbols:image-outline',
    video: 'material-symbols:videocam-outline',
    document: 'material-symbols:description-outline'
  }
  
  return icons[uploadedFileCategory.value]
}

const getUploadedFileTypeLabel = (): string => {
  if (!uploadedFile.value) return ''
  
  const ext = uploadedFile.value.name.toLowerCase().split('.').pop() || ''
  
  const labels: Record<string, string> = {
    pdf: 'PDF 文档',
    doc: 'Word 文档',
    docx: 'Word 文档',
    ppt: 'PowerPoint 演示文稿',
    pptx: 'PowerPoint 演示文稿',
    xls: 'Excel 表格',
    xlsx: 'Excel 表格',
    txt: '文本文件',
    rtf: '富文本文件',
    jpg: 'JPEG 图片',
    jpeg: 'JPEG 图片',
    png: 'PNG 图片',
    gif: 'GIF 图片',
    bmp: 'BMP 图片',
    webp: 'WebP 图片',
    svg: 'SVG 图片',
    mp4: 'MP4 视频',
    mov: 'MOV 视频',
    avi: 'AVI 视频',
    mkv: 'MKV 视频',
    webm: 'WebM 视频',
    flv: 'FLV 视频',
    wmv: 'WMV 视频'
  }
  
  return labels[ext] || `${ext.toUpperCase()} 文件`
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const triggerFileUpload = () => {
  fileInput.value?.click()
}

const handleFileUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  
  uploadedFile.value = file
  uploadedFileCategory.value = getFileCategory(file.name)
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const result = e.target?.result as string
    fileContent.value = result
    
    if (uploadedFileCategory.value === 'image') {
      imagePreview.value = result
      videoPreview.value = ''
    } else if (uploadedFileCategory.value === 'video') {
      videoPreview.value = result
      imagePreview.value = ''
    } else {
      imagePreview.value = ''
      videoPreview.value = ''
    }
  }
  reader.readAsDataURL(file)
}

const clearUploadedFile = () => {
  uploadedFile.value = null
  uploadedFileCategory.value = 'document'
  fileContent.value = ''
  imagePreview.value = ''
  videoPreview.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatText = (command: string) => {
  document.execCommand(command, false)
  richTextEditor.value?.focus()
}

const formatHeading = (event: Event) => {
  const select = event.target as HTMLSelectElement
  const value = select.value
  if (value) {
    if (value === 'p') {
      document.execCommand('formatBlock', false, 'p')
    } else {
      document.execCommand('formatBlock', false, value)
    }
  }
  richTextEditor.value?.focus()
  select.value = ''
}

const insertImageFromFile = () => {
  richTextImageInput.value?.click()
}

const handleRichTextImageInsert = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      const result = e.target?.result as string
      const imgHtml = `<img src="${result}" style="max-width: 100%; margin: 16px 0; border-radius: 8px;" />`
      document.execCommand('insertHTML', false, imgHtml)
      handleRichTextInput()
    }
    reader.readAsDataURL(file)
  }
  if (richTextImageInput.value) {
    richTextImageInput.value.value = ''
  }
}

const insertVideoFromFile = () => {
  richTextVideoInput.value?.click()
}

const handleRichTextVideoInsert = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      const result = e.target?.result as string
      const videoHtml = `<video src="${result}" controls style="max-width: 100%; margin: 16px 0; border-radius: 8px;"></video>`
      document.execCommand('insertHTML', false, videoHtml)
      handleRichTextInput()
    }
    reader.readAsDataURL(file)
  }
  if (richTextVideoInput.value) {
    richTextVideoInput.value.value = ''
  }
}

const handleRichTextInput = () => {
  if (richTextEditor.value) {
    richTextContent.value = richTextEditor.value.innerHTML
    updateRichTextCharacterCount()
  }
}

const handleRichTextBlur = () => {
  handleRichTextInput()
}

const updateRichTextCharacterCount = () => {
  if (richTextEditor.value) {
    const text = richTextEditor.value.innerText || ''
    richTextCharacterCount.value = text.length
  }
}

const getMemoryType = (): MemoryType => {
  if (createMode.value === 'richtext') {
    return 'richtext'
  } else {
    if (uploadedFileCategory.value === 'image') {
      return 'image'
    } else if (uploadedFileCategory.value === 'video') {
      return 'video'
    } else {
      return 'document'
    }
  }
}

const getMemoryContent = (): string => {
  if (createMode.value === 'richtext') {
    return richTextContent.value
  } else {
    return fileContent.value
  }
}

const saveMemory = async () => {
  if (!canSave.value) return

  try {
    if (isEdit.value) {
      let updates: UpdateMemoryRequest = {
        title: form.value.title,
        description: form.value.description,
        tags: form.value.tags
      }
      
      if (!isEdit.value || richTextContent.value) {
        updates.type = getMemoryType()
        updates.content = getMemoryContent()
      }
      
      const response = await apiService.updateMemory(memoryId.value, updates)
      if (response.success) {
        showToastMessage('success', '记忆更新成功')
        setTimeout(() => {
          router.back()
        }, 1500)
      } else {
        showToastMessage('error', response.error || '更新失败')
      }
    } else {
      const newMemory: CreateMemoryRequest = {
        avatarId: form.value.avatarId,
        title: form.value.title,
        type: getMemoryType(),
        content: getMemoryContent(),
        description: form.value.description,
        tags: form.value.tags
      }
      
      const response = await apiService.createMemory(newMemory)
      if (response.success) {
        showToastMessage('success', '记忆创建成功')
        setTimeout(() => {
          router.back()
        }, 1500)
      } else {
        showToastMessage('error', response.error || '创建失败')
      }
    }
  } catch (error) {
    showToastMessage('error', '操作失败，请重试')
  }
}

const confirmDelete = () => {
  showDeleteModal.value = true
}

const deleteMemory = async () => {
  try {
    const response = await apiService.deleteMemory(memoryId.value)
    if (response.success) {
      showDeleteModal.value = false
      showToastMessage('success', '记忆删除成功')
      setTimeout(() => {
        router.back()
      }, 1500)
    } else {
      showToastMessage('error', response.error || '删除失败')
    }
  } catch (error) {
    showToastMessage('error', '删除失败，请重试')
  }
}

onMounted(() => {
  loadAvatars()
  if (isEdit.value) {
    loadMemory()
  }
})
</script>

<style scoped>
.prose :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 16px 0;
}

.prose :deep(video) {
  max-width: 100%;
  border-radius: 8px;
  margin: 16px 0;
}

.prose :deep(p) {
  margin: 8px 0;
  line-height: 1.75;
}

.prose :deep(h1) {
  font-size: 1.875rem;
  font-weight: 700;
  margin: 16px 0 8px 0;
  color: #5C4A3A;
}

.prose :deep(h2) {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 14px 0 7px 0;
  color: #5C4A3A;
}

.prose :deep(h3) {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 12px 0 6px 0;
  color: #5C4A3A;
}

.prose :deep(ul) {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin: 8px 0;
}

.prose :deep(ol) {
  list-style-type: decimal;
  padding-left: 1.5rem;
  margin: 8px 0;
}

.prose :deep(li) {
  margin: 4px 0;
}

.prose :deep(strong) {
  font-weight: 600;
}

.prose :deep(em) {
  font-style: italic;
}

.prose :deep(u) {
  text-decoration: underline;
}

[contenteditable]:empty:before {
  content: attr(placeholder);
  color: #9CA3AF;
  pointer-events: none;
}
</style>
