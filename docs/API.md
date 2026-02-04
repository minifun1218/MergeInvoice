# 发票管理系统 API 文档

## 概述

本文档定义了发票管理系统前后端交互的 RESTful API 接口规范。

**Base URL**: `/api/v1`

**通用响应格式**:
```json
{
  "code": 0,          // 0 表示成功，非 0 表示错误
  "message": "success",
  "data": {}          // 具体数据
}
```

---

## 1. 仪表板统计 API

### 1.1 获取统计数据

获取首页仪表板的统计信息。

**请求**
```
GET /dashboard/stats
```

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "processedCount": 1284,       // 本月已处理数量
    "processedChange": 12.5,      // 较上月变化百分比
    "pendingCount": 12,           // 待审核任务数
    "pendingChange": -2.4,        // 待办变化百分比
    "savedTax": 4590.20,          // 本月节省税额
    "savedChange": 5.8            // 节省变化百分比
  }
}
```

---

## 2. 发票管理 API

### 2.1 获取发票列表

分页获取发票列表，支持关键词搜索和状态筛选。

**请求**
```
GET /invoices?page=1&pageSize=20&status=verified&keyword=京东
```

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 否 | 页码，默认 1 |
| pageSize | number | 否 | 每页数量，默认 20，最大 100 |
| status | string | 否 | 状态筛选：pending/verified/reviewing/failed |
| keyword | string | 否 | 搜索关键词（销方名称/发票号码） |

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "data": [
      {
        "id": "inv_001",
        "code": "044001900111",
        "number": "12345678",
        "type": "vat_special",
        "sellerName": "上海某某科技有限公司",
        "buyerName": "北京某某公司",
        "date": "2023-11-20",
        "amount": 1106.19,
        "taxAmount": 143.81,
        "totalAmount": 1250.00,
        "status": "verified",
        "fileUrl": "https://storage.example.com/invoices/xxx.pdf",
        "fileType": "pdf",
        "createdAt": "2023-11-20T10:00:00Z",
        "updatedAt": "2023-11-20T10:30:00Z"
      }
    ],
    "total": 156,
    "page": 1,
    "pageSize": 20
  }
}
```

### 2.2 获取发票详情

**请求**
```
GET /invoices/{id}
```

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "inv_001",
    "code": "044001900111",
    "number": "12345678",
    "type": "vat_special",
    "sellerName": "上海某某科技有限公司",
    "buyerName": "北京某某公司",
    "date": "2023-11-20",
    "amount": 1106.19,
    "taxAmount": 143.81,
    "totalAmount": 1250.00,
    "status": "verified",
    "fileUrl": "https://storage.example.com/invoices/xxx.pdf",
    "fileType": "pdf",
    "createdAt": "2023-11-20T10:00:00Z",
    "updatedAt": "2023-11-20T10:30:00Z"
  }
}
```

### 2.3 上传发票（普通上传）

上传单个发票文件，后端自动进行 OCR 识别。

**请求**
```
POST /invoices/upload
Content-Type: multipart/form-data
```

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 发票文件（PDF/JPG/PNG，最大 10MB） |

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "inv_002",
    "code": "044001900112",
    "number": "87654321",
    "type": "vat_normal",
    "sellerName": "北京某某餐饮有限公司",
    "buyerName": "北京某某公司",
    "date": "2023-11-21",
    "amount": 398.23,
    "taxAmount": 51.77,
    "totalAmount": 450.00,
    "status": "pending",
    "fileUrl": "https://storage.example.com/invoices/yyy.pdf",
    "fileType": "pdf",
    "createdAt": "2023-11-21T09:00:00Z",
    "updatedAt": "2023-11-21T09:00:00Z"
  }
}
```

### 2.4 上传发票切片（分片上传）

用于大文件分片上传，前端将文件切片后逐个上传。

