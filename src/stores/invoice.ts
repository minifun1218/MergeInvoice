import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Invoice, UploadFileItem, MergeTask, DashboardStats } from '@/types/invoice'

/** 发票管理状态 */
export const useInvoiceStore = defineStore('invoice', () => {
  // 发票列表
  const invoices = ref<Invoice[]>([])
  // 待上传文件队列
  const uploadQueue = ref<UploadFileItem[]>([])
  // 选中的发票ID列表（用于合并）
  const selectedInvoiceIds = ref<string[]>([])
  // 当前合并任务
  const currentMergeTask = ref<MergeTask | null>(null)
  // 仪表板统计
  const dashboardStats = ref<DashboardStats | null>(null)
  // 加载状态
  const loading = ref(false)

  // 计算属性：选中的发票列表
  const selectedInvoices = computed(() => {
    return invoices.value.filter((inv) => selectedInvoiceIds.value.includes(inv.id))
  })

  // 计算属性：选中发票总金额
  const selectedTotalAmount = computed(() => {
    return selectedInvoices.value.reduce((sum, inv) => sum + inv.totalAmount, 0)
  })

  // 计算属性：上传进度
  const uploadProgress = computed(() => {
    if (uploadQueue.value.length === 0) return 0
    const total = uploadQueue.value.reduce((sum, item) => sum + item.progress, 0)
    return Math.round(total / uploadQueue.value.length)
  })

  // 添加文件到上传队列
  function addToUploadQueue(files: File[]) {
    const newItems: UploadFileItem[] = files.map((file) => ({
      id: `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type,
      progress: 0,
      status: 'ready',
      file,
    }))
    uploadQueue.value.push(...newItems)
  }

  // 从上传队列移除
  function removeFromUploadQueue(id: string) {
    const index = uploadQueue.value.findIndex((item) => item.id === id)
    if (index > -1) {
      uploadQueue.value.splice(index, 1)
    }
  }

  // 更新上传进度
  function updateUploadProgress(id: string, progress: number, status?: UploadFileItem['status']) {
    const item = uploadQueue.value.find((item) => item.id === id)
    if (item) {
      item.progress = progress
      if (status) item.status = status
    }
  }

  // 清空上传队列
  function clearUploadQueue() {
    uploadQueue.value = []
  }

  // 添加发票
  function addInvoice(invoice: Invoice) {
    invoices.value.unshift(invoice)
  }

  // 批量添加发票
  function addInvoices(newInvoices: Invoice[]) {
    invoices.value.unshift(...newInvoices)
  }

  // 删除发票
  function removeInvoice(id: string) {
    const index = invoices.value.findIndex((inv) => inv.id === id)
    if (index > -1) {
      invoices.value.splice(index, 1)
    }
    // 同时从选中列表移除
    const selectedIndex = selectedInvoiceIds.value.indexOf(id)
    if (selectedIndex > -1) {
      selectedInvoiceIds.value.splice(selectedIndex, 1)
    }
  }

  // 切换选中状态
  function toggleSelect(id: string) {
    const index = selectedInvoiceIds.value.indexOf(id)
    if (index > -1) {
      selectedInvoiceIds.value.splice(index, 1)
    } else {
      selectedInvoiceIds.value.push(id)
    }
  }

  // 全选/取消全选
  function selectAll(select: boolean) {
    if (select) {
      selectedInvoiceIds.value = invoices.value.map((inv) => inv.id)
    } else {
      selectedInvoiceIds.value = []
    }
  }

  // 设置统计数据
  function setDashboardStats(stats: DashboardStats) {
    dashboardStats.value = stats
  }

  // 设置当前合并任务
  function setCurrentMergeTask(task: MergeTask | null) {
    currentMergeTask.value = task
  }

  return {
    invoices,
    uploadQueue,
    selectedInvoiceIds,
    currentMergeTask,
    dashboardStats,
    loading,
    selectedInvoices,
    selectedTotalAmount,
    uploadProgress,
    addToUploadQueue,
    removeFromUploadQueue,
    updateUploadProgress,
    clearUploadQueue,
    addInvoice,
    addInvoices,
    removeInvoice,
    toggleSelect,
    selectAll,
    setDashboardStats,
    setCurrentMergeTask,
  }
})
