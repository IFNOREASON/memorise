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
    component: ZupuPage
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
