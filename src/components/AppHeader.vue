<template>
  <header class="sticky top-0 z-50 glass-warm border-b border-[#E8D5C4]">
    <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-4 cursor-pointer" @click="goToRoute('/')">
        <div class="w-12 h-12 bg-[#C84A3E] rounded-sm flex items-center justify-center shadow-md relative overflow-hidden">
          <div class="absolute inset-0 opacity-30" :style="noisePatternStyle"></div>
          <span class="text-white font-serif text-xl font-bold tracking-widest relative z-10">存</span>
        </div>
        <div>
          <h1 class="text-2xl font-bold text-[#5C4A3A] font-serif tracking-wider">memorise</h1>
          <p class="text-xs text-gray-500 tracking-[0.15em] uppercase font-medium">Family Memorial</p>
        </div>
      </div>

      <nav class="hidden lg:flex items-center space-x-4">
        <button v-for="item in navItems" :key="item.id"
          class="flex items-center space-x-2 px-3 py-2 rounded-lg transition-all hover:bg-[#E8D5C4]/50"
          :class="[
            isActiveNav(item.id) ? 'bg-[#E8D5C4] text-[#8B6F4E]' : 'text-gray-600'
          ]"
          @click="goToRoute(item.path)">
          <Icon :icon="item.icon" class="text-lg" />
          <span class="font-medium text-sm">{{ item.label }}</span>
        </button>
      </nav>

      <div class="flex items-center space-x-4">
        <button @click="goToMessages" class="relative w-10 h-10 rounded-full bg-white/80 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow">
          <Icon icon="solar:bell-bold" class="text-gray-600" />
          <span v-if="unreadMessageCount > 0" class="absolute -top-1 -right-1 w-5 h-5 bg-[#C84A3E] text-white text-xs font-bold rounded-full flex items-center justify-center">
            {{ unreadMessageCount > 99 ? '99+' : unreadMessageCount }}
          </span>
        </button>
        <div class="relative flex items-center space-x-3 pl-4 border-l border-[#E8D5C4]">
          <button 
            @click="toggleUserMenu"
            class="flex items-center space-x-3 focus:outline-none"
          >
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-[#E8D5C4] to-[#D4A574] p-0.5">
              <div class="w-full h-full rounded-full bg-gray-200 overflow-hidden">
                <img 
                  :src="authStore.user?.avatarUrl || 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face'" 
                  class="w-full h-full object-cover" 
                  alt="用户头像"
                >
              </div>
            </div>
            <div class="hidden md:block text-left">
              <p class="text-sm font-semibold text-gray-800">{{ authStore.user?.nickname || authStore.user?.username || '用户' }}</p>
              <p class="text-xs text-gray-500">{{ authStore.isAuthenticated ? '已登录' : '未登录' }}</p>
            </div>
            <Icon 
              icon="solar:alt-arrow-down-linear" 
              class="text-gray-400 text-sm transition-transform"
              :class="{ 'rotate-180': showUserMenu }"
            />
          </button>

          <div 
            v-if="showUserMenu"
            class="absolute right-0 top-full mt-2 w-48 bg-white rounded-xl shadow-lg border border-[#E8D5C4] py-2 z-50"
          >
            <template v-if="authStore.isAuthenticated">
              <div class="px-4 py-3 border-b border-[#E8D5C4]">
                <p class="text-sm font-medium text-[#5C4A3A]">
                  {{ authStore.user?.nickname || authStore.user?.username }}
                </p>
              </div>
              <button
                @click="handleChangePassword"
                class="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-[#FAF7F2] flex items-center space-x-3 transition-colors"
              >
                <Icon icon="solar:lock-password-bold" class="text-[#8B6F4E]" />
                <span>修改密码</span>
              </button>
              <div class="border-t border-[#E8D5C4] my-1"></div>
              <button
                @click="handleLogout"
                class="w-full px-4 py-3 text-left text-sm text-red-500 hover:bg-red-50 flex items-center space-x-3 transition-colors"
              >
                <Icon icon="solar:logout-3-bold" />
                <span>退出登录</span>
              </button>
            </template>
            <template v-else>
              <button
                @click="handleLogin"
                class="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-[#FAF7F2] flex items-center space-x-3 transition-colors"
              >
                <Icon icon="solar:login-3-bold" class="text-[#8B6F4E]" />
                <span>登录</span>
              </button>
              <button
                @click="handleRegister"
                class="w-full px-4 py-3 text-left text-sm text-gray-700 hover:bg-[#FAF7F2] flex items-center space-x-3 transition-colors"
              >
                <Icon icon="solar:user-add-bold" class="text-[#8B6F4E]" />
                <span>注册</span>
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div 
        v-if="showChangePasswordModal"
        class="fixed inset-0 z-[100] flex items-center justify-center"
      >
        <div 
          class="absolute inset-0 bg-black/50 backdrop-blur-sm"
          @click="closeChangePasswordModal"
        ></div>
        
        <div class="relative w-full max-w-md mx-4 bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div class="bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] px-6 py-4">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-bold text-white font-serif">
                {{ changePasswordStep === 1 ? '验证身份' : '修改密码' }}
              </h3>
              <button 
                @click="closeChangePasswordModal"
                class="text-white/80 hover:text-white transition-colors"
              >
                <Icon icon="solar:close-circle-bold" class="text-xl" />
              </button>
            </div>
            <div class="flex items-center mt-3 space-x-2">
              <div 
                class="flex items-center space-x-2"
                :class="changePasswordStep >= 1 ? 'text-white' : 'text-white/50'"
              >
                <div 
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                  :class="changePasswordStep >= 1 ? 'bg-white text-[#8B6F4E]' : 'bg-white/30'"
                >
                  1
                </div>
                <span class="text-sm">验证原密码</span>
              </div>
              <div class="flex-1 h-0.5 mx-2" 
                   :class="changePasswordStep >= 2 ? 'bg-white' : 'bg-white/30'"></div>
              <div 
                class="flex items-center space-x-2"
                :class="changePasswordStep >= 2 ? 'text-white' : 'text-white/50'"
              >
                <div 
                  class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                  :class="changePasswordStep >= 2 ? 'bg-white text-[#8B6F4E]' : 'bg-white/30'"
                >
                  2
                </div>
                <span class="text-sm">设置新密码</span>
              </div>
            </div>
          </div>

          <div class="p-6">
            <template v-if="changePasswordStep === 1">
              <p class="text-sm text-gray-500 mb-6">请输入您的原密码以验证身份</p>
              
              <div class="space-y-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">原密码</label>
                  <div class="relative">
                    <Icon icon="solar:lock-password-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
                    <input
                      v-model="currentPassword"
                      :type="showCurrentPassword ? 'text' : 'password'"
                      placeholder="请输入原密码"
                      class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                      @keyup.enter="verifyCurrentPassword"
                    />
                    <button
                      type="button"
                      @click="showCurrentPassword = !showCurrentPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <Icon :icon="showCurrentPassword ? 'solar:eye-bold' : 'solar:eye-closed-bold'" class="text-lg" />
                    </button>
                  </div>
                </div>
              </div>
            </template>

            <template v-else-if="changePasswordStep === 2">
              <p class="text-sm text-gray-500 mb-6">请设置您的新密码</p>
              
              <div class="space-y-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">新密码</label>
                  <div class="relative">
                    <Icon icon="solar:lock-password-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
                    <input
                      v-model="newPassword"
                      :type="showNewPassword ? 'text' : 'password'"
                      placeholder="请输入新密码"
                      class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                      @keyup.enter="handleConfirmChangePassword"
                    />
                    <button
                      type="button"
                      @click="showNewPassword = !showNewPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <Icon :icon="showNewPassword ? 'solar:eye-bold' : 'solar:eye-closed-bold'" class="text-lg" />
                    </button>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">确认新密码</label>
                  <div class="relative">
                    <Icon icon="solar:lock-password-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
                    <input
                      v-model="confirmPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      placeholder="请再次输入新密码"
                      class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                      @keyup.enter="handleConfirmChangePassword"
                    />
                    <button
                      type="button"
                      @click="showConfirmPassword = !showConfirmPassword"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                    >
                      <Icon :icon="showConfirmPassword ? 'solar:eye-bold' : 'solar:eye-closed-bold'" class="text-lg" />
                    </button>
                  </div>
                </div>
              </div>
            </template>

            <div v-if="changePasswordError" class="mt-4 text-red-500 text-sm text-center py-2 bg-red-50 rounded-lg">
              {{ changePasswordError }}
            </div>

            <div v-if="changePasswordSuccess" class="mt-4 text-green-500 text-sm text-center py-2 bg-green-50 rounded-lg">
              {{ changePasswordSuccess }}
            </div>

            <div class="mt-6 flex space-x-3">
              <template v-if="changePasswordStep === 1">
                <button
                  @click="closeChangePasswordModal"
                  class="flex-1 py-3 border border-[#E8D5C4] text-gray-600 font-medium rounded-xl hover:bg-[#FAF7F2] transition-all"
                >
                  取消
                </button>
                <button
                  @click="verifyCurrentPassword"
                  :disabled="changePasswordLoading"
                  class="flex-1 py-3 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white font-medium rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <Icon v-if="changePasswordLoading" icon="solar:refresh-circle-bold" class="animate-spin mr-2" />
                  {{ changePasswordLoading ? '验证中...' : '下一步' }}
                </button>
              </template>
              <template v-else-if="changePasswordStep === 2">
                <button
                  @click="goBackToStep1"
                  class="flex-1 py-3 border border-[#E8D5C4] text-gray-600 font-medium rounded-xl hover:bg-[#FAF7F2] transition-all flex items-center justify-center"
                >
                  <Icon icon="solar:arrow-left-linear" class="mr-1" />
                  上一步
                </button>
                <button
                  @click="handleConfirmChangePassword"
                  :disabled="changePasswordLoading"
                  class="flex-1 py-3 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white font-medium rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  <Icon v-if="changePasswordLoading" icon="solar:refresh-circle-bold" class="animate-spin mr-2" />
                  {{ changePasswordLoading ? '修改中...' : '确认修改' }}
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import { authStore, apiService, type ChangePasswordRequest } from '../services/api'

