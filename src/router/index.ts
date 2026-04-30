import { createRouter, createWebHistory } from 'vue-router'
import WebHomePage from '../components/WebHomePage.vue'
import ZupuPage from '../components/ZupuPage.vue'
import GalleryPage from '../components/GalleryPage.vue'
import ImageRepairPage from '../components/ImageRepairPage.vue'
import HabitatPage from '../components/HabitatPage.vue'
import MemoryListPage from '../components/MemoryListPage.vue'
import MemoryEditorPage from '../components/MemoryEditorPage.vue'
import ChatCompanionPage from '../components/ChatCompanionPage.vue'
import LoginPage from '../components/LoginPage.vue'
import RegisterPage from '../components/RegisterPage.vue'
import MemberManagement from '../components/MemberManagement.vue'
import ApprovalList from '../components/ApprovalList.vue'
import OperationLogs from '../components/OperationLogs.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
    meta: { guest: true }
  },
  {
    path: '/',
    name: 'Home',
    component: WebHomePage
  },
  {
    path: '/zupu',
    name: 'Zupu',
    component: ZupuPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: GalleryPage
  },
  {
    path: '/gallery/repair',
    name: 'ImageRepair',
    component: ImageRepairPage
  },
  {
    path: '/habitat',
    name: 'Habitat',
    component: HabitatPage
  },
  {
    path: '/memories',
    name: 'MemoryList',
    component: MemoryListPage
  },
  {
    path: '/memory/create',
    name: 'MemoryCreate',
    component: MemoryEditorPage
  },
  {
    path: '/memory/edit/:id',
    name: 'MemoryEdit',
    component: MemoryEditorPage
  },
  {
    path: '/chat',
    name: 'ChatCompanion',
    component: ChatCompanionPage
  },
  {
    path: '/family/members',
    name: 'MemberManagement',
    component: MemberManagement,
    meta: { requiresAuth: true }
  },
  {
    path: '/family/approvals',
    name: 'ApprovalList',
    component: ApprovalList,
    meta: { requiresAuth: true }
  },
  {
    path: '/family/logs',
    name: 'OperationLogs',
    component: OperationLogs,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

import { authStore } from '../services/api'

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
