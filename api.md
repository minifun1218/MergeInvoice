# 发票管理系统 API 文档

## 基础信息

- **基础路径**: `/api/v1`
- **数据格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

```json
{
  "code": 0,          // 0 表示成功，非0表示错误
  "message": "成功",  // 响应消息
  "data": {}          // 响应数据
}
```

## 分页请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 是 | 页码，从1开始 |
| pageSize | number | 是 | 每页数量 |

## 分页响应格式

```json
{
  "data": [],       // 数据列表
  "total": 100,     // 总数量
  "page": 1,        // 当前页码
  "pageSize": 10    // 每页数量
}
```

---

## 接口列表

### 1. 仪表板统计

#### GET /api/v1/dashboard/stats

获取首页仪表板统计数据。

**响应示例**:
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "processedCount": 1284,
    "processedChange": 12.5,
    "pendingCount": 12,
    "pendingChange": -2.4,
    "savedTax": 4590.20,
    "savedChange": 5.8
  }
}
```

---

### 2. 发票管理

#### GET /api/v1/invoices

获取发票列表（分页）。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 是 | 页码 |
| pageSize | number | 是 | 每页数量 |
| status | string | 否 | 状态筛选：verified/reviewing/pending/failed |
| keyword | string | 否 | 搜索关键词 |

**响应示例**:
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "data": [
      {
        "id": "1",
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
        "fileUrl": "/files/invoice_1.pdf",
        "fileType": "pdf",
        "createdAt": "2023-11-20T10:00:00Z",
        "updatedAt": "2023-11-20T10:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
}
```

---

#### GET /api/v1/invoices/:id

获取发票详情。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 发票ID |

**响应示例**:
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": "1",
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
    "fileUrl": "/files/invoice_1.pdf",
    "fileType": "pdf",
    "createdAt": "2023-11-20T10:00:00Z",
    "updatedAt": "2023-11-20T10:00:00Z"
  }
}
```

---

#### POST /api/v1/invoices/upload

上传单张发票文件（支持进度回调）。

**请求格式**: `multipart/form-data`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 发票文件（PDF/JPG/PNG，最大10MB） |

**响应示例**:
```json
{
  "code": 0,
  "message": "上传成功",
  "data": {
    "id": "new-invoice-id",
    "code": "044001900112",
    "number": "87654321",
    "type": "vat_normal",
    "sellerName": "识别的销方名称",
    "buyerName": "识别的购方名称",
    "date": "2023-11-25",
    "amount": 500.00,
    "taxAmount": 65.00,
    "totalAmount": 565.00,
    "status": "pending",
    "fileUrl": "/files/invoice_new.pdf",
    "fileType": "pdf",
    "createdAt": "2023-11-25T10:00:00Z",
    "updatedAt": "2023-11-25T10:00:00Z"
  }
}
```

---

#### POST /api/v1/invoices/batch-upload

批量上传发票文件。

**请求格式**: `multipart/form-data`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| files | File[] | 是 | 多个发票文件 |

**响应示例**:
```json
{
  "code": 0,
  "message": "批量上传成功",
  "data": [
    { "id": "1", "... 发票信息" },
    { "id": "2", "... 发票信息" }
  ]
}
```

---

#### DELETE /api/v1/invoices/:id

删除发票。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 发票ID |

**响应示例**:
```json
{
  "code": 0,
  "message": "删除成功",
  "data": null
}
```

---

### 3. 合并任务

#### POST /api/v1/merge-tasks

创建发票合并任务。

**请求格式**: `application/json`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| invoiceIds | string[] | 是 | 要合并的发票ID列表 |
| outputType | string | 是 | 输出类型：pdf / zip |

**请求示例**:
```json
{
  "invoiceIds": ["1", "2", "3"],
  "outputType": "pdf"
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "任务创建成功",
  "data": {
    "id": "task-123",
    "status": "processing",
    "invoiceIds": ["1", "2", "3"],
    "outputType": "pdf",
    "progress": 0,
    "createdAt": "2023-11-25T10:00:00Z"
  }
}
```

---

#### GET /api/v1/merge-tasks/:id

获取合并任务详情。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 任务ID |

**响应示例**:
```json
{
  "code": 0,
  "message": "成功",
  "data": {
    "id": "task-123",
    "status": "completed",
    "invoiceIds": ["1", "2", "3"],
    "outputType": "pdf",
    "progress": 100,
    "downloadUrl": "/api/v1/merge-tasks/task-123/download",
    "createdAt": "2023-11-25T10:00:00Z",
    "completedAt": "2023-11-25T10:01:00Z"
  }
}
```

---

#### GET /api/v1/merge-tasks

获取合并任务列表（分页）。

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 是 | 页码 |
| pageSize | number | 是 | 每页数量 |

---

#### GET /api/v1/merge-tasks/:id/download

下载合并后的文件。

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 任务ID |

**响应**: 文件流（PDF或ZIP）

---

### 4. 草稿管理

#### POST /api/v1/drafts

保存草稿。

**请求格式**: `application/json`

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| invoiceIds | string[] | 是 | 发票ID列表 |

**请求示例**:
```json
{
  "invoiceIds": ["1", "2", "3"]
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "草稿保存成功",
  "data": {
    "draftId": "draft-456"
  }
}
```

---

## 数据类型说明

### 发票类型 (type)
| 值 | 说明 |
|------|------|
| vat_special | 增值税专用发票 |
| vat_normal | 增值税普通发票 |
| flight | 航空运输电子客票 |
| taxi | 打车费发票 |
| hotel | 酒店住宿发票 |
| other | 其他发票 |

### 发票状态 (status)
| 值 | 说明 |
|------|------|
| pending | 待处理 |
| reviewing | 审核中 |
| verified | 已验真 |
| failed | 验证失败 |

### 合并任务状态
| 值 | 说明 |
|------|------|
| processing | 处理中 |
| completed | 已完成 |
| failed | 失败 |

---

## 错误码

| 错误码 | 说明 |
|------|------|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