const router = useRouter()
const route = useRoute()

const showUserMenu = ref(false)

const showChangePasswordModal = ref(false)
const changePasswordStep = ref(1)
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const changePasswordLoading = ref(false)
const changePasswordError = ref('')
const changePasswordSuccess = ref('')
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const unreadMessageCount = ref(0)
let messagePollingInterval: number | null = null

const loadUnreadMessageCount = async () => {
  if (!authStore.isAuthenticated) {
    unreadMessageCount.value = 0
    return
  }
  try {
    const response = await apiService.getUnreadCount()
    if (response.success && response.data) {
      unreadMessageCount.value = response.data.count
    }
  } catch (error) {
    console.error('获取未读消息数失败:', error)
  }
}

const goToMessages = () => {
  router.push('/messages')
}

const navItems = [
  { id: 'home', label: '首页', icon: 'solar:home-2-bold', path: '/' },
  { id: 'family', label: '家承', icon: 'solar:tree-bold-duotone', path: '/zupu' },
  { id: 'gallery', label: '影集', icon: 'solar:gallery-wide-bold-duotone', path: '/gallery' },
  { id: 'digital', label: '生境', icon: 'solar:magic-stick-3-bold-duotone', path: '/habitat' },
  { id: 'chat', label: '语伴', icon: 'solar:chat-round-dots-bold-duotone', path: '/chat' },
  { id: 'space', label: '念境', icon: 'solar:heart-lock-bold-duotone', path: '/space' },
]

