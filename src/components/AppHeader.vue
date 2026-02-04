<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const searchQuery = ref('')

const navItems = [
  { path: '/', label: '首页', icon: 'home' },
  { path: '/upload', label: '上传发票', icon: 'upload_file' },
  { path: '/history', label: '历史记录', icon: 'history' },
]

function isActive(path: string): boolean {
  return route.path === path
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
        <button
          class="flex cursor-pointer items-center justify-center rounded-lg h-10 w-10 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
        >
          <span class="material-symbols-outlined">account_circle</span>
        </button>
      </div>
    </div>
  </header>
</template>
