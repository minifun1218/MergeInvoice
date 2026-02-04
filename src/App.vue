<script setup lang="ts">
import AppHeader from '@/components/AppHeader.vue'
</script>

<template>
  <div class="relative flex h-auto min-h-screen w-full flex-col overflow-x-hidden bg-slate-50 dark:bg-slate-950">
    <div class="layout-container flex h-full grow flex-col">
      <AppHeader />
      <router-view />

      <!-- Footer -->
      <footer class="mt-auto px-10 py-8 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
        <div class="max-w-[1024px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div class="flex items-center gap-2 text-slate-400">
            <span class="material-symbols-outlined text-sm">copyright</span>
            <p class="text-sm">2024 发票智慧管理系统. 保留所有权利.</p>
          </div>
          <div class="flex gap-6 text-slate-500 dark:text-slate-400 text-sm">
            <a class="hover:text-primary transition-colors" href="#">使用条款</a>
            <a class="hover:text-primary transition-colors" href="#">隐私政策</a>
            <a class="hover:text-primary transition-colors" href="#">帮助中心</a>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

:root {
  --primary: #137fec;
}

body {
  font-family: 'Inter', 'Noto Sans SC', sans-serif;
}

.material-symbols-outlined {
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
</style>