const isActiveNav = (navId: string): boolean => {
  const path = route.path
  if (navId === 'home') {
    return path === '/'
  } else if (navId === 'family') {
    return path === '/zupu' || path.startsWith('/family/')
  } else if (navId === 'gallery') {
    return path === '/gallery' || path.startsWith('/gallery/')
  } else if (navId === 'digital') {
    return path === '/habitat'
  } else if (navId === 'chat') {
    return path === '/chat'
  } else if (navId === 'space') {
    return path === '/space'
  }
  return false
}

const goToRoute = (path: string) => {
  showUserMenu.value = false
  router.push(path)
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const closeUserMenu = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    showUserMenu.value = false
  }
}

const handleChangePassword = () => {
  showUserMenu.value = false
  openChangePasswordModal()
}

const openChangePasswordModal = () => {
  showChangePasswordModal.value = true
  changePasswordStep.value = 1
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  changePasswordError.value = ''
  changePasswordSuccess.value = ''
  changePasswordLoading.value = false
  showCurrentPassword.value = false
  showNewPassword.value = false
  showConfirmPassword.value = false
}

const closeChangePasswordModal = () => {
  showChangePasswordModal.value = false
  changePasswordStep.value = 1
  currentPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  changePasswordError.value = ''
  changePasswordSuccess.value = ''
  changePasswordLoading.value = false
}

