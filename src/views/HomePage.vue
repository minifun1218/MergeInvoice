<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInvoiceStore } from '@/stores/invoice'
import { getDashboardStats, getInvoiceList } from '@/api/invoice'
import type { Invoice } from '@/types/invoice'

const router = useRouter()
const invoiceStore = useInvoiceStore()

const recentInvoices = ref<Invoice[]>([])
const loading = ref(true)

const stats = ref({
  processedCount: 0,
  processedChange: 0,
  pendingCount: 0,
  pendingChange: 0,
  savedTax: 0,
  savedChange: 0,
})

// 模拟数据
onMounted(async () => {
  loading.value = true
  try {
    // 获取统计数据
    const statsRes = await getDashboardStats()
    if (statsRes.code === 0) {
      stats.value = statsRes.data
      invoiceStore.setDashboardStats(statsRes.data)
    }

    // 获取最近发票
    const listRes = await getInvoiceList({ page: 1, pageSize: 5 })
    if (listRes.code === 0) {
      recentInvoices.value = listRes.data.data
    }
  } catch {
    // 使用模拟数据
    stats.value = {
      processedCount: 1284,
      processedChange: 12.5,
      pendingCount: 12,
      pendingChange: -2.4,
      savedTax: 4590.2,
      savedChange: 5.8,
    }
    recentInvoices.value = [
      {
        id: '1',
        code: '044001900111',
        number: '12345678',
        type: 'vat_special',
        sellerName: '上海某某科技有限公司',
        buyerName: '北京某某公司',
        date: '2023-11-20',
        amount: 1106.19,
        taxAmount: 143.81,
        totalAmount: 1250.0,
        status: 'verified',
        fileUrl: '',
        fileType: 'pdf',
        createdAt: '2023-11-20T10:00:00Z',
        updatedAt: '2023-11-20T10:00:00Z',
      },
      {
        id: '2',
        code: '044001900112',
        number: '87654321',
        type: 'flight',
        sellerName: '中国东方航空股份有限公司',
        buyerName: '北京某某公司',
        date: '2023-11-18',
        amount: 2840.0,
        taxAmount: 0,
        totalAmount: 2840.0,
        status: 'reviewing',
        fileUrl: '',
        fileType: 'pdf',
        createdAt: '2023-11-18T10:00:00Z',
        updatedAt: '2023-11-18T10:00:00Z',
      },
      {
        id: '3',
        code: '044001900113',
        number: '11223344',
        type: 'taxi',
        sellerName: '北京滴滴支付有限公司',
        buyerName: '北京某某公司',
        date: '2023-11-15',
        amount: 45.5,
        taxAmount: 0,
        totalAmount: 45.5,
        status: 'verified',
        fileUrl: '',
        fileType: 'pdf',
        createdAt: '2023-11-15T10:00:00Z',
        updatedAt: '2023-11-15T10:00:00Z',
      },
    ]
  } finally {
    loading.value = false
  }
})

function getStatusClass(status: string) {
  switch (status) {
    case 'verified':
      return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
    case 'reviewing':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
    case 'pending':
      return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
    case 'failed':
      return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
    default:
      return 'bg-slate-100 text-slate-700'
  }
}

function getStatusText(status: string) {
  const map: Record<string, string> = {
    verified: '已验真',
    reviewing: '审核中',
    pending: '待处理',
    failed: '验证失败',
  }
  return map[status] || status
}

function getTypeIcon(type: string): { icon: string; color: string } {
  const defaultIcon = { icon: 'description', color: 'text-slate-500 bg-slate-100' }
  const map: Record<string, { icon: string; color: string }> = {
    vat_special: { icon: 'receipt_long', color: 'text-primary bg-primary/10' },
    vat_normal: { icon: 'receipt', color: 'text-primary bg-primary/10' },
    flight: { icon: 'flight_takeoff', color: 'text-amber-500 bg-amber-100' },
    taxi: { icon: 'local_taxi', color: 'text-purple-500 bg-purple-100' },
    hotel: { icon: 'hotel', color: 'text-green-500 bg-green-100' },
    other: defaultIcon,
  }
  return map[type] ?? defaultIcon
}

function getTypeName(type: string) {
  const map: Record<string, string> = {
    vat_special: '增值税专用发票',
    vat_normal: '增值税普通发票',
    flight: '航空运输电子客票',
    taxi: '打车费发票',
    hotel: '酒店住宿发票',
    other: '其他发票',
  }
  return map[type] || '其他发票'
}

