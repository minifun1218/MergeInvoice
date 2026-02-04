import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'

/** 用户状态管理 */
export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const showAuthModal = ref(false)
  const authModalTab = ref<'login' | 'register'>('login')

  // 是否已登录
  const isLoggedIn = computed(() => !!token.value && !!user.value)

  // 初始化 - 从本地存储恢复
  function init() {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }

  // 设置登录信息
  function setAuth(newToken: string, newUser: User) {
    token.value = newToken
    user.value = newUser
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  // 登出
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 打开登录弹窗
  function openLoginModal() {
    authModalTab.value = 'login'
    showAuthModal.value = true
  }

  // 打开注册弹窗
  function openRegisterModal() {
    authModalTab.value = 'register'
    showAuthModal.value = true
  }

  // 关闭弹窗
  function closeAuthModal() {
    showAuthModal.value = false
  }

  // 切换标签
  function switchTab(tab: 'login' | 'register') {
    authModalTab.value = tab
  }

  return {
    user,
    token,
    showAuthModal,
    authModalTab,
    isLoggedIn,
    init,
    setAuth,
    logout,
    openLoginModal,
    openRegisterModal,
    closeAuthModal,
    switchTab,
  }
})
