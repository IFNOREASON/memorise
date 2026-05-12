<script setup lang="ts">
import AppHeader from './components/AppHeader.vue'
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const shouldShowHeader = computed(() => {
  return route.path !== '/login' && route.path !== '/register'
})
</script>

<template>
  <div class="min-h-screen">
    <AppHeader v-if="shouldShowHeader" />
    <RouterView />
  </div>
</template>
