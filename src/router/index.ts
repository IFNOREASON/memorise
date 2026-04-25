import { createRouter, createWebHistory } from 'vue-router'
import WebHomePage from '../components/WebHomePage.vue'
import ZupuPage from '../components/ZupuPage.vue'
import GalleryPage from '../components/GalleryPage.vue'
import ImageRepairPage from '../components/ImageRepairPage.vue'
import HabitatPage from '../components/HabitatPage.vue'

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
  },
  {
    path: '/habitat',
    name: 'Habitat',
    component: HabitatPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
