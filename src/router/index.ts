import { createRouter, createWebHistory } from 'vue-router'
import WebHomePage from '../components/WebHomePage.vue'
import ZupuPage from '../components/ZupuPage.vue'
import GalleryPage from '../components/GalleryPage.vue'
import ImageRepairPage from '../components/ImageRepairPage.vue'

const routes = [
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