function formatMoney(amount: number) {
  return `¥${amount.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
}

function goToUpload() {
  router.push('/upload')
}
</script>

<template>
  <main class="px-40 flex flex-1 justify-center py-8">
    <div class="layout-content-container flex flex-col max-w-[1024px] flex-1">
      <!-- Page Heading -->
      <div class="flex flex-wrap justify-between gap-3 p-4 mb-4">
        <div class="flex min-w-72 flex-col gap-3">
          <p
            class="text-slate-900 dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]"
          >
            欢迎回来, 管理员
          </p>
          <p class="text-slate-500 dark:text-slate-400 text-base font-normal leading-normal">
            这里是您的发票管理看板，高效处理您的税务发票与合并需求。
          </p>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="goToUpload"
            class="bg-primary text-white px-6 py-2.5 rounded-lg font-bold text-sm shadow-lg shadow-primary/20 hover:bg-primary/90 transition-all flex items-center gap-2"
          >
            <span class="material-symbols-outlined text-[20px]">add_circle</span>
            开始新报销
          </button>
        </div>
      </div>

      <!-- Stats Dashboard -->
      <div class="flex flex-wrap gap-4 p-4">
        <div
          class="flex min-w-[200px] flex-1 flex-col gap-2 rounded-xl p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm"
        >
          <div class="flex justify-between items-start">
            <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">本月已处理</p>
            <span class="material-symbols-outlined text-primary">description</span>
          </div>
          <p class="text-slate-900 dark:text-white tracking-light text-3xl font-bold leading-tight">
            {{ stats.processedCount.toLocaleString() }}
            <span class="text-sm font-normal text-slate-400">张</span>
          </p>
          <div class="flex items-center gap-1 mt-1">
            <span
              :class="[
                'material-symbols-outlined text-sm',
                stats.processedChange >= 0 ? 'text-green-600' : 'text-red-600',
              ]"
            >
              {{ stats.processedChange >= 0 ? 'trending_up' : 'trending_down' }}
            </span>
            <p
              :class="[
                'text-sm font-medium leading-normal',
                stats.processedChange >= 0 ? 'text-green-600' : 'text-red-600',
              ]"
            >
              {{ stats.processedChange >= 0 ? '+' : '' }}{{ stats.processedChange }}% 较上月
            </p>
          </div>
        </div>

        <div
          class="flex min-w-[200px] flex-1 flex-col gap-2 rounded-xl p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm"
        >
          <div class="flex justify-between items-start">
            <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">待审核/核验</p>
            <span class="material-symbols-outlined text-amber-500">pending_actions</span>
          </div>
          <p class="text-slate-900 dark:text-white tracking-light text-3xl font-bold leading-tight">
            {{ stats.pendingCount }}
            <span class="text-sm font-normal text-slate-400">个任务</span>
          </p>
          <div class="flex items-center gap-1 mt-1">
            <span
              :class="[
                'material-symbols-outlined text-sm',
                stats.pendingChange <= 0 ? 'text-green-600' : 'text-red-600',
              ]"
            >
              {{ stats.pendingChange <= 0 ? 'trending_down' : 'trending_up' }}
            </span>
            <p
              :class="[
                'text-sm font-medium leading-normal',
                stats.pendingChange <= 0 ? 'text-green-600' : 'text-red-600',
              ]"
            >
              {{ stats.pendingChange }}% 待办下降
            </p>
          </div>
        </div>

        <div
          class="flex min-w-[200px] flex-1 flex-col gap-2 rounded-xl p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm"
        >
          <div class="flex justify-between items-start">
            <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">本月节省税额</p>
            <span class="material-symbols-outlined text-green-600">savings</span>
          </div>
          <p class="text-slate-900 dark:text-white tracking-light text-3xl font-bold leading-tight">
            {{ formatMoney(stats.savedTax) }}
          </p>
          <div class="flex items-center gap-1 mt-1">
            <span class="material-symbols-outlined text-green-600 text-sm">trending_up</span>
            <p class="text-green-600 text-sm font-medium leading-normal">
              +{{ stats.savedChange }}% 效率提升
            </p>
          </div>
        </div>
      </div>

      <!-- Quick Start Section -->
      <div class="mt-4">
        <h2
          class="text-slate-900 dark:text-white text-[22px] font-bold leading-tight tracking-[-0.015em] px-4 pb-3 pt-5 flex items-center gap-2"
        >
          <span class="material-symbols-outlined">rocket_launch</span>
          快速开始
        </h2>
        <div class="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-5 p-4">
          <router-link
            to="/upload"
            class="flex flex-col gap-4 p-5 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-all cursor-pointer group shadow-sm"
          >
            <div
              class="w-full h-32 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center overflow-hidden"
            >
              <span
                class="material-symbols-outlined text-primary text-5xl group-hover:scale-110 transition-transform"
                >upload_file</span
              >
            </div>
            <div>
              <p class="text-slate-900 dark:text-white text-lg font-bold leading-normal">
                单张/快速上传
              </p>
              <p class="text-slate-500 dark:text-slate-400 text-sm font-normal mt-1">
                支持PDF、OFD、JPG及电子发票原件
              </p>
            </div>
          </router-link>

          <router-link
            to="/upload?batch=true"
            class="flex flex-col gap-4 p-5 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-all cursor-pointer group shadow-sm"
          >
            <div
              class="w-full h-32 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center overflow-hidden"
            >
              <span
                class="material-symbols-outlined text-primary text-5xl group-hover:scale-110 transition-transform"
                >folder_zip</span
              >
            </div>
            <div>
              <p class="text-slate-900 dark:text-white text-lg font-bold leading-normal">
                批量导入压缩包
              </p>
              <p class="text-slate-500 dark:text-slate-400 text-sm font-normal mt-1">
                支持ZIP格式，一次处理多达100张发票
              </p>
            </div>
          </router-link>

          <div
            class="flex flex-col gap-4 p-5 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-primary/50 transition-all cursor-pointer group shadow-sm"
          >
            <div
              class="w-full h-32 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center overflow-hidden"
            >
              <span
                class="material-symbols-outlined text-primary text-5xl group-hover:scale-110 transition-transform"
                >document_scanner</span
              >
            </div>
            <div>
              <p class="text-slate-900 dark:text-white text-lg font-bold leading-normal">
                OCR智能扫描
              </p>
              <p class="text-slate-500 dark:text-slate-400 text-sm font-normal mt-1">
                连接手机或扫描仪，实时识别纸质发票
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity Section -->
      <div class="mt-8 px-4">
        <div class="flex items-center justify-between mb-4">
          <h2
            class="text-slate-900 dark:text-white text-[22px] font-bold leading-tight tracking-[-0.015em] flex items-center gap-2"
          >
            <span class="material-symbols-outlined">history</span>
            最近活动
          </h2>
          <router-link to="/history" class="text-primary text-sm font-medium hover:underline">
            查看全部
          </router-link>
        </div>
        <div
          class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm"
        >
          <table class="w-full text-left border-collapse">
            <thead class="bg-slate-50 dark:bg-slate-800/50">
              <tr>
                <th
                  class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider"
                >
                  发票类型
                </th>
                <th
                  class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider"
                >
                  销方名称
                </th>
                <th
                  class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider"
                >
                  日期
                </th>
                <th
                  class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider"
                >
                  金额
                </th>
                <th
                  class="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-right"
                >
                  状态
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              <tr
                v-for="invoice in recentInvoices"
                :key="invoice.id"
                class="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors cursor-pointer"
              >
                <td class="px-6 py-4">
                  <div class="flex items-center gap-3">
                    <span
                      :class="[
                        'material-symbols-outlined p-1.5 rounded-lg text-lg',
                        getTypeIcon(invoice.type).color,
                      ]"
                    >
                      {{ getTypeIcon(invoice.type).icon }}
                    </span>
                    <span class="text-slate-900 dark:text-white font-medium">
                      {{ getTypeName(invoice.type) }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 text-slate-600 dark:text-slate-400 text-sm">
                  {{ invoice.sellerName }}
                </td>
                <td class="px-6 py-4 text-slate-500 dark:text-slate-400 text-sm">
                  {{ invoice.date }}
                </td>
                <td class="px-6 py-4 text-slate-900 dark:text-white font-bold">
                  {{ formatMoney(invoice.totalAmount) }}
                </td>
                <td class="px-6 py-4 text-right">
                  <span
                    :class="[
                      'px-3 py-1 text-xs font-bold rounded-full',
                      getStatusClass(invoice.status),
                    ]"
                  >
                    {{ getStatusText(invoice.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
@import '@/assets/home.css';
</style>
