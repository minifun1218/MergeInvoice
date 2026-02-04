<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()
const searchQuery = ref('')
const showUserMenu = ref(false)

const navItems = [
  { path: '/', label: '首页', icon: 'home' },
  { path: '/upload', label: '上传发票', icon: 'upload_file' },
  { path: '/history', label: '历史记录', icon: 'history' },
]

function isActive(path: string): boolean {
  return route.path === path
}

function handleLogout() {
  userStore.logout()
  showUserMenu.value = false
}

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

function closeUserMenu() {
  showUserMenu.value = false
}
</script>

<template>
  <header
    class="flex items-center justify-between whitespace-nowrap border-b border-solid border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-10 py-3 sticky top-0 z-50"
  >
    <div class="flex items-center gap-8">
      <router-link to="/" class="flex items-center gap-4 text-primary">
        <div class="size-8">
          <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
            <path
              clip-rule="evenodd"
              d="M24 4H42V17.3333V30.6667H24V44H6V30.6667V17.3333H24V4Z"
              fill="currentColor"
              fill-rule="evenodd"
            />
          </svg>
        </div>
        <h2 class="text-slate-900 dark:text-white text-lg font-bold leading-tight tracking-[-0.015em]">
          发票智慧管理
        </h2>
      </router-link>

      <label class="flex flex-col min-w-40 h-10 max-w-64">
        <div class="flex w-full flex-1 items-stretch rounded-lg h-full">
          <div
            class="text-slate-500 flex border-none bg-slate-100 dark:bg-slate-800 items-center justify-center pl-4 rounded-l-lg"
          >
            <span class="material-symbols-outlined">search</span>
          </div>
          <input
            v-model="searchQuery"
            class="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-slate-900 dark:text-white focus:outline-0 focus:ring-0 border-none bg-slate-100 dark:bg-slate-800 h-full placeholder:text-slate-500 px-4 rounded-l-none pl-2 text-base font-normal"
            placeholder="搜索发票或记录"
          />
        </div>
      </label>
    </div>

    <div class="flex flex-1 justify-end gap-8">
      <nav class="flex items-center gap-9">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'text-sm font-medium leading-normal transition-colors',
            isActive(item.path)
              ? 'text-primary font-bold border-b-2 border-primary pb-1'
              : 'text-slate-600 dark:text-slate-300 hover:text-primary',
          ]"
        >
          {{ item.label }}
        </router-link>
      </nav>

      <div class="flex gap-2">
        <button
          class="flex cursor-pointer items-center justify-center rounded-lg h-10 w-10 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
        >
          <span class="material-symbols-outlined">notifications</span>
        </button>

        <!-- 已登录状态 -->
        <div v-if="userStore.isLoggedIn" class="relative">
          <button
            @click="toggleUserMenu"
            class="flex cursor-pointer items-center gap-2 rounded-lg h-10 px-3 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          >
            <img
              v-if="userStore.user?.avatar"
              :src="userStore.user.avatar"
              class="w-6 h-6 rounded-full"
            />
            <span v-else class="material-symbols-outlined">account_circle</span>
            <span class="text-sm font-medium max-w-20 truncate">{{ userStore.user?.nickname || userStore.user?.username }}</span>
            <span class="material-symbols-outlined text-sm">expand_more</span>
          </button>

          <!-- 用户下拉菜单 -->
          <Transition name="dropdown">
            <div
              v-if="showUserMenu"
              class="absolute right-0 top-12 w-48 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-2 z-50"
              @mouseleave="closeUserMenu"
            >
              <div class="px-4 py-2 border-b border-slate-100 dark:border-slate-700">
                <p class="text-sm font-medium text-slate-900 dark:text-white truncate">{{ userStore.user?.nickname || userStore.user?.username }}</p>
                <p class="text-xs text-slate-500 truncate">{{ userStore.user?.email }}</p>
              </div>
              <a href="#" class="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700">
                <span class="material-symbols-outlined text-lg">person</span>
                个人中心
              </a>
              <a href="#" class="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700">
                <span class="material-symbols-outlined text-lg">settings</span>
                账户设置
              </a>
              <div class="border-t border-slate-100 dark:border-slate-700 mt-2 pt-2">
                <button
                  @click="handleLogout"
                  class="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <span class="material-symbols-outlined text-lg">logout</span>
                  退出登录
                </button>
              </div>
            </div>
          </Transition>
        </div>

        <!-- 未登录状态 -->
        <template v-else>
          <button
            @click="userStore.openLoginModal"
            class="flex cursor-pointer items-center justify-center rounded-lg h-10 px-4 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors text-sm font-medium"
          >
            登录
          </button>
          <button
            @click="userStore.openRegisterModal"
            class="flex cursor-pointer items-center justify-center rounded-lg h-10 px-4 bg-primary text-white hover:bg-primary/90 transition-colors text-sm font-medium"
          >
            注册
          </button>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
