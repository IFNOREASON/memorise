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
        <h2 class="text-xl font-bold text-[#5C4A3A] font-serif mb-6 text-center">欢迎回来</h2>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">用户名</label>
            <div class="relative">
              <Icon icon="solar:user-bold" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                v-model="form.username"
                type="text"
                placeholder="请输入用户名"
                class="w-full pl-10 pr-4 py-3 border border-[#E8D5C4] rounded-xl focus:outline-none focus:ring-2 focus:ring-[#D4A574] focus:border-transparent transition-all bg-[#FAF7F2] placeholder-gray-400"
                required
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
                placeholder="请输入密码"
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
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>

        <div class="mt-6 text-center">
          <p class="text-sm text-gray-500">
            还没有账号？
            <router-link to="/register" class="text-[#8B6F4E] font-medium hover:underline">
              立即注册
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import { apiService, authStore } from '../services/api'

const router = useRouter()

const form = ref({
  username: '',
  password: ''
})

const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    error.value = '请填写用户名和密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const result = await apiService.login(form.value.username, form.value.password)
    if (result.success && result.data) {
      authStore.setToken(result.data.accessToken)
      authStore.setUser(result.data.user)
      router.push('/')
    } else {
      error.value = result.error || '登录失败'
    }
  } catch (e) {
    error.value = '登录时发生错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
