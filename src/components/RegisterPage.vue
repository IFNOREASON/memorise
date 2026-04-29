<template>
  <div class="min-h-screen paper-texture flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center mb-4">
          <div class="w-16 h-16 bg-[#C84A3E] rounded-sm flex items-center justify-center shadow-md relative overflow-hidden">
            <span class="text-white font-serif text-2xl font-bold tracking-widest relative z-10">存</span>
          </div>
        </div>
        <h1 class="text-3xl font-bold text-[#5C4A3A] font-serif tracking-wider">memorise</h1>
        <p class="text-sm text-gray-500 tracking-[0.15em] uppercase font-medium mt-1">Family Memorial</p>
      </div>

      <div class="bg-white rounded-2xl shadow-soft border border-stone-100 p-8">
        <h2 class="text-xl font-bold text-[#5C4A3A] font-serif mb-6 text-center">创建账号</h2>

        <form @submit.prevent="handleRegister" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">用户名</label>
            <div class="relative">
              <Icon icon="solar:user-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                v-model="form.username"
                type="text"
                placeholder="请输入用户名（字母、数字、下划线）"
                class="w-full pl-10 pr-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                required
              />
            </div>
            <p v-if="errors.username" class="text-red-500 text-xs mt-1">{{ errors.username }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">昵称 <span class="text-gray-400">（选填）</span></label>
            <div class="relative">
              <Icon icon="solar:smile-circle-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                v-model="form.nickname"
                type="text"
                placeholder="请输入昵称"
                class="w-full pl-10 pr-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
            <div class="relative">
              <Icon icon="solar:lock-password-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码（至少6位）"
                class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                required
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Icon :icon="showPassword ? 'solar:eye-bold' : 'solar:eye-closed-bold'" class="text-lg" />
              </button>
            </div>
            <p v-if="errors.password" class="text-red-500 text-xs mt-1">{{ errors.password }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">确认密码</label>
            <div class="relative">
              <Icon icon="solar:lock-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="请再次输入密码"
                class="w-full pl-10 pr-12 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                required
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <Icon :icon="showConfirmPassword ? 'solar:eye-bold' : 'solar:eye-closed-bold'" class="text-lg" />
              </button>
            </div>
            <p v-if="errors.confirmPassword" class="text-red-500 text-xs mt-1">{{ errors.confirmPassword }}</p>
          </div>

          <div v-if="error" class="text-red-500 text-sm text-center py-2 bg-red-50 rounded-lg">
            {{ error }}
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 bg-gradient-to-r from-[#8B6F4E] to-[#A67B5B] text-white font-medium rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <Icon v-if="loading" icon="solar:refresh-circle-bold" class="animate-spin mr-2" />
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-sm text-gray-500">
            已有账号？
            <router-link to="/login" class="text-[#8B6F4E] font-medium hover:underline">
              立即登录
            </router-link>
          </p>
        </div>
      </div>

      <div class="mt-6 text-center">
        <router-link to="/" class="text-sm text-gray-400 hover:text-gray-600 flex items-center justify-center">
          <Icon icon="solar:arrow-left-linear" class="mr-1" />
          返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { apiService } from '../services/api'

const router = useRouter()

const form = ref({
  username: '',
  nickname: '',
  password: '',
  confirmPassword: ''
})

const errors = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const error = ref('')

const validateForm = (): boolean => {
  errors.username = ''
  errors.password = ''
  errors.confirmPassword = ''
  error.value = ''

  if (!form.value.username) {
    errors.username = '请输入用户名'
    return false
  }

  if (form.value.username.length < 3) {
    errors.username = '用户名至少3个字符'
    return false
  }

  if (!/^[a-zA-Z0-9_]+$/.test(form.value.username)) {
    errors.username = '用户名只能包含字母、数字和下划线'
    return false
  }

  if (!form.value.password) {
    errors.password = '请输入密码'
    return false
  }

  if (form.value.password.length < 6) {
    errors.password = '密码至少6个字符'
    return false
  }

  if (form.value.password !== form.value.confirmPassword) {
    errors.confirmPassword = '两次输入的密码不一致'
    return false
  }

  return true
}

const handleRegister = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true
  error.value = ''

  try {
    const result = await apiService.register({
      username: form.value.username,
      password: form.value.password,
      confirmPassword: form.value.confirmPassword,
      nickname: form.value.nickname || undefined
    })
    if (result.success) {
      router.push('/login?registered=true')
    } else {
      error.value = result.error || '注册失败'
    }
  } catch (e) {
    error.value = '注册时发生错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