**请求**
```
POST /invoices/upload-chunk
Content-Type: multipart/form-data
```

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| chunk | Blob | 是 | 文件切片数据 |
| chunkIndex | number | 是 | 切片索引（从 0 开始） |
| chunkHash | string | 是 | 切片哈希值 |
| fileHash | string | 是 | 完整文件哈希值 |
| fileName | string | 是 | 原始文件名 |
| totalChunks | number | 是 | 总切片数 |

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "chunkIndex": 0,
    "received": true
  }
}
```

### 2.5 合并切片

所有切片上传完成后，请求合并切片。

**请求**
```
POST /invoices/merge-chunks
Content-Type: application/json
```

**请求体**
```json
{
  "fileHash": "file_name_12345_1700000000000",
  "fileName": "发票.pdf",
  "totalChunks": 5
}
```

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "inv_003",
    "code": "044001900113",
    "number": "11223344",
    "type": "vat_special",
    "sellerName": "广州某某贸易有限公司",
    "buyerName": "北京某某公司",
    "date": "2023-11-22",
    "amount": 8849.56,
    "taxAmount": 1150.44,
    "totalAmount": 10000.00,
    "status": "pending",
    "fileUrl": "https://storage.example.com/invoices/zzz.pdf",
    "fileType": "pdf",
    "createdAt": "2023-11-22T14:00:00Z",
    "updatedAt": "2023-11-22T14:00:00Z"
  }
}
```

### 2.6 批量上传发票

一次上传多个发票文件。

**请求**
```
POST /invoices/batch-upload
Content-Type: multipart/form-data
```

**参数**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| files | File[] | 是 | 发票文件数组（最多 20 个） |

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": "inv_004",
      "fileName": "发票1.pdf",
      "status": "success",
      "invoice": { /* Invoice 对象 */ }
    },
    {
      "id": null,
      "fileName": "发票2.jpg",
      "status": "failed",
      "error": "OCR识别失败"
    }
  ]
}
```

### 2.7 删除发票

**请求**
```
DELETE /invoices/{id}
```

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

---

## 3. 合并任务 API

### 3.1 创建合并任务

创建发票合并任务，生成 PDF 或 ZIP 文件。

**请求**
```
POST /merge-tasks
Content-Type: application/json
```

**请求体**
```json
{
  "invoiceIds": ["inv_001", "inv_002", "inv_003"],
  "outputType": "pdf",
  "layout": {
    "layout": "2x1",
    "orientation": "portrait",
    "margin": 10,
    "gap": 5,
    "showPageNumber": true,
    "showCategoryLabel": true
  }
}
```

**参数说明**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| invoiceIds | string[] | 是 | 要合并的发票 ID 列表 |
| outputType | string | 是 | 输出格式：pdf / zip |
| layout | object | 否 | 布局配置（仅 PDF 有效） |
| layout.layout | string | 否 | 每页布局：1x1 / 2x1 / 2x2 |
| layout.orientation | string | 否 | 方向：portrait / landscape |
| layout.margin | number | 否 | 边距(mm) |
| layout.gap | number | 否 | 间距(mm) |
| layout.showPageNumber | boolean | 否 | 显示页码 |
| layout.showCategoryLabel | boolean | 否 | 显示分类标签 |

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "task_001",
    "invoiceIds": ["inv_001", "inv_002", "inv_003"],
    "status": "processing",
    "outputType": "pdf",
    "totalPages": 2,
    "totalAmount": 11700.00,
    "createdAt": "2023-11-22T15:00:00Z",
    "downloadUrl": null
  }
}
```

### 3.2 获取合并任务详情

**请求**
```
GET /merge-tasks/{id}
```

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "task_001",
    "invoiceIds": ["inv_001", "inv_002", "inv_003"],
    "status": "completed",
    "outputType": "pdf",
    "totalPages": 2,
    "totalAmount": 11700.00,
    "createdAt": "2023-11-22T15:00:00Z",
    "downloadUrl": "https://storage.example.com/merged/task_001.pdf"
  }
}
```

### 3.3 获取合并任务列表

**请求**
```
GET /merge-tasks?page=1&pageSize=20
```

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "data": [
      {
        "id": "task_001",
        "status": "completed",
        "outputType": "pdf",
        "totalPages": 2,
        "totalAmount": 11700.00,
        "createdAt": "2023-11-22T15:00:00Z"
      }
    ],
    "total": 25,
    "page": 1,
    "pageSize": 20
  }
}
```

