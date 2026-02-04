/**
 * 文件上传工具 - 支持切片上传和并发控制
 */

const API_BASE = '/api/v1'

/** 切片大小: 2MB */
const CHUNK_SIZE = 2 * 1024 * 1024

/** 最大并发数 */
const MAX_CONCURRENT = 3

/** 切片信息 */
interface ChunkInfo {
  index: number
  start: number
  end: number
  blob: Blob
  hash: string
}

/** 上传进度回调 */
type ProgressCallback = (progress: number) => void

/** 上传结果 */
interface UploadResult {
  success: boolean
  fileId?: string
  error?: string
}

/**
 * 计算文件hash(简化版，使用文件信息)
 */
function calculateFileHash(file: File): string {
  return `${file.name}_${file.size}_${file.lastModified}`
}

/**
 * 将文件切片
 */
function createChunks(file: File): ChunkInfo[] {
  const chunks: ChunkInfo[] = []
  const fileHash = calculateFileHash(file)
  let index = 0
  let start = 0

  while (start < file.size) {
    const end = Math.min(start + CHUNK_SIZE, file.size)
    chunks.push({
      index,
      start,
      end,
      blob: file.slice(start, end),
      hash: `${fileHash}_${index}`,
    })
    start = end
    index++
  }

  return chunks
}

/**
 * 上传单个切片
 */
async function uploadChunk(
  fileHash: string,
  chunk: ChunkInfo,
  fileName: string,
  totalChunks: number,
): Promise<boolean> {
  const formData = new FormData()
  formData.append('chunk', chunk.blob)
  formData.append('chunkIndex', chunk.index.toString())
  formData.append('chunkHash', chunk.hash)
  formData.append('fileHash', fileHash)
  formData.append('fileName', fileName)
  formData.append('totalChunks', totalChunks.toString())

  const response = await fetch(`${API_BASE}/invoices/upload-chunk`, {
    method: 'POST',
    body: formData,
  })

  return response.ok
}

/**
 * 合并切片请求
 */
async function mergeChunks(fileHash: string, fileName: string, totalChunks: number): Promise<UploadResult> {
  const response = await fetch(`${API_BASE}/invoices/merge-chunks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fileHash, fileName, totalChunks }),
  })

  const result = await response.json()
  return {
    success: response.ok,
    fileId: result.data?.id,
    error: result.message,
  }
}

/**
 * 并发控制器
 */
class ConcurrencyController {
  private running = 0
  private queue: (() => Promise<void>)[] = []

  constructor(private maxConcurrent: number) {}

  async add<T>(task: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      const run = async () => {
        this.running++
        try {
          const result = await task()
          resolve(result)
        } catch (error) {
          reject(error)
        } finally {
          this.running--
          this.next()
        }
      }

      if (this.running < this.maxConcurrent) {
        run()
      } else {
        this.queue.push(run)
      }
    })
  }

  private next() {
    if (this.queue.length > 0 && this.running < this.maxConcurrent) {
      const task = this.queue.shift()
      task?.()
    }
  }
}

/**
 * 切片上传(大文件)
 */
export async function uploadWithChunks(
  file: File,
  onProgress?: ProgressCallback,
): Promise<UploadResult> {
  const fileHash = calculateFileHash(file)
  const chunks = createChunks(file)
  const totalChunks = chunks.length

  const controller = new ConcurrencyController(MAX_CONCURRENT)
  let uploadedCount = 0

  try {
    // 并发上传所有切片
    await Promise.all(
      chunks.map((chunk) =>
        controller.add(async () => {
          const success = await uploadChunk(fileHash, chunk, file.name, totalChunks)
          if (!success) {
            throw new Error(`切片 ${chunk.index} 上传失败`)
          }
          uploadedCount++
          onProgress?.(Math.round((uploadedCount / totalChunks) * 90)) // 90%用于上传
        }),
      ),
    )

    // 请求合并
    onProgress?.(95)
    const result = await mergeChunks(fileHash, file.name, totalChunks)
    onProgress?.(100)

    return result
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : '上传失败',
    }
  }
}

/**
 * 普通上传(小文件)
 */
export async function uploadFile(
  file: File,
  onProgress?: ProgressCallback,
): Promise<UploadResult> {
  const formData = new FormData()
  formData.append('file', file)

  return new Promise((resolve) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `${API_BASE}/invoices/upload`)

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        onProgress?.(Math.round((e.loaded / e.total) * 100))
      }
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        const result = JSON.parse(xhr.responseText)
        resolve({ success: true, fileId: result.data?.id })
      } else {
        resolve({ success: false, error: xhr.statusText })
      }
    }

    xhr.onerror = () => resolve({ success: false, error: '网络错误' })
    xhr.send(formData)
  })
}

/**
 * 智能上传 - 根据文件大小选择上传方式
 */
export async function smartUpload(
  file: File,
  onProgress?: ProgressCallback,
): Promise<UploadResult> {
  // 大于5MB使用切片上传
  if (file.size > 5 * 1024 * 1024) {
    return uploadWithChunks(file, onProgress)
  }
  return uploadFile(file, onProgress)
}

/**
 * 批量并发上传
 */
export async function batchUpload(
  files: File[],
  onFileProgress?: (fileIndex: number, progress: number) => void,
  onComplete?: (results: UploadResult[]) => void,
): Promise<UploadResult[]> {
  const controller = new ConcurrencyController(MAX_CONCURRENT)
  const results: UploadResult[] = []

  await Promise.all(
    files.map((file, index) =>
      controller.add(async () => {
        const result = await smartUpload(file, (progress) => {
          onFileProgress?.(index, progress)
        })
        results[index] = result
      }),
    ),
  )

  onComplete?.(results)
  return results
}
