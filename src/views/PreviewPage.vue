<script setup lang="ts">
import { computed, onMounted, watch, ref } from 'vue'
import { useInvoiceStore } from '@/stores/invoice'
import { useLayoutStore } from '@/stores/layout'
import { createMergeTask, downloadMergedFile, uploadAndMerge, deleteAllInvoices } from '@/api/invoice'

const invoiceStore = useInvoiceStore()
const layoutStore = useLayoutStore()

const outputType = ref<'pdf' | 'zip'>('pdf')
const isGenerating = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const isUploading = ref(false)
const isLoading = ref(false)

// 从 store 获取发票数据和合并后的PDF
const invoices = computed(() => invoiceStore.invoices)
const mergedPdfUrl = computed(() => invoiceStore.mergedPdfUrl)

// 计算总金额
const totalAmount = computed(() => {
  return invoices.value.reduce((sum, inv) => sum + inv.totalAmount, 0)
})

// 计算总页数（每页2个发票）
const totalPages = computed(() => {
  const perPage = layoutStore.invoicesPerPage
  return Math.ceil(invoices.value.length / perPage)
})

// 当前页显示的发票
const currentInvoices = computed(() => {
  const perPage = layoutStore.invoicesPerPage
  const startIndex = (layoutStore.currentPage - 1) * perPage
  const endIndex = Math.min(startIndex + perPage, invoices.value.length)
  return invoices.value.slice(startIndex, endIndex)
})

// 删除发票
async function removeInvoice(id: string) {
  if (!confirm('确定要删除这张发票吗？')) return

  isLoading.value = true
  try {
    // 从store中删除
    invoiceStore.removeInvoice(id)
    console.log('✅ 已从前端删除发票:', id)

    // 如果还有发票，重新合并
    if (invoiceStore.invoices.length > 0) {
      console.log('🔄 重新合并剩余发票，数量:', invoiceStore.invoices.length)

      // 调用后端重新合并所有剩余发票
      const { uploadAndMerge, deleteAllInvoices } = await import('@/api/invoice')

      // 获取所有剩余发票的ID
      const remainingIds = invoiceStore.invoices.map(inv => inv.id)

      // 调用后端API重新生成合并PDF
      // 注意：这里需要一个新的API endpoint来合并已有的发票，或者通过其他方式
      // 暂时的解决方案：调用merge-service
      const { createMergeTask } = await import('@/api/invoice')
      const result = await createMergeTask(remainingIds, 'pdf', '2x1')

      if (result.code === 0 && result.data.downloadUrl) {
        invoiceStore.mergedPdfUrl = result.data.downloadUrl
        console.log('✅ 重新合并完成')
      }
    } else {
      // 没有发票了，清空PDF
      invoiceStore.mergedPdfUrl = ''
      console.log('✅ 所有发票已删除')
    }
  } catch (error) {
    console.error('❌ 删除发票失败:', error)
    alert('删除失败，请重试')
  } finally {
    isLoading.value = false
  }
}