const verifyCurrentPassword = async () => {
  if (!currentPassword.value) {
    changePasswordError.value = '请输入原密码'
    return
  }

  changePasswordLoading.value = true
  changePasswordError.value = ''

  try {
    const result = await apiService.verifyPassword(currentPassword.value)
    if (result.success) {
      changePasswordStep.value = 2
      changePasswordError.value = ''
    } else {
      changePasswordError.value = result.error || '密码错误'
    }
  } catch (e) {
    changePasswordError.value = '验证密码时发生错误，请稍后重试'
  } finally {
    changePasswordLoading.value = false
  }
}

const handleConfirmChangePassword = async () => {
  if (!newPassword.value || !confirmPassword.value) {
    changePasswordError.value = '请填写所有密码字段'
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    changePasswordError.value = '两次输入的新密码不一致'
    return
  }

  if (newPassword.value.length < 6) {
    changePasswordError.value = '新密码长度至少为6位'
    return
  }

  changePasswordLoading.value = true
  changePasswordError.value = ''

  try {
    const request: ChangePasswordRequest = {
      currentPassword: currentPassword.value,
      newPassword: newPassword.value,
      confirmPassword: confirmPassword.value
    }

    const result = await apiService.changePassword(request)
    if (result.success) {
      changePasswordSuccess.value = '密码修改成功，请重新登录'
      changePasswordError.value = ''
      
      setTimeout(() => {
        authStore.clearAuth()
        closeChangePasswordModal()
        router.push('/login')
      }, 2000)
    } else {
      changePasswordError.value = result.error || '密码修改失败'
    }
  } catch (e) {
    changePasswordError.value = '修改密码时发生错误，请稍后重试'
  } finally {
    changePasswordLoading.value = false
  }
}

const goBackToStep1 = () => {
  changePasswordStep.value = 1
  newPassword.value = ''
  confirmPassword.value = ''
  changePasswordError.value = ''
  changePasswordSuccess.value = ''
}

const handleLogout = () => {
  showUserMenu.value = false
  authStore.clearAuth()
  router.push('/login')
}

const handleLogin = () => {
  showUserMenu.value = false
  router.push('/login')
}

const handleRegister = () => {
  showUserMenu.value = false
  router.push('/register')
}

onMounted(() => {
  document.addEventListener('click', closeUserMenu)
  loadUnreadMessageCount()
  messagePollingInterval = window.setInterval(() => {
    loadUnreadMessageCount()
  }, 60000)
})

onUnmounted(() => {
  document.removeEventListener('click', closeUserMenu)
  if (messagePollingInterval) {
    window.clearInterval(messagePollingInterval)
    messagePollingInterval = null
  }
})

const noisePatternStyle = computed(() => ({
  backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox=%220 0 100 100%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22 opacity=%220.3%22/%3E%3C/svg%3E")`
}))
</script>