### 3.4 下载合并文件

**请求**
```
GET /merge-tasks/{id}/download
```

**响应**
- Content-Type: application/pdf 或 application/zip
- Content-Disposition: attachment; filename="invoices_merged.pdf"
- 返回文件二进制流

---

## 4. 草稿 API

### 4.1 保存草稿

保存当前选中的发票列表为草稿。

**请求**
```
POST /drafts
Content-Type: application/json
```

**请求体**
```json
{
  "invoiceIds": ["inv_001", "inv_002"],
  "name": "11月报销单"
}
```

**响应**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "draftId": "draft_001",
    "name": "11月报销单",
    "invoiceCount": 2,
    "createdAt": "2023-11-22T16:00:00Z"
  }
}
```

---

## 5. 错误码说明

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 文件格式不支持 |
| 1003 | 文件大小超限 |
| 2001 | 发票不存在 |
| 2002 | 发票已被删除 |
| 2003 | OCR识别失败 |
| 3001 | 合并任务不存在 |
| 3002 | 合并任务进行中 |
| 3003 | 合并任务失败 |
| 5001 | 服务器内部错误 |

---

## 6. 数据类型定义

### Invoice（发票）
```typescript
interface Invoice {
  id: string              // 发票ID
  code: string            // 发票代码
  number: string          // 发票号码
  type: InvoiceType       // 发票类型
  sellerName: string      // 销方名称
  buyerName: string       // 购方名称
  date: string            // 开票日期 (YYYY-MM-DD)
  amount: number          // 金额(不含税)
  taxAmount: number       // 税额
  totalAmount: number     // 价税合计
  status: InvoiceStatus   // 状态
  fileUrl: string         // 原始文件URL
  fileType: 'pdf' | 'jpg' | 'png' | 'ofd'
  createdAt: string       // 创建时间 (ISO 8601)
  updatedAt: string       // 更新时间 (ISO 8601)
}
```

### InvoiceType（发票类型）
```typescript
type InvoiceType =
  | 'vat_special'   // 增值税专用发票
  | 'vat_normal'    // 增值税普通发票
  | 'flight'        // 航空运输电子客票
  | 'taxi'          // 出租车票
  | 'hotel'         // 酒店住宿发票
  | 'other'         // 其他
```

### InvoiceStatus（发票状态）
```typescript
type InvoiceStatus =
  | 'pending'    // 待处理
  | 'verified'   // 已验真
  | 'reviewing'  // 审核中
  | 'failed'     // 验证失败
```

### MergeTask（合并任务）
```typescript
interface MergeTask {
  id: string
  invoiceIds: string[]
  status: 'pending' | 'processing' | 'completed' | 'failed'
  outputType: 'pdf' | 'zip'
  totalPages: number
  totalAmount: number
  createdAt: string
  downloadUrl?: string
}
```

---

## 7. 前端功能说明

### 7.1 文件切片上传

前端对大于 5MB 的文件自动启用切片上传：
- 切片大小：2MB
- 最大并发：3 个请求
- 支持断点续传（通过 fileHash 标识）

### 7.2 Canvas 预览渲染

前端使用 Canvas 实现发票合并预览：
- 支持 PDF 转图片预览（使用 pdf.js）
- 支持多种布局：1x1、2x1、2x2
- 支持缩放和翻页
- 支持横向/纵向切换

### 7.3 布局配置状态管理

使用 Pinia 管理布局状态：
- 布局类型（layout）
- 纸张方向（orientation）
- 边距和间距（margin, gap）
- 页码显示（showPageNumber）
- 分类标签（showCategoryLabel）
- 预览缩放（previewZoom）
- 当前页码（currentPage）
