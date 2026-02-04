import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomePage.vue'),
      meta: { title: '首页 - 发票管理系统' },
    },
    {
      path: '/upload',
      name: 'upload',
      component: () => import('@/views/UploadPage.vue'),
      meta: { title: '上传发票 - 发票管理系统' },
    },
    {
      path: '/preview',
      name: 'preview',
      component: () => import('@/views/PreviewPage.vue'),
      meta: { title: '发票预览与处理 - 发票管理系统' },
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('@/views/HomePage.vue'), // TODO: 创建历史记录页面
      meta: { title: '历史记录 - 发票管理系统' },
    },
  ],
})

// 路由守卫 - 更新页面标题
router.beforeEach((to, _from, next) => {
  document.title = (to.meta.title as string) || '发票管理系统'
  next()
})

export default router
