// 发票相关类型定义

/** 发票状态 */
export type InvoiceStatus = 'pending' | 'verified' | 'reviewing' | 'failed'

/** 发票类型 */
export type InvoiceType = 'vat_special' | 'vat_normal' | 'flight' | 'taxi' | 'hotel' | 'other'

/** 发票信息 */
export interface Invoice {
  id: string
  /** 发票代码 */
  code: string
  /** 发票号码 */
  number: string
  /** 发票类型 */
  type: InvoiceType
  /** 销方名称 */
  sellerName: string
  /** 购方名称 */
  buyerName: string
  /** 开票日期 */
  date: string
  /** 金额(不含税) */
  amount: number
  /** 税额 */
  taxAmount: number
  /** 价税合计 */
  totalAmount: number
  /** 状态 */
  status: InvoiceStatus
  /** 原始文件URL */
  fileUrl: string
  /** 文件类型 */
  fileType: 'pdf' | 'jpg' | 'png' | 'ofd'
  /** 创建时间 */
  createdAt: string
  /** 更新时间 */
  updatedAt: string
}

/** 上传文件项 */
export interface UploadFileItem {
  id: string
  fileName: string
  fileSize: number
  fileType: string
  progress: number
  status: 'ready' | 'uploading' | 'success' | 'error'
  file: File
}

/** 合并任务 */
export interface MergeTask {
  id: string
  invoiceIds: string[]
  status: 'pending' | 'processing' | 'completed' | 'failed'
  outputType: 'pdf' | 'zip'
  totalPages: number
  totalAmount: number
  createdAt: string
  downloadUrl?: string
}

/** 统计数据 */
export interface DashboardStats {
  /** 本月已处理数量 */
  processedCount: number
  /** 处理数量变化百分比 */
  processedChange: number
  /** 待审核任务数 */
  pendingCount: number
  /** 待审核变化百分比 */
  pendingChange: number
  /** 本月节省税额 */
  savedTax: number
  /** 节省变化百分比 */
  savedChange: number
}

/** 分页请求 */
export interface PageRequest {
  page: number
  pageSize: number
}

/** 分页响应 */
export interface PageResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
}

/** API响应 */
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}
