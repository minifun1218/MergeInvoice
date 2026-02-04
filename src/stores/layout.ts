import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/** 页面布局类型 */
export type PageLayout = '1x1' | '2x1' | '2x2'

/** 纸张方向 */
export type PageOrientation = 'portrait' | 'landscape'

/** 布局配置 */
export interface LayoutConfig {
  /** 每页发票数量布局 */
  layout: PageLayout
  /** 纸张方向 */
  orientation: PageOrientation
  /** 边距(mm) */
  margin: number
  /** 发票间距(mm) */
  gap: number
  /** 是否显示页码 */
  showPageNumber: boolean
  /** 是否显示发票分类标签 */
  showCategoryLabel: boolean
  /** 缩放比例 */
  scale: number
}

/** 布局配置状态管理 */
export const useLayoutStore = defineStore('layout', () => {
  // 默认布局配置
  const config = ref<LayoutConfig>({
    layout: '2x1',
    orientation: 'portrait',
    margin: 10,
    gap: 5,
    showPageNumber: true,
    showCategoryLabel: true,
    scale: 1,
  })

  // 预览缩放
  const previewZoom = ref(1)

  // 当前预览页码
  const currentPage = ref(1)

  // 总页数
  const totalPages = ref(0)

  // 计算每页显示发票数量
  const invoicesPerPage = computed(() => {
    switch (config.value.layout) {
      case '1x1':
        return 1
      case '2x1':
        return 2
      case '2x2':
        return 4
      default:
        return 2
    }
  })

  // A4尺寸(像素, 96dpi)
  const a4Size = computed(() => {
    const width = config.value.orientation === 'portrait' ? 794 : 1123
    const height = config.value.orientation === 'portrait' ? 1123 : 794
    return { width, height }
  })

  // 更新布局配置
  function updateConfig(partial: Partial<LayoutConfig>) {
    config.value = { ...config.value, ...partial }
  }

  // 设置布局
  function setLayout(layout: PageLayout) {
    config.value.layout = layout
  }

  // 设置方向
  function setOrientation(orientation: PageOrientation) {
    config.value.orientation = orientation
  }

  // 缩放预览
  function zoomIn() {
    previewZoom.value = Math.min(previewZoom.value + 0.1, 2)
  }

  function zoomOut() {
    previewZoom.value = Math.max(previewZoom.value - 0.1, 0.5)
  }

  function resetZoom() {
    previewZoom.value = 1
  }

  // 翻页
  function nextPage() {
    if (currentPage.value < totalPages.value) {
      currentPage.value++
    }
  }

  function prevPage() {
    if (currentPage.value > 1) {
      currentPage.value--
    }
  }

  function goToPage(page: number) {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  // 设置总页数
  function setTotalPages(pages: number) {
    totalPages.value = pages
    if (currentPage.value > pages) {
      currentPage.value = Math.max(1, pages)
    }
  }

  // 重置配置
  function resetConfig() {
    config.value = {
      layout: '2x1',
      orientation: 'portrait',
      margin: 10,
      gap: 5,
      showPageNumber: true,
      showCategoryLabel: true,
      scale: 1,
    }
    previewZoom.value = 1
    currentPage.value = 1
  }

  return {
    config,
    previewZoom,
    currentPage,
    totalPages,
    invoicesPerPage,
    a4Size,
    updateConfig,
    setLayout,
    setOrientation,
    zoomIn,
    zoomOut,
    resetZoom,
    nextPage,
    prevPage,
    goToPage,
    setTotalPages,
    resetConfig,
  }
})
