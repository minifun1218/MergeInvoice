/**
 * Canvas 渲染工具 - 发票预览与合并
 */

import type { Invoice } from '@/types/invoice'
import type { LayoutConfig } from '@/stores/layout'

/** A4尺寸常量(像素, 96dpi) */
const A4_WIDTH_PORTRAIT = 794
const A4_HEIGHT_PORTRAIT = 1123

/** PDF点数转像素 */
const PT_TO_PX = 96 / 72

/** 发票渲染项 */
interface RenderItem {
  invoice: Invoice
  image: HTMLImageElement | null
  x: number
  y: number
  width: number
  height: number
}

/**
 * 加载图片
 */
export function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => resolve(img)
    img.onerror = reject
    img.src = src
  })
}

/**
 * 从PDF第一页生成预览图(需要pdf.js)
 */
export async function pdfToImage(pdfUrl: string): Promise<HTMLImageElement> {
  // 动态导入pdf.js
  const pdfjsLib = await import('pdfjs-dist')
  pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js'

  const pdf = await pdfjsLib.getDocument(pdfUrl).promise
  const page = await pdf.getPage(1)
  const viewport = page.getViewport({ scale: 1.5 })

  const canvas = document.createElement('canvas')
  canvas.width = viewport.width
  canvas.height = viewport.height

  const ctx = canvas.getContext('2d')!
  await page.render({ canvasContext: ctx, viewport }).promise

  return loadImage(canvas.toDataURL('image/png'))
}

/**
 * 计算布局位置
 */
export function calculateLayout(
  invoiceCount: number,
  config: LayoutConfig,
): { positions: { x: number; y: number; width: number; height: number }[]; totalPages: number } {
  const isPortrait = config.orientation === 'portrait'
  const pageWidth = isPortrait ? A4_WIDTH_PORTRAIT : A4_HEIGHT_PORTRAIT
  const pageHeight = isPortrait ? A4_HEIGHT_PORTRAIT : A4_WIDTH_PORTRAIT

  const marginPx = config.margin * PT_TO_PX
  const gapPx = config.gap * PT_TO_PX

  const contentWidth = pageWidth - marginPx * 2
  const contentHeight = pageHeight - marginPx * 2

  let cols = 1
  let rows = 1

  switch (config.layout) {
    case '1x1':
      cols = 1
      rows = 1
      break
    case '2x1':
      cols = 1
      rows = 2
      break
    case '2x2':
      cols = 2
      rows = 2
      break
  }

  const cellWidth = (contentWidth - gapPx * (cols - 1)) / cols
  const cellHeight = (contentHeight - gapPx * (rows - 1)) / rows
  const perPage = cols * rows

  const positions: { x: number; y: number; width: number; height: number }[] = []
  const totalPages = Math.ceil(invoiceCount / perPage)

  for (let i = 0; i < invoiceCount; i++) {
    const pageIndex = Math.floor(i / perPage)
    const indexInPage = i % perPage
    const row = Math.floor(indexInPage / cols)
    const col = indexInPage % cols

    positions.push({
      x: marginPx + col * (cellWidth + gapPx),
      y: marginPx + row * (cellHeight + gapPx) + pageIndex * pageHeight,
      width: cellWidth,
      height: cellHeight,
    })
  }

  return { positions, totalPages }
}

/**
 * 渲染单页预览
 */
