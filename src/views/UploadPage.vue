<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useInvoiceStore } from '@/stores/invoice'
import { batchUpload } from '@/utils/upload'
import type { UploadFileItem } from '@/types/invoice'

const router = useRouter()
const invoiceStore = useInvoiceStore()

const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

const uploadQueue = computed(() => invoiceStore.uploadQueue)

// 文件类型图标
function getFileIcon(fileType: string) {
  if (fileType.includes('pdf')) return { icon: 'picture_as_pdf', color: 'text-red-500' }
  if (fileType.includes('image')) return { icon: 'image', color: 'text-blue-500' }
  return { icon: 'receipt', color: 'text-primary' }
}

// 格式化文件大小
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// 获取状态文本
function getStatusText(item: UploadFileItem): string {
  switch (item.status) {
    case 'ready':
      return '就绪'
    case 'uploading':
      return `${item.progress}%`
    case 'success':
      return '完成'
    case 'error':
      return '失败'
    default:
      return ''
  }
}

// 处理文件选择
function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files) {
    addFiles(Array.from(input.files))
  }
  input.value = '' // 重置以便重复选择同一文件
}

// 处理拖放
function handleDrop(event: DragEvent) {
  isDragging.value = false
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

// 添加文件到队列
function addFiles(files: File[]) {
  const validFiles = files.filter((file) => {
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
    const maxSize = 10 * 1024 * 1024 // 10MB
    return validTypes.includes(file.type) && file.size <= maxSize
  })
  invoiceStore.addToUploadQueue(validFiles)
}

// 移除文件
function removeFile(id: string) {
  invoiceStore.removeFromUploadQueue(id)
}

// 清空队列
function clearQueue() {
  invoiceStore.clearUploadQueue()
}

// 触发文件选择
function triggerFileInput() {
  fileInputRef.value?.click()
}

// 开始上传
async function startUpload() {
  const files = uploadQueue.value.map((item) => item.file)
  if (files.length === 0) return

  // 更新所有状态为上传中
  uploadQueue.value.forEach((item) => {
    invoiceStore.updateUploadProgress(item.id, 0, 'uploading')
  })

  // 并发上传
  await batchUpload(
    files,
    (fileIndex, progress) => {
      const item = uploadQueue.value[fileIndex]
      if (item) {
        invoiceStore.updateUploadProgress(item.id, progress, 'uploading')
      }
    },
    (results) => {
      results.forEach((result, index) => {
        const item = uploadQueue.value[index]
        if (item) {
          invoiceStore.updateUploadProgress(item.id, 100, result.success ? 'success' : 'error')
        }
      })
    },
  )

  // 上传完成后跳转到预览页
  setTimeout(() => {
    router.push('/preview')
  }, 1000)
}

// 计算是否有正在上传的文件
const isUploading = computed(() => {
  return uploadQueue.value.some((item) => item.status === 'uploading')
})
</script>

<template>
  <main class="flex-1 flex flex-col items-center">
    <div class="w-full max-w-[960px] px-4 py-8">
      <!-- Breadcrumbs -->
      <nav class="flex flex-wrap gap-2 py-4 mb-2">
        <router-link
          to="/"
          class="text-slate-500 dark:text-slate-400 text-sm font-medium leading-normal hover:text-primary transition-colors"
        >
          首页
        </router-link>
        <span class="text-slate-500 dark:text-slate-600 text-sm font-medium leading-normal">/</span>
        <span class="text-slate-900 dark:text-white text-sm font-medium leading-normal">发票上传</span>
      </nav>

      <!-- Headline -->
      <div class="text-center mb-10">
        <h1 class="text-slate-900 dark:text-white tracking-tight text-3xl font-bold leading-tight pb-2">
          上传发票
        </h1>
        <p class="text-slate-500 dark:text-slate-400 text-base font-normal leading-normal max-w-2xl mx-auto">
          请上传您的PDF、JPG或PNG格式的发票文件。系统将自动提取日期、金额及税号等核心财务信息，提高您的报销效率。
        </p>
      </div>

      <!-- Upload Area -->
      <div class="flex flex-col mb-12">
        <div
          @dragover.prevent="isDragging = true"
          @dragleave.prevent="isDragging = false"
          @drop.prevent="handleDrop"
          :class="[
            'flex flex-col items-center gap-6 rounded-xl border-2 border-dashed px-6 py-20 transition-all',
            isDragging
              ? 'border-primary bg-primary/5'
              : 'border-primary/40 dark:border-primary/30 bg-white dark:bg-slate-900/50 hover:border-primary',
          ]"
        >
          <div class="size-16 rounded-full bg-primary/10 flex items-center justify-center text-primary">
            <span class="material-symbols-outlined text-4xl">cloud_upload</span>
          </div>
          <div class="flex flex-col items-center gap-2">
            <p
              class="text-slate-900 dark:text-white text-xl font-bold leading-tight tracking-[-0.015em] text-center"
            >
              点击或将文件拖拽到此处上传
            </p>
            <p class="text-slate-500 dark:text-slate-400 text-sm font-normal leading-normal text-center">
              支持 PDF, JPG, PNG 格式 (单个文件不超过10MB)
            </p>
          </div>
          <div class="flex gap-3">
            <input
              ref="fileInputRef"
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png"
              class="hidden"
              @change="handleFileSelect"
            />
            <button
              @click="triggerFileInput"
              class="flex min-w-[120px] cursor-pointer items-center justify-center rounded-lg h-11 px-6 bg-primary text-white text-sm font-bold leading-normal tracking-[0.015em] hover:bg-primary/90 transition-colors"
            >
              浏览本地文件
            </button>
            <button
              class="flex min-w-[120px] cursor-pointer items-center justify-center rounded-lg h-11 px-6 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white text-sm font-bold leading-normal tracking-[0.015em] hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              扫描二维码上传
            </button>
          </div>
        </div>
      </div>

      <!-- Queued Files List -->
      <div v-if="uploadQueue.length > 0" class="flex flex-col gap-4">
        <div class="flex items-center justify-between px-4">
          <h3 class="text-lg font-bold text-slate-900 dark:text-white">
            待处理列表 ({{ uploadQueue.length }})
          </h3>
          <button @click="clearQueue" class="text-primary text-sm font-semibold hover:underline">
            全部清空
          </button>
        </div>

        <div class="space-y-3">
          <div
            v-for="item in uploadQueue"
            :key="item.id"
            class="flex items-center gap-4 p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700"
          >
            <div
              :class="[
                'size-10 bg-slate-100 dark:bg-slate-700 rounded flex items-center justify-center',
                getFileIcon(item.fileType).color,
              ]"
            >
              <span class="material-symbols-outlined">{{ getFileIcon(item.fileType).icon }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-slate-900 dark:text-white truncate">
                {{ item.fileName }}
              </p>
              <template v-if="item.status === 'uploading'">
                <div
                  class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full mt-2 overflow-hidden"
                >
                  <div
                    class="bg-primary h-full rounded-full transition-all"
                    :style="{ width: `${item.progress}%` }"
                  ></div>
                </div>
              </template>
              <template v-else>
                <p class="text-xs text-slate-500 dark:text-slate-400">
                  {{ formatFileSize(item.fileSize) }} · {{ getStatusText(item) }}
                </p>
              </template>
            </div>
            <div class="flex items-center gap-2">
              <template v-if="item.status === 'uploading'">
                <span class="text-xs font-medium text-primary">{{ item.progress }}%</span>
              </template>
              <template v-else-if="item.status === 'success'">
                <span class="material-symbols-outlined text-green-500">check_circle</span>
              </template>
              <template v-else-if="item.status === 'error'">
                <span class="material-symbols-outlined text-red-500">error</span>
              </template>
              <template v-else>
                <span
                  @click="removeFile(item.id)"
                  class="material-symbols-outlined text-slate-400 cursor-pointer hover:text-red-500 transition-colors"
                >
                  delete
                </span>
              </template>
            </div>
          </div>
        </div>

        <div class="flex justify-center mt-8">
          <button
            @click="startUpload"
            :disabled="isUploading || uploadQueue.length === 0"
            :class="[
              'flex min-w-[240px] cursor-pointer items-center justify-center rounded-lg h-12 px-8 text-white text-base font-bold leading-normal tracking-[0.015em] shadow-lg transition-all',
              isUploading
                ? 'bg-slate-400 cursor-not-allowed'
                : 'bg-primary shadow-primary/20 hover:scale-[1.02] active:scale-[0.98]',
            ]"
          >
            <span class="material-symbols-outlined mr-2">send</span>
            {{ isUploading ? '上传中...' : '开始解析并提交' }}
          </button>
        </div>
      </div>

      <!-- Footer Tip -->
      <div class="mt-16 text-center">
        <div
          class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-50 dark:bg-primary/10 border border-blue-100 dark:border-primary/20"
        >
          <span class="material-symbols-outlined text-primary text-sm">info</span>
          <span class="text-xs text-slate-500 dark:text-slate-400 font-medium">
            提示：上传后系统将通过 OCR 识别发票代码、号码、金额及日期
          </span>
        </div>
      </div>
    </div>
  </main>
</template>
