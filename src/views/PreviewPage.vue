<script setup lang="ts">
import { computed, onMounted, watch, ref } from 'vue'
import { useInvoiceStore } from '@/stores/invoice'
import { useLayoutStore } from '@/stores/layout'
import { renderPage } from '@/utils/canvas'
import { createMergeTask, downloadMergedFile } from '@/api/invoice'

const invoiceStore = useInvoiceStore()
const layoutStore = useLayoutStore()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const imageCache = new Map<string, HTMLImageElement>()
const outputType = ref<'pdf' | 'zip'>('pdf')
const isGenerating = ref(false)

// 从 store 获取发票数据
const invoices = computed(() => invoiceStore.invoices)

// 计算总金额
const totalAmount = computed(() => {
  return invoices.value.reduce((sum, inv) => sum + inv.totalAmount, 0)
})

// 计算总页数
const totalPages = computed(() => {
  const perPage = layoutStore.invoicesPerPage
  return Math.ceil(invoices.value.length / perPage)
})

// 渲染预览
async function renderPreview() {
  if (!canvasRef.value) return
  await renderPage(
    canvasRef.value,
    invoices.value,
    layoutStore.currentPage - 1,
    layoutStore.config,
    imageCache,
  )
}

// 删除发票
function removeInvoice(id: string) {
  invoiceStore.removeInvoice(id)
}

// 格式化金额
function formatMoney(amount: number): string {
  return `¥ ${amount.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
}

// 生成PDF
async function generatePdf() {
  isGenerating.value = true
  try {
    const invoiceIds = invoices.value.map((inv) => inv.id)
    const result = await createMergeTask(invoiceIds, outputType.value)
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

// 监听配置变化重新渲染
watch(
  () => [layoutStore.config, layoutStore.currentPage],
  () => {
    renderPreview()
  },
  { deep: true },
)

// 监听发票列表变化
watch(
  () => invoices.value,
  () => {
    layoutStore.setTotalPages(totalPages.value)
    renderPreview()
  },
  { immediate: true, deep: true },
)

onMounted(() => {
  layoutStore.setTotalPages(totalPages.value)
  renderPreview()
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
            A4 打印预览 ({{ layoutStore.config.layout }})
          </h3>
          <div class="flex items-center gap-4">
            <span class="text-slate-500 text-xs font-medium">
              当前共 {{ totalPages }} 页
            </span>
            <div
              class="flex items-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-1"
            >
              <button
                @click="layoutStore.zoomIn"
                class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded transition-colors"
              >
                <span class="material-symbols-outlined !text-xl">zoom_in</span>
              </button>
              <button
                @click="layoutStore.zoomOut"
                class="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded transition-colors"
              >
                <span class="material-symbols-outlined !text-xl">zoom_out</span>
              </button>
            </div>
          </div>
        </div>

        <div
          class="relative bg-slate-200 dark:bg-slate-950 rounded-xl border border-slate-300 dark:border-slate-800 overflow-hidden shadow-inner"
        >
          <div class="h-[750px] overflow-y-auto p-8 flex flex-col items-center gap-12">
            <div class="flex flex-col gap-4 w-full max-w-[530px]">
              <canvas
                ref="canvasRef"
                class="w-full shadow-lg"
                :style="{ transform: `scale(${layoutStore.previewZoom})`, transformOrigin: 'top center' }"
              ></canvas>
              <div class="flex justify-between items-center px-1">
                <span class="text-slate-500 text-xs font-medium">
                  第 {{ layoutStore.currentPage }} 页 / 共 {{ totalPages }} 页
                </span>
                <div class="flex gap-2">
                  <button
                    @click="layoutStore.prevPage"
                    :disabled="layoutStore.currentPage <= 1"
                    class="p-1 hover:bg-slate-100 rounded disabled:opacity-50"
                  >
                    <span class="material-symbols-outlined !text-lg">chevron_left</span>
                  </button>
                  <button
                    @click="layoutStore.nextPage"
                    :disabled="layoutStore.currentPage >= totalPages"
                    class="p-1 hover:bg-slate-100 rounded disabled:opacity-50"
                  >
                    <span class="material-symbols-outlined !text-lg">chevron_right</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Panel -->
      <div class="col-span-5 flex flex-col gap-6">
        <!-- Add More -->
        <router-link
          to="/upload"
          class="p-6 rounded-xl bg-white dark:bg-slate-900 border-2 border-dashed border-slate-200 dark:border-slate-800 flex flex-col items-center justify-center gap-3 hover:border-primary transition-colors cursor-pointer"
        >
          <div class="size-12 rounded-full bg-primary/10 text-primary flex items-center justify-center">
            <span class="material-symbols-outlined">add_circle</span>
          </div>
          <div class="text-center">
            <p class="text-slate-900 dark:text-white text-sm font-bold">添加更多发票</p>
            <p class="text-slate-500 text-xs">拖拽文件或点击此处上传 (PDF, JPG, PNG)</p>
          </div>
        </router-link>

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
          <div class="overflow-x-auto">
            <table class="w-full text-left text-sm">
              <thead>
                <tr class="text-slate-500 bg-slate-50 dark:bg-slate-800/50">
                  <th class="px-4 py-3 font-medium">日期</th>
                  <th class="px-4 py-3 font-medium">供应商</th>
                  <th class="px-4 py-3 font-medium text-right">金额</th>
                  <th class="px-4 py-3 font-medium text-center">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                <tr
                  v-for="invoice in invoices"
                  :key="invoice.id"
                  class="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                >
                  <td class="px-4 py-4 dark:text-slate-300">{{ invoice.date }}</td>
                  <td class="px-4 py-4 dark:text-slate-300">{{ invoice.sellerName }}</td>
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