export async function renderPage(
  canvas: HTMLCanvasElement,
  invoices: Invoice[],
  pageIndex: number,
  config: LayoutConfig,
  imageCache: Map<string, HTMLImageElement>,
): Promise<void> {
  const ctx = canvas.getContext('2d')!
  const isPortrait = config.orientation === 'portrait'
  const pageWidth = isPortrait ? A4_WIDTH_PORTRAIT : A4_HEIGHT_PORTRAIT
  const pageHeight = isPortrait ? A4_HEIGHT_PORTRAIT : A4_WIDTH_PORTRAIT

  // 应用缩放
  canvas.width = pageWidth * config.scale
  canvas.height = pageHeight * config.scale
  ctx.scale(config.scale, config.scale)

  // 白色背景
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, pageWidth, pageHeight)

  // 计算布局
  const { positions } = calculateLayout(invoices.length, config)
  const perPage =
    config.layout === '1x1' ? 1 : config.layout === '2x1' ? 2 : 4
  const startIndex = pageIndex * perPage
  const endIndex = Math.min(startIndex + perPage, invoices.length)

  // 渲染发票
  for (let i = startIndex; i < endIndex; i++) {
    const invoice = invoices[i]
    const pos = positions[i - startIndex]

    // 绘制边框
    ctx.strokeStyle = '#e5e7eb'
    ctx.lineWidth = 1
    ctx.strokeRect(pos.x, pos.y, pos.width, pos.height)

    // 尝试获取缓存图片
    let img = imageCache.get(invoice.id)
    if (!img && invoice.fileUrl) {
      try {
        if (invoice.fileType === 'pdf') {
          img = await pdfToImage(invoice.fileUrl)
        } else {
          img = await loadImage(invoice.fileUrl)
        }
        imageCache.set(invoice.id, img)
      } catch {
        // 图片加载失败，绘制占位符
      }
    }

    if (img) {
      // 保持比例缩放
      const scale = Math.min(pos.width / img.width, pos.height / img.height)
      const drawWidth = img.width * scale
      const drawHeight = img.height * scale
      const drawX = pos.x + (pos.width - drawWidth) / 2
      const drawY = pos.y + (pos.height - drawHeight) / 2
      ctx.drawImage(img, drawX, drawY, drawWidth, drawHeight)
    } else {
      // 绘制占位符
      ctx.fillStyle = '#f3f4f6'
      ctx.fillRect(pos.x + 2, pos.y + 2, pos.width - 4, pos.height - 4)
      ctx.fillStyle = '#9ca3af'
      ctx.font = '14px Inter, sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('发票预览', pos.x + pos.width / 2, pos.y + pos.height / 2)
    }

    // 显示分类标签
    if (config.showCategoryLabel) {
      ctx.fillStyle = 'rgba(19, 127, 236, 0.9)'
      ctx.fillRect(pos.x, pos.y, 80, 24)
      ctx.fillStyle = '#ffffff'
      ctx.font = '12px Inter, sans-serif'
      ctx.textAlign = 'left'
      ctx.fillText(getInvoiceTypeName(invoice.type), pos.x + 8, pos.y + 16)
    }
  }

  // 显示页码
  if (config.showPageNumber) {
    const totalPages = Math.ceil(invoices.length / perPage)
    ctx.fillStyle = '#6b7280'
    ctx.font = '12px Inter, sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(
      `第 ${pageIndex + 1} 页 / 共 ${totalPages} 页`,
      pageWidth / 2,
      pageHeight - 20,
    )
  }
}

/**
 * 获取发票类型名称
 */
function getInvoiceTypeName(type: string): string {
  const typeMap: Record<string, string> = {
    vat_special: '增值税专用',
    vat_normal: '增值税普通',
    flight: '航空客票',
    taxi: '出租车票',
    hotel: '酒店住宿',
    other: '其他',
  }
  return typeMap[type] || '未知类型'
}

/**
 * 导出为图片
 */
export function canvasToBlob(canvas: HTMLCanvasElement, type = 'image/png'): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (blob) {
        resolve(blob)
      } else {
        reject(new Error('导出失败'))
      }
    }, type)
  })
}

/**
 * 渲染所有页面并生成PDF数据
 */
export async function renderAllPages(
  invoices: Invoice[],
  config: LayoutConfig,
): Promise<Blob[]> {
  const perPage =
    config.layout === '1x1' ? 1 : config.layout === '2x1' ? 2 : 4
  const totalPages = Math.ceil(invoices.length / perPage)
  const imageCache = new Map<string, HTMLImageElement>()
  const blobs: Blob[] = []

  const canvas = document.createElement('canvas')

  for (let i = 0; i < totalPages; i++) {
    await renderPage(canvas, invoices, i, config, imageCache)
    const blob = await canvasToBlob(canvas)
    blobs.push(blob)
  }

  return blobs
}
