import { createRouter, createWebHistory } from 'vue-router'
import WebHomePage from '../components/WebHomePage.vue'
import ZupuPage from '../components/ZupuPage.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
