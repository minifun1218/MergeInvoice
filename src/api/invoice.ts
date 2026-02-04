// 发票API服务
import type {
  Invoice,
  MergeTask,
  DashboardStats,
  PageRequest,
  PageResponse,
  ApiResponse,
} from '@/types/invoice'

const API_BASE = '/api/v1'

/** 获取仪表板统计数据 */
export async function getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
  const response = await fetch(`${API_BASE}/dashboard/stats`)
  return response.json()
}

/** 获取发票列表 */
export async function getInvoiceList(
  params: PageRequest & { status?: string; keyword?: string },
): Promise<ApiResponse<PageResponse<Invoice>>> {
  const query = new URLSearchParams(params as unknown as Record<string, string>).toString()
  const response = await fetch(`${API_BASE}/invoices?${query}`)
  return response.json()
}

/** 获取发票详情 */
export async function getInvoiceDetail(id: string): Promise<ApiResponse<Invoice>> {
  const response = await fetch(`${API_BASE}/invoices/${id}`)
  return response.json()
}

/** 上传发票文件 */
export async function uploadInvoice(
  file: File,
  onProgress?: (progress: number) => void,
): Promise<ApiResponse<Invoice>> {
  const formData = new FormData()
  formData.append('file', file)

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE}/invoices/upload`)

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText))
      } else {
        reject(new Error(xhr.statusText))
      }
    }

    xhr.onerror = () => reject(new Error('上传失败'))
    xhr.send(formData)
  })
}

/** 批量上传发票 */
export async function batchUploadInvoices(files: File[]): Promise<ApiResponse<Invoice[]>> {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))

  const response = await fetch(`${API_BASE}/invoices/batch-upload`, {
    method: 'POST',
    body: formData,
  })
  return response.json()
}

/** 删除发票 */
export async function deleteInvoice(id: string): Promise<ApiResponse<null>> {
  const response = await fetch(`${API_BASE}/invoices/${id}`, {
    method: 'DELETE',
  })
  return response.json()
}

/** 创建合并任务 */
export async function createMergeTask(
  invoiceIds: string[],
  outputType: 'pdf' | 'zip',
): Promise<ApiResponse<MergeTask>> {
  const response = await fetch(`${API_BASE}/merge-tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ invoiceIds, outputType }),
  })
  return response.json()
}

/** 获取合并任务详情 */
export async function getMergeTaskDetail(id: string): Promise<ApiResponse<MergeTask>> {
  const response = await fetch(`${API_BASE}/merge-tasks/${id}`)
  return response.json()
}

/** 获取合并任务列表 */
export async function getMergeTaskList(
  params: PageRequest,
): Promise<ApiResponse<PageResponse<MergeTask>>> {
  const query = new URLSearchParams(params as unknown as Record<string, string>).toString()
  const response = await fetch(`${API_BASE}/merge-tasks?${query}`)
  return response.json()
}

/** 下载合并文件 */
export function downloadMergedFile(taskId: string): void {
  window.open(`${API_BASE}/merge-tasks/${taskId}/download`, '_blank')
}

/** 保存草稿 */
export async function saveDraft(invoiceIds: string[]): Promise<ApiResponse<{ draftId: string }>> {
  const response = await fetch(`${API_BASE}/drafts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ invoiceIds }),
  })
  return response.json()
}
