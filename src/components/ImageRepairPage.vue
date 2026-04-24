<template>
  <div class="min-h-screen paper-texture">
    <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div class="flex items-center space-x-4 cursor-pointer" @click="goBack">
          <button class="w-10 h-10 rounded-full bg-[#E8D5C4] flex items-center justify-center hover:bg-[#D4A574] transition-colors">
            <Icon icon="solar:arrow-left-bold" class="text-[#8B6F4E] text-lg" />
          </button>
          <div>
            <h1 class="text-xl font-bold text-[#5C4A3A] font-serif tracking-wider">影像修复</h1>
            <p class="text-xs text-gray-500 tracking-[0.15em] uppercase font-medium">让老照片焕发新生</p>
          </div>
        </div>

        <div class="flex items-center space-x-3">
          <button class="w-10 h-10 rounded-full bg-white/80 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow">
            <Icon icon="solar:bell-bold" class="text-gray-600" />
          </button>
          <div class="flex items-center space-x-3 pl-4 border-l border-[#E8D5C4]">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] p-0.5">
              <div class="w-full h-full rounded-full bg-gray-200 overflow-hidden">
                <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face" 
                     class="w-full h-full object-cover" alt="用户头像">
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="max-w-5xl mx-auto px-6 py-8">
      <div v-if="!uploadedImage" class="bg-white rounded-2xl p-8 shadow-soft border border-stone-100">
        <div 
          class="border-2 border-dashed border-[#E8D5C4] rounded-2xl p-16 text-center hover:border-[#D4A574] transition-colors cursor-pointer"
          @click="triggerUpload"
          @dragover.prevent="isDragOver = true"
          @dragleave="isDragOver = false"
          @drop.prevent="handleDrop"
          :class="{ 'border-[#D4A574] bg-[#F5E6D3]/30': isDragOver }"
        >
          <input 
            type="file" 
            ref="fileInput" 
            class="hidden" 
            accept="image/*"
            @change="handleFileSelect"
          >
          <div class="w-20 h-20 bg-[#E8D5C4] rounded-full flex items-center justify-center mx-auto mb-4">
            <Icon icon="solar:upload-cloud-bold-duotone" class="text-[#8B6F4E] text-4xl" />
          </div>
          <p class="text-lg font-medium text-gray-700 mb-2">上传照片开始修复</p>
          <p class="text-sm text-gray-400">点击或拖拽上传 JPG、PNG、WEBP 格式照片</p>
        </div>

        <div v-if="recentImages.length > 0" class="mt-8">
          <h4 class="text-sm font-medium text-gray-600 mb-4">最近使用</h4>
          <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
            <div 
              v-for="img in recentImages" :key="img.id"
              class="aspect-square rounded-lg overflow-hidden bg-gray-100 relative group cursor-pointer hover:shadow-lg transition-shadow"
              @click="selectRecentImage(img)"
            >
              <img :src="img.url" class="w-full h-full object-cover" :alt="`最近照片${img.id}`">
              <div class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
                <Icon icon="solar:check-circle-bold" class="text-white text-2xl" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="bg-white rounded-2xl shadow-soft border border-stone-100 overflow-hidden">
        <div class="relative">
          <div class="absolute top-4 right-4 z-10 flex items-center space-x-2">
            <button 
              class="flex items-center space-x-1.5 px-3 py-2 bg-white/90 backdrop-blur-sm text-[#8B6F4E] rounded-lg shadow-sm hover:bg-[#E8D5C4]/80 transition-colors text-sm"
              @click="showSaveGalleryModal = true"
            >
              <Icon icon="solar:gallery-add-bold" class="text-base" />
              <span class="font-medium">保存</span>
            </button>
            <button 
              class="flex items-center space-x-1.5 px-3 py-2 bg-[#8B6F4E] text-white rounded-lg shadow-sm hover:bg-[#6B5342] transition-colors text-sm"
              @click="downloadImage"
            >
              <Icon icon="solar:download-minimalistic-bold" class="text-base" />
              <span class="font-medium">下载</span>
            </button>
          </div>

          <div v-if="isProcessing" class="absolute top-4 left-4 z-10 px-3 py-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-sm">
            <div class="flex items-center space-x-2 text-sm text-[#8B6F4E]">
              <Icon icon="solar:loader-2-bold" class="animate-spin" />
              <span>正在处理... {{ processingProgress }}%</span>
            </div>
          </div>

          <div v-if="showBeforeAfter && repairedImage" class="grid grid-cols-2 gap-0.5 p-4 bg-[#F5E6D3]/30">
            <div class="relative">
              <p class="absolute top-2 left-2 z-10 px-2 py-1 bg-black/60 text-white text-xs rounded">原图</p>
              <div class="aspect-video rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
                <img 
                  :src="uploadedImage" 
                  class="max-w-full max-h-full object-contain transition-transform duration-300"
                  :style="imageTransform"
                  alt="原图"
                >
              </div>
            </div>
            <div class="relative">
              <p class="absolute top-2 left-2 z-10 px-2 py-1 bg-emerald-500/80 text-white text-xs rounded">修复后</p>
              <div class="aspect-video rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
                <img 
                  :src="repairedImage" 
                  class="max-w-full max-h-full object-contain transition-transform duration-300"
                  :style="imageTransform"
                  alt="修复后"
                >
              </div>
            </div>
          </div>

          <div v-else class="p-4 bg-[#F5E6D3]/30">
            <div class="aspect-video rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center relative">
              <img 
                :src="repairedImage || uploadedImage" 
                class="max-w-full max-h-full object-contain transition-all duration-300"
                :style="imageTransform"
                :alt="repairedImage ? '修复后' : '原图'"
              >
              <div v-if="repairedImage" class="absolute bottom-3 right-3 px-2.5 py-1 bg-emerald-500/90 text-white text-xs rounded-full">
                <Icon icon="solar:check-bold" class="inline mr-1" />
                已修复
              </div>
            </div>
          </div>
        </div>

        <div class="p-4 border-t border-[#E8D5C4]">
          <div class="mb-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wider">照片编辑</h4>
              <div v-if="activeEditTool" class="flex items-center space-x-3">
                <button 
                  class="text-xs text-gray-400 hover:text-[#8B6F4E]"
                  @click="resetEditTool"
                >
                  重置
                </button>
                <button 
                  class="text-xs text-[#8B6F4E] font-medium"
                  @click="applyEdit"
                >
                  完成
                </button>
              </div>
            </div>
            
            <div class="flex items-center space-x-1 overflow-x-auto pb-2">
              <button 
                v-for="editTool in editTools" :key="editTool.id"
                class="flex flex-col items-center space-y-1 px-4 py-2.5 rounded-lg transition-all flex-shrink-0"
                :class="[
                  activeEditTool === editTool.id 
                    ? 'bg-[#8B6F4E] text-white' 
                    : 'bg-[#F5E6D3]/50 text-gray-700 hover:bg-[#E8D5C4]'
                ]"
                @click="selectEditTool(editTool.id)"
              >
                <Icon :icon="editTool.icon" class="text-lg" />
                <span class="text-xs font-medium">{{ editTool.label }}</span>
              </button>
            </div>

            <div v-if="activeEditTool" class="mt-3 bg-[#F5E6D3]/30 rounded-lg p-3">
              <div v-if="activeEditTool === 'rotate'">
                <div class="flex items-center justify-center space-x-2">
                  <button 
                    v-for="angle in [0, 90, 180, 270]" :key="angle"
                    class="px-3 py-1.5 rounded-md text-xs transition-all"
                    :class="[
                      rotation === angle 
                        ? 'bg-[#8B6F4E] text-white' 
                        : 'bg-white text-[#8B6F4E] hover:bg-[#D4A574]'
                    ]"
                    @click="rotation = angle"
                  >
                    {{ angle }}°
                  </button>
                </div>
              </div>

              <div v-if="activeEditTool === 'flip'">
                <div class="flex items-center justify-center space-x-3">
                  <button 
                    class="px-4 py-2 rounded-md text-xs transition-all flex items-center space-x-1.5"
                    :class="[
                      flipHorizontal 
                        ? 'bg-[#8B6F4E] text-white' 
                        : 'bg-white text-[#8B6F4E] hover:bg-[#D4A574]'
                    ]"
                    @click="flipHorizontal = !flipHorizontal"
                  >
                    <Icon icon="solar:swap-horizontal-bold" class="text-sm" />
                    <span>水平</span>
                  </button>
                  <button 
                    class="px-4 py-2 rounded-md text-xs transition-all flex items-center space-x-1.5"
                    :class="[
                      flipVertical 
                        ? 'bg-[#8B6F4E] text-white' 
                        : 'bg-white text-[#8B6F4E] hover:bg-[#D4A574]'
                    ]"
                    @click="flipVertical = !flipVertical"
                  >
                    <Icon icon="solar:swap-vertical-bold" class="text-sm" />
                    <span>垂直</span>
                  </button>
                </div>
              </div>

              <div v-if="activeEditTool === 'zoom'">
                <div class="flex items-center justify-between text-xs mb-2">
                  <span class="text-gray-600">缩放比例</span>
                  <span class="text-[#8B6F4E] font-medium">{{ zoom }}%</span>
                </div>
                <input 
                  type="range" 
                  v-model.number="zoom" 
                  min="50" 
                  max="200" 
                  step="10"
                  class="w-full h-1.5 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer accent-[#8B6F4E]"
                >
              </div>

              <div v-if="activeEditTool === 'crop'">
                <div class="flex items-center justify-center space-x-1.5 flex-wrap gap-1.5">
                  <button 
                    v-for="ratio in cropRatios" :key="ratio.id"
                    class="px-3 py-1.5 rounded-md text-xs transition-all"
                    :class="[
                      selectedCropRatio === ratio.id 
                        ? 'bg-[#8B6F4E] text-white' 
                        : 'bg-white text-[#8B6F4E] hover:bg-[#D4A574]'
                    ]"
                    @click="selectedCropRatio = ratio.id"
                  >
                    {{ ratio.label }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="pt-4 border-t border-[#E8D5C4]">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-xs font-medium text-gray-500 uppercase tracking-wider">修复工具</h4>
              <div v-if="hasAnyToolApplied && !repairedImage" class="flex items-center space-x-2">
                <button 
                  class="flex items-center space-x-1.5 px-3 py-1.5 bg-[#8B6F4E] text-white rounded-lg hover:bg-[#6B5342] transition-colors text-xs"
                  @click="applyAllTools"
                >
                  <Icon icon="solar:magic-stick-3-bold" class="text-sm" />
                  <span class="font-medium">应用修复</span>
                </button>
              </div>
              <div v-else-if="repairedImage" class="flex items-center space-x-2">
                <button 
                  class="text-xs text-[#8B6F4E] hover:underline"
                  @click="toggleCompare"
                >
                  {{ showBeforeAfter ? '关闭对比' : '对比查看' }}
                </button>
                <button 
                  class="text-xs text-gray-400 hover:text-gray-600"
                  @click="resetAll"
                >
                  重新开始
                </button>
              </div>
            </div>

            <div class="flex items-center space-x-1 overflow-x-auto pb-2">
              <button 
                v-for="tool in repairTools" :key="tool.id"
                class="flex flex-col items-center space-y-1 px-4 py-2.5 rounded-lg transition-all flex-shrink-0 relative"
                :class="[
                  activeTool === tool.id 
                    ? 'bg-[#8B6F4E] text-white' 
                    : toolApplied[tool.id]
                    ? 'bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200'
                    : 'bg-[#F5E6D3]/50 text-gray-700 hover:bg-[#E8D5C4]'
                ]"
                @click="selectTool(tool.id)"
              >
                <Icon :icon="tool.icon" 
                      :class="activeTool === tool.id ? 'text-white' : toolApplied[tool.id] ? 'text-emerald-600' : tool.color"
                      class="text-lg" />
                <span class="text-xs font-medium">{{ tool.label }}</span>
                <Icon v-if="toolApplied[tool.id]" 
                      icon="solar:check-circle-bold" 
                      class="text-emerald-500 absolute -top-1 -right-1" />
              </button>
            </div>

            <div v-if="activeToolConfig && !repairedImage" class="mt-3 bg-[#F5E6D3]/30 rounded-lg p-3">
              <div v-if="activeToolConfig.hasStrength">
                <div class="flex items-center justify-between text-xs mb-2">
                  <span class="text-gray-600">修复强度</span>
                  <span class="text-[#8B6F4E] font-medium">{{ toolStrength }}%</span>
                </div>
                <input 
                  type="range" 
                  v-model="toolStrength" 
                  min="10" 
                  max="100" 
                  step="10"
                  class="w-full h-1.5 bg-[#E8D5C4] rounded-lg appearance-none cursor-pointer accent-[#8B6F4E]"
                >
              </div>

              <div v-if="activeToolConfig.options" class="grid grid-cols-2 gap-2">
                <button 
                  v-for="option in activeToolConfig.options" :key="option.id"
                  class="px-3 py-2 rounded-md border transition-all text-left"
                  :class="[
                    selectedOption === option.id 
                      ? 'border-[#8B6F4E] bg-[#E8D5C4]/50' 
                      : 'border-[#E8D5C4] bg-white hover:border-[#D4A574]'
                  ]"
                  @click="selectedOption = option.id"
                >
                  <p class="font-medium text-xs" :class="selectedOption === option.id ? 'text-[#8B6F4E]' : 'text-gray-700'">
                    {{ option.label }}
                  </p>
                  <p class="text-[10px] text-gray-400 mt-0.5">{{ option.description }}</p>
                </button>
              </div>

              <button 
                class="w-full mt-3 flex items-center justify-center space-x-1.5 px-3 py-2 bg-[#8B6F4E] text-white rounded-lg hover:bg-[#6B5342] transition-colors text-xs"
                @click="applyCurrentTool"
              >
                <Icon icon="solar:check-bold" class="text-sm" />
                <span class="font-medium">应用{{ activeToolConfig.label }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="uploadedImage" class="mt-6">
        <h4 class="text-sm font-medium text-gray-600 mb-4">点击切换其他照片</h4>
        <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-3">
          <div 
            v-for="img in recentImages" :key="img.id"
            class="aspect-square rounded-lg overflow-hidden bg-gray-100 relative group cursor-pointer hover:shadow-lg transition-shadow"
            :class="{ 'ring-2 ring-[#8B6F4E]': uploadedImage === img.url }"
            @click="selectRecentImage(img)"
          >
            <img :src="img.url" class="w-full h-full object-cover" :alt="`最近照片${img.id}`">
            <div v-if="uploadedImage === img.url" class="absolute inset-0 bg-[#8B6F4E]/20 flex items-center justify-center">
              <Icon icon="solar:check-circle-bold" class="text-[#8B6F4E] text-3xl" />
            </div>
            <div v-else class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
              <Icon icon="solar:check-circle-bold" class="text-white text-2xl" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showSaveGalleryModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/50" @click="showSaveGalleryModal = false"></div>
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">保存到影集</h3>
          <button 
            class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
            @click="showSaveGalleryModal = false"
          >
            <Icon icon="solar:close-circle-bold" class="text-xl" />
          </button>
        </div>

        <div class="aspect-video rounded-xl overflow-hidden bg-gray-100 mb-6">
          <img :src="repairedImage || uploadedImage" class="w-full h-full object-contain" alt="预览">
        </div>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">选择影集</label>
          <div class="relative">
            <button 
              class="w-full flex items-center justify-between px-4 py-3 border border-[#E8D5C4] rounded-xl bg-white hover:border-[#D4A574] transition-colors"
              @click="showGalleryDropdown = !showGalleryDropdown"
            >
              <span class="text-sm" :class="selectedGallery ? 'text-gray-800' : 'text-gray-400'">
                {{ selectedGallery ? getGalleryById(selectedGallery)?.name : '请选择影集' }}
              </span>
              <Icon :icon="showGalleryDropdown ? 'solar:arrow-up-bold' : 'solar:arrow-down-bold'" class="text-gray-400" />
            </button>

            <div v-if="showGalleryDropdown" class="absolute top-full left-0 right-0 mt-2 bg-white border border-[#E8D5C4] rounded-xl shadow-lg overflow-hidden z-10">
              <div 
                v-for="gallery in galleryList" :key="gallery.id"
                class="flex items-center space-x-3 px-4 py-3 hover:bg-[#F5E6D3]/50 cursor-pointer transition-colors"
                :class="{ 'bg-[#E8D5C4]/50': selectedGallery === gallery.id }"
                @click="selectGallery(gallery.id)"
              >
                <div class="w-10 h-10 rounded-lg bg-[#E8D5C4] flex items-center justify-center overflow-hidden">
                  <img v-if="gallery.thumb" :src="gallery.thumb" class="w-full h-full object-cover" :alt="gallery.name">
                  <Icon v-else icon="solar:gallery-wide-bold-duotone" class="text-[#8B6F4E]" />
                </div>
                <div class="flex-1">
                  <p class="font-medium text-sm text-gray-800">{{ gallery.name }}</p>
                  <p class="text-xs text-gray-400">{{ gallery.personName }} · {{ gallery.mediaCount }} 张</p>
                </div>
                <Icon v-if="selectedGallery === gallery.id" icon="solar:check-circle-bold" class="text-[#8B6F4E]" />
              </div>
            </div>
          </div>
        </div>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">添加备注（可选）</label>
          <textarea 
            v-model="galleryNote"
            class="w-full px-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent text-sm resize-none"
            rows="3"
            placeholder="为这张照片添加备注..."
          ></textarea>
        </div>

        <div class="flex items-center justify-end space-x-3">
          <button 
            class="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors text-sm"
            @click="showSaveGalleryModal = false"
          >
            取消
          </button>
          <button 
            class="px-5 py-2.5 bg-[#8B6F4E] text-white rounded-xl hover:bg-[#6B5342] transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!selectedGallery"
            @click="saveToGallery"
          >
            保存
          </button>
        </div>
      </div>
    </div>

    <footer class="bg-[#5C4A3A] text-white py-6 mt-auto">
      <div class="max-w-7xl mx-auto px-6">
        <div class="flex flex-col md:flex-row items-center justify-between">
          <div class="flex items-center space-x-4 mb-4 md:mb-0">
            <div class="w-8 h-8 bg-[#C84A3E] rounded-sm flex items-center justify-center">
              <span class="text-white font-serif text-sm font-bold">存</span>
            </div>
            <p class="text-xs text-white/60">© 2024 memorise · 家族精神纪念馆</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const router = useRouter()

const fileInput = ref<HTMLInputElement | null>(null)

const isDragOver = ref(false)
const uploadedImage = ref<string | null>(null)
const repairedImage = ref<string | null>(null)
const isProcessing = ref(false)
const processingProgress = ref(0)

const activeTool = ref<string | null>(null)
const toolStrength = ref(80)
const selectedOption = ref<string | null>(null)
const toolApplied = reactive<Record<string, boolean>>({})
const showBeforeAfter = ref(false)

const activeEditTool = ref<string | null>(null)
const rotation = ref(0)
const flipHorizontal = ref(false)
const flipVertical = ref(false)
const zoom = ref(100)
const selectedCropRatio = ref('original')

const showSaveGalleryModal = ref(false)
const showGalleryDropdown = ref(false)
const selectedGallery = ref<string | null>(null)
const galleryNote = ref('')

const recentImages = ref([
  { id: '1', url: 'https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=300&h=300&fit=crop' },
  { id: '2', url: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=300&h=300&fit=crop' },
  { id: '3', url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&h=300&fit=crop' },
  { id: '4', url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=300&h=300&fit=crop' },
])

const editTools = [
  { id: 'rotate', label: '旋转', icon: 'solar:refresh-bold-duotone' },
  { id: 'flip', label: '翻转', icon: 'solar:swap-horizontal-bold-duotone' },
  { id: 'zoom', label: '缩放', icon: 'solar:zoom-in-bold-duotone' },
  { id: 'crop', label: '裁剪', icon: 'solar:scissors-bold-duotone' },
]

const cropRatios = [
  { id: 'original', label: '原图' },
  { id: '1:1', label: '1:1' },
  { id: '4:3', label: '4:3' },
  { id: '16:9', label: '16:9' },
  { id: '3:4', label: '3:4' },
  { id: '9:16', label: '9:16' },
]

interface RepairTool {
  id: string
  label: string
  description: string
  icon: string
  color: string
  hasStrength?: boolean
  options?: { id: string; label: string; description: string }[]
}

const repairTools: RepairTool[] = [
  {
    id: 'sharpen',
    label: '变清晰',
    description: '提升分辨率和锐度',
    icon: 'solar:zoom-in-bold-duotone',
    color: 'text-[#8B6F4E]',
    hasStrength: true,
    options: [
      { id: 'light', label: '轻度', description: '轻微增强' },
      { id: 'medium', label: '中等', description: '平衡效果' },
      { id: 'strong', label: '强力', description: '显著提升' },
      { id: 'auto', label: '智能', description: '自动识别' }
    ]
  },
  {
    id: 'restore',
    label: '去破损',
    description: '去除划痕、污渍',
    icon: 'solar:eraser-bold-duotone',
    color: 'text-orange-600',
    hasStrength: true,
    options: [
      { id: 'scratch', label: '去划痕', description: '修复线条损伤' },
      { id: 'spot', label: '去污点', description: '去除斑点污渍' },
      { id: 'fold', label: '去折痕', description: '修复折叠痕迹' },
      { id: 'all', label: '全修复', description: '综合修复' }
    ]
  },
  {
    id: 'colorize',
    label: '还原色彩',
    description: '黑白照片上色',
    icon: 'solar:palette-bold-duotone',
    color: 'text-purple-600',
    hasStrength: false,
    options: [
      { id: 'natural', label: '自然色彩', description: '真实还原' },
      { id: 'vintage', label: '复古色调', description: '怀旧风格' },
      { id: 'vibrant', label: '鲜艳色彩', description: '色彩增强' },
      { id: 'sepia', label: '棕褐色', description: '老照片风格' }
    ]
  },
  {
    id: 'animate',
    label: '变成动图',
    description: '让照片动起来',
    icon: 'solar:video-frame-play-horizontal-bold',
    color: 'text-emerald-600',
    hasStrength: false,
    options: [
      { id: 'blink', label: '眨眼', description: '轻微眨眼效果' },
      { id: 'smile', label: '微笑', description: '自然微笑' },
      { id: 'head', label: '点头', description: '轻微头部动作' },
      { id: 'breath', label: '呼吸', description: '自然呼吸感' }
    ]
  }
]

interface Gallery {
  id: string
  name: string
  personName: string
  mediaCount: number
  thumb?: string
}

const galleryList = ref<Gallery[]>([
  {
    id: '1',
    name: '爷爷的青春岁月',
    personName: '张明远',
    mediaCount: 12,
    thumb: 'https://images.unsplash.com/photo-1552374196-c4e7ffc6e126?w=100&h=100&fit=crop'
  },
  {
    id: '2',
    name: '奶奶的美好时光',
    personName: '李淑华',
    mediaCount: 8,
    thumb: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop'
  },
  {
    id: '3',
    name: '家族团圆纪念',
    personName: '家族全员',
    mediaCount: 24,
    thumb: 'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=100&h=100&fit=crop'
  }
])

const imageTransform = computed(() => {
  const scale = zoom.value / 100
  const rotate = rotation.value
  const scaleX = flipHorizontal.value ? -1 : 1
  const scaleY = flipVertical.value ? -1 : 1
  return {
    transform: `scale(${scaleX * scale}, ${scaleY * scale}) rotate(${rotate}deg)`,
    transformOrigin: 'center center'
  }
})

const activeToolConfig = computed(() => {
  return repairTools.find(t => t.id === activeTool.value) || null
})

const hasAnyToolApplied = computed(() => {
  return Object.values(toolApplied).some(v => v === true)
})

const goBack = () => {
  router.push('/gallery')
}

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  const file = event.dataTransfer?.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const processFile = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImage.value = e.target?.result as string
    resetToolState()
    resetEditState()
  }
  reader.readAsDataURL(file)
}

const selectRecentImage = (img: { id: string; url: string }) => {
  uploadedImage.value = img.url
  resetToolState()
  resetEditState()
}

const resetToolState = () => {
  repairedImage.value = null
  activeTool.value = null
  toolStrength.value = 80
  selectedOption.value = null
  showBeforeAfter.value = false
  Object.keys(toolApplied).forEach(key => {
    delete toolApplied[key]
  })
}

const resetEditState = () => {
  activeEditTool.value = null
  rotation.value = 0
  flipHorizontal.value = false
  flipVertical.value = false
  zoom.value = 100
  selectedCropRatio.value = 'original'
}

const selectEditTool = (toolId: string) => {
  activeEditTool.value = activeEditTool.value === toolId ? null : toolId
}

const resetEditTool = () => {
  if (activeEditTool.value === 'rotate') {
    rotation.value = 0
  } else if (activeEditTool.value === 'flip') {
    flipHorizontal.value = false
    flipVertical.value = false
  } else if (activeEditTool.value === 'zoom') {
    zoom.value = 100
  } else if (activeEditTool.value === 'crop') {
    selectedCropRatio.value = 'original'
  }
}

const applyEdit = () => {
  activeEditTool.value = null
}

const selectTool = (toolId: string) => {
  if (!uploadedImage.value) return
  activeTool.value = toolId
  const tool = repairTools.find(t => t.id === toolId)
  if (tool?.options && tool.options.length > 0) {
    selectedOption.value = tool.options[0].id
  }
}

const applyCurrentTool = () => {
  if (!activeTool.value) return
  
  toolApplied[activeTool.value] = true
  activeTool.value = null
}

const applyAllTools = () => {
  isProcessing.value = true
  processingProgress.value = 0
  
  const interval = setInterval(() => {
    processingProgress.value += Math.random() * 20
    if (processingProgress.value >= 100) {
      processingProgress.value = 100
      clearInterval(interval)
      
      setTimeout(() => {
        isProcessing.value = false
        repairedImage.value = uploadedImage.value
      }, 500)
    }
  }, 200)
}

const toggleCompare = () => {
  showBeforeAfter.value = !showBeforeAfter.value
}

const changeImage = () => {
  triggerUpload()
}

const resetAll = () => {
  uploadedImage.value = null
  repairedImage.value = null
  activeTool.value = null
  activeEditTool.value = null
  toolStrength.value = 80
  selectedOption.value = null
  isProcessing.value = false
  processingProgress.value = 0
  showBeforeAfter.value = false
  rotation.value = 0
  flipHorizontal.value = false
  flipVertical.value = false
  zoom.value = 100
  selectedCropRatio.value = 'original'
  Object.keys(toolApplied).forEach(key => {
    delete toolApplied[key]
  })
}

const downloadImage = () => {
  const imageToDownload = repairedImage.value || uploadedImage.value
  if (!imageToDownload) return
  
  const link = document.createElement('a')
  link.href = imageToDownload
  link.download = `memorise-${Date.now()}.png`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const getGalleryById = (id: string) => {
  return galleryList.value.find(g => g.id === id)
}

const selectGallery = (id: string) => {
  selectedGallery.value = id
  showGalleryDropdown.value = false
}

const saveToGallery = () => {
  if (!selectedGallery.value) return
  
  const gallery = getGalleryById(selectedGallery.value)
  alert(`已保存到影集「${gallery?.name}」！`)
  
  showSaveGalleryModal.value = false
  selectedGallery.value = null
  galleryNote.value = ''
}
</script>