// 格式化金额
function formatMoney(amount: number): string {
  return `¥ ${amount.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
}

// 下载合并后的PDF
function downloadPdf() {
  if (mergedPdfUrl.value) {
    window.open(mergedPdfUrl.value, '_blank')
  }
}

// 触发文件选择
function triggerFileInput() {
  fileInputRef.value?.click()
}

// 处理继续上传文件
async function handleContinueUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return

  const files = Array.from(input.files)
  const validFiles = files.filter((file) => {
    const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
    const maxSize = 10 * 1024 * 1024 // 10MB
    return validTypes.includes(file.type) && file.size <= maxSize
  })

  if (validFiles.length === 0) {
    alert('请选择有效的PDF或图片文件（最大10MB）')
    return
  }

  isUploading.value = true
  isLoading.value = true  // 开启加载状态
  try {
    console.log('📤 继续上传并拼接发票，文件数:', validFiles.length)

    // 调用上传并合并API（会自动拼接到现有发票）
    const result = await uploadAndMerge(validFiles, '2x1')

    if (result.code === 0 && result.data) {
      console.log('✅ 上传并拼接成功')
      console.log('📋 新发票数据:', result.data.invoices)
      console.log('📄 新合并PDF URL:', result.data.mergedPdfUrl)

      // 更新发票列表和合并后的PDF URL
      invoiceStore.invoices = result.data.invoices
      invoiceStore.mergedPdfUrl = result.data.mergedPdfUrl
      invoiceStore.totalPages = result.data.totalPages

      console.log('✅ 拼接完成，当前发票总数:', invoiceStore.invoices.length)
    } else {
      console.error('❌ 上传拼接失败:', result.message)
      alert('上传失败：' + result.message)
    }
  } catch (error) {
    console.error('❌ 上传拼接失败:', error)
    alert('上传失败，请重试')
  } finally {
    isUploading.value = false
    isLoading.value = false  // 关闭加载状态
    input.value = '' // 重置以便重复选择
  }
}

// 生成PDF
async function generatePdf() {
  isGenerating.value = true
  try {
    const invoiceIds = invoices.value.map((inv) => inv.id)
    // 传递当前布局配置到后端
    const result = await createMergeTask(invoiceIds, outputType.value, layoutStore.config.layout)
    console.log('📦 生成PDF请求:', {
      invoiceIds,
      outputType: outputType.value,
      layout: layoutStore.config.layout
    })
    if (result.code === 0 && result.data.id) {
      downloadMergedFile(result.data.id)
    }
  } catch (error) {
    console.error('生成失败:', error)
  } finally {
    isGenerating.value = false
  }
}

// 保存草稿
function saveDraft() {
  // TODO: 实现保存草稿
  console.log('保存草稿')
}

// 监听发票列表变化
watch(
  () => invoices.value,
  () => {
    layoutStore.setTotalPages(totalPages.value)
  },
  { immediate: true, deep: true },
)

onMounted(() => {
  layoutStore.setTotalPages(totalPages.value)
  console.log('📄 预览页面加载完成，发票数量:', invoices.value.length)
})
</script>

<template>
  <main class="flex flex-col px-10 py-5 gap-4">
    <!-- Breadcrumbs -->
    <div class="flex flex-wrap gap-2 py-2">
      <router-link
        to="/"
        class="text-slate-500 text-sm font-medium leading-normal hover:text-primary transition-colors"
      >
        首页
      </router-link>
      <span class="text-slate-500 text-sm font-medium leading-normal">/</span>
      <span class="text-slate-900 dark:text-slate-200 text-sm font-medium leading-normal">
        发票预览与处理
      </span>
    </div>

    <!-- Page Header -->
    <div class="flex flex-wrap justify-between items-center gap-3 py-2">
      <div class="flex min-w-72 flex-col gap-1">
        <p class="text-slate-900 dark:text-white tracking-light text-[32px] font-bold leading-tight">
          发票预览与处理
        </p>
        <p class="text-slate-500 dark:text-slate-400 text-sm font-normal leading-normal">
          预览合并结果并管理发票明细，支持A4规格(2合1)打印排版
        </p>
      </div>
      <div class="flex gap-3">
        <button
          @click="saveDraft"
          class="flex min-w-[100px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-200 text-sm font-medium leading-normal hover:bg-slate-200 transition-colors"
        >
          <span class="truncate">保存草稿</span>
        </button>
        <button
          @click="generatePdf"
          :disabled="isGenerating"
          class="flex min-w-[100px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-primary text-white text-sm font-medium leading-normal shadow-lg shadow-primary/20 hover:bg-primary/90 transition-colors disabled:bg-slate-400"
        >
          <span class="truncate">{{ isGenerating ? '生成中...' : '生成 PDF' }}</span>
        </button>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-12 gap-8 mt-4 items-start">
      <!-- Preview Panel -->
      <div class="col-span-7 flex flex-col gap-4">
        <div class="flex items-center justify-between pb-2">
          <h3 class="text-slate-900 dark:text-white tracking-light text-xl font-bold leading-tight">
            发票预览 ({{ invoices.length }}张)
          </h3>
          <div class="flex items-center gap-3">
            <input
              ref="fileInputRef"
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png"
              class="hidden"
              @change="handleContinueUpload"
            />
            <button
              @click="triggerFileInput"
              :disabled="isUploading"
              class="flex items-center gap-2 px-4 py-2 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-200 text-sm font-medium rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
            >
              <span class="material-symbols-outlined !text-lg">add</span>
              <span>{{ isUploading ? '上传中...' : '继续添加' }}</span>
            </button>
            <button
              v-if="mergedPdfUrl"
              @click="downloadPdf"
              class="flex items-center gap-2 px-4 py-2 bg-primary text-white text-sm font-medium rounded-lg hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20"
            >
              <span class="material-symbols-outlined !text-lg">download</span>
              <span>下载PDF</span>
            </button>
          </div>
        </div>

        <!-- PDF预览区域 - 显示合并后的PDF -->
        <div
          class="relative bg-white dark:bg-slate-900 rounded-xl border border-slate-300 dark:border-slate-800 overflow-hidden shadow-inner"
        >
          <!-- 线性加载进度条 -->
          <div v-if="isLoading" class="absolute top-0 left-0 right-0 z-50">
            <div class="h-1 bg-slate-200 dark:bg-slate-800">
              <div class="h-full bg-primary animate-pulse" style="width: 100%; animation: progress 1.5s ease-in-out infinite;">
              </div>
            </div>
            <div class="absolute top-4 left-0 right-0 flex items-center justify-center">
              <div class="bg-white dark:bg-slate-800 px-6 py-3 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 flex items-center gap-3">
                <div class="w-5 h-5 border-3 border-primary border-t-transparent rounded-full animate-spin"></div>
                <span class="text-sm font-medium text-slate-700 dark:text-slate-300">正在处理并合并发票...</span>
              </div>
            </div>
          </div>

          <div class="h-[750px] overflow-hidden bg-white dark:bg-slate-900">
            <div v-if="!mergedPdfUrl" class="flex flex-col items-center justify-center h-full gap-4">
              <span class="material-symbols-outlined text-slate-400 text-6xl">description</span>
              <p class="text-slate-500">没有合并的PDF文件</p>
              <p class="text-slate-400 text-sm">请先上传发票文件</p>
            </div>

            <!-- 合并后的PDF查看器（2x1布局，隐藏工具栏） -->
            <iframe
              v-else
              :src="mergedPdfUrl + '#toolbar=0&navpanes=0&scrollbar=0'"
              type="application/pdf"
              class="w-full h-full border-0 bg-white"
              :class="{ 'opacity-50': isLoading }"
            ></iframe>
          </div>
        </div>
      </div>

      <!-- Right Panel -->
      <div class="col-span-5 flex flex-col gap-6">
        <!-- Invoice List -->
        <div
          class="flex flex-col bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm"
        >
          <div class="p-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center">
            <h4 class="text-slate-900 dark:text-white font-bold text-sm">
              发票明细 ({{ invoices.length }})
            </h4>
            <span class="text-primary text-xs font-medium cursor-pointer">批量编辑</span>
          </div>
          <!-- 添加固定高度和垂直滚动 -->
          <div class="overflow-x-auto overflow-y-auto max-h-[400px]">
            <table class="w-full text-left text-sm">
              <thead class="sticky top-0 z-10 bg-slate-50 dark:bg-slate-800/50">
                <tr class="text-slate-500">
                  <th class="px-4 py-3 font-medium">序号</th>
                  <th class="px-4 py-3 font-medium">日期</th>
                  <th class="px-4 py-3 font-medium text-right">总金额</th>
                  <th class="px-4 py-3 font-medium text-center">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-800 bg-white dark:bg-slate-900">
                <tr
                  v-for="(invoice, index) in invoices"
                  :key="invoice.id"
                  class="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                >
                  <td class="px-4 py-4 dark:text-slate-300">#{{ index + 1 }}</td>
                  <td class="px-4 py-4 dark:text-slate-300">{{ invoice.date }}</td>
                  <td class="px-4 py-4 text-right font-medium text-slate-900 dark:text-white">
                    {{ formatMoney(invoice.totalAmount) }}
                  </td>
                  <td class="px-4 py-4 text-center">
                    <button
                      @click="removeInvoice(invoice.id)"
                      class="text-slate-500 hover:text-red-500 transition-colors"
                    >
                      <span class="material-symbols-outlined !text-xl">delete</span>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="p-4 bg-slate-50 dark:bg-slate-800/30 border-t border-slate-100 dark:border-slate-800">
            <div class="flex justify-between items-center text-sm">
              <span class="text-slate-500">总计金额</span>
              <span class="text-xl font-bold text-primary">{{ formatMoney(totalAmount) }}</span>
            </div>
          </div>
        </div>

        <!-- Download Options -->
        <div
          class="p-6 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex flex-col gap-4 shadow-sm"
        >
          <h4 class="text-slate-900 dark:text-white font-bold mb-1 text-sm">下载选项</h4>
          <div class="grid grid-cols-1 gap-3">
            <label
              :class="[
                'flex items-center gap-3 p-3 rounded-lg border cursor-pointer group transition-all',
                outputType === 'pdf'
                  ? 'border-primary bg-primary/5 dark:border-primary/50'
                  : 'border-slate-200 dark:border-slate-700 hover:border-primary/50',
              ]"
            >
              <input type="radio" v-model="outputType" value="pdf" class="hidden" />
              <div
                :class="[
                  'size-5 rounded-full border-2 flex items-center justify-center p-1',
                  outputType === 'pdf' ? 'border-primary' : 'border-slate-300 dark:border-slate-600',
                ]"
              >
                <div v-if="outputType === 'pdf'" class="size-full bg-primary rounded-full"></div>
              </div>
              <div class="flex-1">
                <p class="text-sm font-bold text-slate-900 dark:text-white">合并为 PDF (打印推荐)</p>
                <p class="text-xs text-slate-500">2张/页 A4 排版，含文件目录</p>
              </div>
              <span class="material-symbols-outlined text-primary">picture_as_pdf</span>
            </label>

            <label
              :class="[
                'flex items-center gap-3 p-3 rounded-lg border cursor-pointer group transition-all',
                outputType === 'zip'
                  ? 'border-primary bg-primary/5 dark:border-primary/50'
                  : 'border-slate-200 dark:border-slate-700 hover:border-primary/50',
              ]"
            >
              <input type="radio" v-model="outputType" value="zip" class="hidden" />
              <div
                :class="[
                  'size-5 rounded-full border-2 flex items-center justify-center',
                  outputType === 'zip' ? 'border-primary' : 'border-slate-300 dark:border-slate-600',
                ]"
              >
                <div v-if="outputType === 'zip'" class="size-full bg-primary rounded-full"></div>
              </div>
              <div class="flex-1">
                <p class="text-sm font-bold text-slate-900 dark:text-white">原始文件压缩包 (ZIP)</p>
                <p class="text-xs text-slate-500">包含识别出的结构化数据 CSV</p>
              </div>
              <span
                :class="[
                  'material-symbols-outlined',
                  outputType === 'zip' ? 'text-primary' : 'text-slate-300 group-hover:text-primary',
                ]"
              >
                folder_zip
              </span>
            </label>
          </div>

          <button
            @click="generatePdf"
            :disabled="isGenerating || invoices.length === 0"
            class="w-full flex items-center justify-center gap-2 rounded-lg h-12 bg-primary text-white font-bold text-base shadow-lg shadow-primary/30 hover:bg-primary/90 active:scale-[0.98] transition-all disabled:bg-slate-400 disabled:shadow-none"
          >
            <span class="material-symbols-outlined">download</span>
            <span>{{ isGenerating ? '生成中...' : '确认并下载合并文件' }}</span>
          </button>
          <p class="text-[10px] text-center text-slate-500">文件将保留在系统 30 天，请及时保存</p>
        </div>
      </div>
    </div>
  </main>
</template>
