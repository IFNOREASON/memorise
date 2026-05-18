<template>
  <div class="min-h-screen paper-texture">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-[#5C4A3A] font-serif mb-2">念境</h1>
        <p class="text-gray-500">3D 虚拟纪念空间，让思念有了具象的归宿</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2">
          <div 
            class="bg-white rounded-2xl shadow-soft border border-stone-100 overflow-hidden transition-all duration-500"
            :style="sceneBackgroundStyle"
          >
            <div class="h-[500px] relative">
              <ThreeDModelViewer
                :key="selectedModel?.id"
                :model-url="selectedModel?.url"
                :auto-rotate="autoRotate"
                :full-height="true"
                :debug-mode="false"
                :background-color="sceneBgColor"
                @loaded="onModelLoaded"
                @error="onModelError"
              />
              <Candle3D 
                v-show="candleLit" 
                :position="candlePosition" 
                :key="candleLit ? 'lit' : 'unlit'"
              />
              <div class="absolute top-4 left-4 bg-white/90 backdrop-blur px-4 py-2 rounded-full shadow-md">
                <span class="text-sm font-medium text-[#5C4A3A]">
                  {{ selectedScene?.name }} · {{ selectedModel?.name }}
                </span>
              </div>
            </div>
            <div class="p-4 border-t border-stone-100 flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <button
                    @click="toggleAutoRotate"
                    class="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-[#E8D5C4]/50 transition-colors"
                    :class="autoRotate ? 'bg-[#E8D5C4] text-[#8B6F4E]' : 'text-gray-600'"
                  >
                    <Icon icon="solar:refresh-bold" class="text-lg" />
                    <span class="text-sm font-medium">{{ autoRotate ? '停止旋转' : '自动旋转' }}</span>
                  </button>
                  <button
                    @click="toggleCandle"
                    class="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-[#E8D5C4]/50 transition-colors"
                    :class="candleLit ? 'bg-amber-100 text-amber-600' : 'text-gray-600'"
                  >
                    <Icon :icon="candleLit ? 'solar:candle-bold' : 'solar:candle-linear'" class="text-lg" />
                    <span class="text-sm font-medium">{{ candleLit ? '熄灭烛光' : '点亮烛光' }}</span>
                  </button>
                </div>
                <div class="text-sm text-gray-400">
                  拖拽旋转 · 滚轮缩放
                </div>
              </div>
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-bold text-[#5C4A3A] font-serif">纪念场景</h3>
              <button 
                @click="showImportModal = true"
                class="text-sm text-[#8B6F4E] hover:underline flex items-center space-x-1"
              >
                <Icon icon="solar:import-bold" class="text-sm" />
                <span>导入场景</span>
              </button>
            </div>
            <div class="space-y-3">
              <div
                v-for="scene in scenes"
                :key="scene.id"
                @click="selectScene(scene)"
                class="p-4 rounded-xl border-2 cursor-pointer transition-all hover:shadow-md"
                :class="selectedScene?.id === scene.id
                  ? 'border-[#8B6F4E] bg-[#FAF7F2]'
                  : 'border-stone-100 hover:border-[#E8D5C4]'"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-10 h-10 rounded-lg flex items-center justify-center"
                       :class="scene.color">
                    <Icon :icon="scene.icon" class="text-xl" />
                  </div>
                  <div>
                    <h4 class="font-bold text-gray-800">{{ scene.name }}</h4>
                    <p class="text-xs text-gray-500">{{ scene.description }}</p>
                  </div>
                </div>
              </div>
              
              <div v-for="scene in customScenes" :key="scene.id"
                @click="selectScene(scene)"
                class="p-4 rounded-xl border-2 border-dashed cursor-pointer transition-all hover:shadow-md"
                :class="selectedScene?.id === scene.id
                  ? 'border-[#8B6F4E] bg-[#FAF7F2]'
                  : 'border-stone-200 hover:border-[#E8D5C4]'"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center text-purple-600">
                      <Icon icon="solar:folder-bold" class="text-xl" />
                    </div>
                    <div>
                      <h4 class="font-bold text-gray-800">{{ scene.name }}</h4>
                      <p class="text-xs text-gray-500">自定义场景</p>
                    </div>
                  </div>
                  <button 
                    @click.stop="deleteCustomScene(scene.id)"
                    class="text-red-400 hover:text-red-600 p-1"
                  >
                    <Icon icon="solar:trash-bin-trash-bold" class="text-sm" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-2xl shadow-soft border border-stone-100 p-6">
            <h3 class="text-lg font-bold text-[#5C4A3A] font-serif mb-4">纪念模型</h3>
            <div class="grid grid-cols-2 gap-3">
              <div
                v-for="model in models"
                :key="model.id"
                @click="selectModel(model)"
                class="p-3 rounded-xl border-2 cursor-pointer transition-all hover:shadow-md text-center"
                :class="selectedModel?.id === model.id
                  ? 'border-[#8B6F4E] bg-[#FAF7F2]'
                  : 'border-stone-100 hover:border-[#E8D5C4]'"
              >
                <div class="w-full h-16 rounded-lg bg-[#E8D5C4]/30 flex items-center justify-center mb-2">
                  <Icon :icon="model.icon" class="text-2xl text-[#8B6F4E]" />
                </div>
                <p class="text-sm font-medium text-gray-700">{{ model.name }}</p>
              </div>
            </div>
          </div>

          <div class="bg-gradient-to-br from-[#8B6F4E] to-[#A67B5B] rounded-2xl p-6 text-white">
            <div class="flex items-center space-x-3 mb-4">
              <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <Icon :icon="candleLit ? 'solar:candle-bold' : 'solar:candle-linear'" class="text-xl" />
              </div>
              <div>
                <h3 class="font-bold font-serif">今日纪念</h3>
                <p class="text-xs text-white/70">
                  {{ candleLit ? '烛光已点亮，愿思念永恒' : '点击按钮点亮思念的烛光' }}
                </p>
              </div>
            </div>
            <button 
              @click="toggleCandle"
              class="w-full py-3 bg-white/20 backdrop-blur rounded-xl font-medium hover:bg-white/30 transition-colors active:scale-95"
            >
              <span class="flex items-center justify-center space-x-2">
                <Icon :icon="candleLit ? 'solar:candle-bold' : 'solar:candle-linear'" />
                <span>{{ candleLit ? '熄灭烛光' : '点亮烛光' }}</span>
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showImportModal" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showImportModal = false"></div>
        
        <div class="relative w-full max-w-md mx-4 bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] px-6 py-4">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-bold text-white font-serif">导入自定义场景</h3>
              <button 
                @click="showImportModal = false"
                class="text-white/80 hover:text-white transition-colors"
              >
                <Icon icon="solar:close-circle-bold" class="text-xl" />
              </button>
            </div>
          </div>

          <div class="p-6">
            <div class="mb-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
              <h4 class="text-sm font-bold text-blue-800 mb-2 flex items-center space-x-2">
                <Icon icon="solar:info-circle-bold" class="text-lg" />
                <span>支持的文件格式</span>
              </h4>
              <ul class="text-xs text-blue-700 space-y-1">
                <li>• <strong>.glb</strong> - GL Transmission Format（推荐）</li>
                <li>• <strong>.gltf</strong> - GL Transmission Format（带纹理）</li>
                <li>• <strong>.obj</strong> - Wavefront Object</li>
                <li>• <strong>.fbx</strong> - Autodesk FBX（有限支持）</li>
              </ul>
            </div>

            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">场景名称</label>
              <input 
                v-model="importSceneName"
                type="text"
                placeholder="请输入场景名称"
                class="w-full px-4 py-3 border border-stone-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#8B6F4E] focus:border-transparent"
              />
            </div>

            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-2">选择文件</label>
              <div 
                @click="triggerFileInput"
                @drop="handleDrop"
                @dragover.prevent="dragOver = true"
                @dragleave="dragOver = false"
                class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all"
                :class="dragOver 
                  ? 'border-[#8B6F4E] bg-[#FAF7F2]' 
                  : importError 
                    ? 'border-red-300 bg-red-50' 
                    : importFile 
                      ? 'border-emerald-300 bg-emerald-50' 
                      : 'border-stone-300 hover:border-[#E8D5C4]'"
              >
                <input 
                  ref="fileInputRef"
                  type="file"
                  @change="handleFileSelect"
                  accept=".glb,.gltf,.obj,.fbx"
                  class="hidden"
                />
                
                <div v-if="importFile" class="space-y-2">
                  <div class="w-12 h-12 mx-auto bg-emerald-100 rounded-full flex items-center justify-center">
                    <Icon icon="solar:check-circle-bold" class="text-2xl text-emerald-600" />
                  </div>
                  <p class="text-sm font-medium text-gray-800">{{ importFile.name }}</p>
                  <p class="text-xs text-gray-500">{{ formatFileSize(importFile.size) }}</p>
                </div>
                <div v-else>
                  <div class="w-12 h-12 mx-auto bg-[#E8D5C4] rounded-full flex items-center justify-center mb-3">
                    <Icon icon="solar:upload-minimalistic-bold" class="text-2xl text-[#8B6F4E]" />
                  </div>
                  <p class="text-sm font-medium text-gray-700 mb-1">点击或拖拽文件到此处</p>
                  <p class="text-xs text-gray-400">支持 .glb, .gltf, .obj, .fbx 格式</p>
                </div>
              </div>
              
              <p v-if="importError" class="mt-2 text-xs text-red-500 flex items-center space-x-1">
                <Icon icon="solar:danger-triangle-bold" class="text-sm" />
                <span>{{ importError }}</span>
              </p>
            </div>

            <div class="flex space-x-3">
              <button
                @click="showImportModal = false"
                class="flex-1 py-3 border border-stone-200 text-gray-600 font-medium rounded-xl hover:bg-stone-50 transition-all"
              >
                取消
              </button>
              <button
                @click="confirmImport"
                :disabled="!importFile || !importSceneName || importing"
                class="flex-1 py-3 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white font-medium rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <Icon v-if="importing" icon="solar:refresh-circle-bold" class="animate-spin mr-2" />
                {{ importing ? '导入中...' : '确认导入' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'
import ThreeDModelViewer from './ThreeDModelViewer.vue'
import Candle3D from './Candle3D.vue'

interface Scene {
  id: string
  name: string
  description: string
  icon: string
  color: string
  bgColor: string
  bgColorHex: number
  ambientColor: number
  isCustom?: boolean
  customUrl?: string
}

interface Model {
  id: string
  name: string
  icon: string
  url?: string
}

const autoRotate = ref(true)
const selectedScene = ref<Scene | null>(null)
const selectedModel = ref<Model | null>(null)
const candleLit = ref(false)
const candlePosition = ref([0, 0, 0])

const showImportModal = ref(false)
const importSceneName = ref('')
const importFile = ref<File | null>(null)
const importError = ref('')
const importing = ref(false)
const dragOver = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const customScenes = ref<Scene[]>([])

const scenes: Scene[] = [
  { 
    id: 'garden', 
    name: '静谧花园', 
    description: '春暖花开，宁静致远', 
    icon: 'solar:tree-bold', 
    color: 'bg-emerald-100 text-emerald-600',
    bgColor: 'rgba(16, 185, 129, 0.05)',
    bgColorHex: 0xf0fdf4,
    ambientColor: 0x86efac
  },
  { 
    id: 'ocean', 
    name: '永恒之海', 
    description: '海阔天空，思念无边', 
    icon: 'solar:waterdrop-bold', 
    color: 'bg-blue-100 text-blue-600',
    bgColor: 'rgba(59, 130, 246, 0.05)',
    bgColorHex: 0xf0f9ff,
    ambientColor: 0x93c5fd
  },
  { 
    id: 'mountain', 
    name: '高山之巅', 
    description: '登高望远，情怀永存', 
    icon: 'solar:mountains-bold', 
    color: 'bg-amber-100 text-amber-600',
    bgColor: 'rgba(245, 158, 11, 0.05)',
    bgColorHex: 0xfffbeb,
    ambientColor: 0xfcd34d
  },
  { 
    id: 'starry', 
    name: '星空之下', 
    description: '繁星点点，思念绵绵', 
    icon: 'solar:stars-bold', 
    color: 'bg-purple-100 text-purple-600',
    bgColor: 'rgba(168, 85, 247, 0.05)',
    bgColorHex: 0xfaf5ff,
    ambientColor: 0xc4b5fd
  }
]

const sceneBackgroundStyle = computed(() => ({
  backgroundColor: selectedScene.value?.bgColor || 'transparent'
}))

const sceneBgColor = computed(() => {
  return selectedScene.value?.bgColorHex || 0xFAF7F2
})

const models: Model[] = [
  { id: 'default', name: '先祖雕像', icon: 'solar:user-circle-bold' },
  { id: 'lantern', name: '祈福天灯', icon: 'solar:lamp-2-bold' },
  { id: 'heart', name: '永恒之心', icon: 'solar:heart-lock-bold' },
  { id: 'tree', name: '生命之树', icon: 'solar:tree-bold-duotone' }
]

const selectScene = (scene: Scene) => {
  console.log('选择场景:', scene.name)
  selectedScene.value = scene
}

const selectModel = (model: Model) => {
  console.log('选择模型:', model.name)
  selectedModel.value = model
}

const modelKey = ref(0)

const toggleAutoRotate = () => {
  autoRotate.value = !autoRotate.value
  console.log('自动旋转状态:', autoRotate.value ? '开启' : '关闭')
}

const toggleCandle = () => {
  candleLit.value = !candleLit.value
  console.log('蜡烛状态:', candleLit.value ? '已点亮' : '已熄灭')
  if (candleLit.value) {
    modelKey.value++
  }
}

const onModelLoaded = () => {
  console.log('3D 模型加载成功')
}

const onModelError = (error: string) => {
  console.error('3D 模型加载错误:', error)
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const validateFile = (file: File): string | null => {
  const validExtensions = ['.glb', '.gltf', '.obj', '.fbx']
  const fileName = file.name.toLowerCase()
  const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext))
  
  if (!hasValidExtension) {
    return `不支持的文件格式。请选择 ${validExtensions.join(', ')} 格式的文件。`
  }
  
  const maxSize = 100 * 1024 * 1024
  if (file.size > maxSize) {
    return '文件大小不能超过 100MB。'
  }
  
  return null
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  
  if (files && files.length > 0) {
    const file = files[0]
    const error = validateFile(file)
    
    if (error) {
      importError.value = error
      importFile.value = null
    } else {
      importError.value = ''
      importFile.value = file
      if (!importSceneName.value) {
        importSceneName.value = file.name.replace(/\.[^/.]+$/, '')
      }
    }
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  dragOver.value = false
  
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    const error = validateFile(file)
    
    if (error) {
      importError.value = error
      importFile.value = null
    } else {
      importError.value = ''
      importFile.value = file
      if (!importSceneName.value) {
        importSceneName.value = file.name.replace(/\.[^/.]+$/, '')
      }
    }
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const confirmImport = async () => {
  if (!importFile.value || !importSceneName.value) return
  
  importing.value = true
  
  try {
    const fileUrl = URL.createObjectURL(importFile.value)
    
    const newCustomScene: Scene = {
      id: 'custom-' + Date.now(),
      name: importSceneName.value,
      description: '自定义导入场景',
      icon: 'solar:folder-bold',
      color: 'bg-purple-100 text-purple-600',
      bgColor: 'rgba(168, 85, 247, 0.05)',
      bgColorHex: 0xfaf5ff,
      ambientColor: 0xc4b5fd,
      isCustom: true,
      customUrl: fileUrl
    }
    
    customScenes.value.push(newCustomScene)
    selectedScene.value = newCustomScene
    
    showImportModal.value = false
    importSceneName.value = ''
    importFile.value = null
  } catch (error) {
    importError.value = '导入失败，请重试'
  } finally {
    importing.value = false
  }
}

const deleteCustomScene = (sceneId: string) => {
  const index = customScenes.value.findIndex(s => s.id === sceneId)
  if (index > -1) {
    const scene = customScenes.value[index]
    if (scene.customUrl) {
      URL.revokeObjectURL(scene.customUrl)
    }
    customScenes.value.splice(index, 1)
    if (selectedScene.value?.id === sceneId) {
      selectedScene.value = scenes[0]
    }
  }
}

onMounted(() => {
  selectedScene.value = scenes[0]
  selectedModel.value = models[0]
})
</script>
