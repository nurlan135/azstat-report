# API Documentation

**Layihə:** azstat-report  
**Versiya:** 1.0  
**Tarix:** 2026-02-01  

---

## Overview

Backend Python FastAPI və ya Flask istifadə edəcək.  
Sadə REST API - Frontend ilə əlaqə üçün.

---

## Endpoints

### 1. Upload Report

**Endpoint:** `POST /api/upload`

Fayl yükləmək və validasiya etmək.

**Request:**
```
Content-Type: multipart/form-data

file: <HTML file>
report_type: "1-isth" | "12-isth"
```

**Response (200 OK):**
```json
{
  "success": true,
  "report_id": 123,
  "organization_code": "1293461",
  "organization_name": "Salyan Rqii Neftçala Xidmət Sahəsi",
  "report_period": "2025",
  "validation": {
    "status": "passed" | "warning" | "failed",
    "error_count": 0,
    "warning_count": 2,
    "info_count": 1,
    "errors": [],
    "warnings": [
      {
        "field": "revenue",
        "category": "logical",
        "message": "Revenue changed by 403.7% from previous period",
        "severity": "warning"
      }
    ],
    "infos": [
      {
        "field": "revenue",
        "category": "anomaly",
        "message": "Previous month was 0",
        "severity": "info"
      }
    ]
  }
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Invalid file format",
  "details": "Only HTML files are allowed"
}
```

---

### 2. Get Report

**Endpoint:** `GET /api/reports/{report_id}`

Hesabatın detallarını götürmək.

**Response (200 OK):**
```json
{
  "id": 123,
  "organization_code": "1293461",
  "organization_name": "Salyan Rqii Neftçala Xidmət Sahəsi",
  "report_type": "1-isth",
  "report_period": "2025",
  "uploaded_at": "2026-02-01T21:00:00Z",
  "section_i_data": { ... },
  "section_ii_data": { ... },
  "validation_results": { ... }
}
```

---

### 3. Get History

**Endpoint:** `GET /api/reports`

Hesabat tarixcəsi.

**Query Parameters:**
- `organization_code` (optional) - Müəsisə kodu
- `report_type` (optional) - "1-isth" və ya "12-isth"
- `limit` (optional, default: 10) - Nəticə sayı

**Response (200 OK):**
```json
{
  "reports": [
    {
      "id": 123,
      "organization_code": "1293461",
      "report_type": "1-isth",
      "report_period": "2025",
      "validation_status": "warning",
      "uploaded_at": "2026-02-01T21:00:00Z"
    },
    {
      "id": 122,
      "organization_code": "1293461",
      "report_type": "12-isth",
      "report_period": "2025-12",
      "validation_status": "passed",
      "uploaded_at": "2026-01-05T14:30:00Z"
    }
  ],
  "total": 10
}
```

---

### 4. Compare Reports

**Endpoint:** `GET /api/reports/compare`

İki hesabatı müqayisə etmək.

**Query Parameters:**
- `current_id` - Cari hesabat ID
- `previous_id` - Əvvəlki hesabat ID (optional, avtomatik tapılacaq)

**Response (200 OK):**
```json
{
  "current": { ... },
  "previous": { ... },
  "comparison": {
    "revenue_change_percent": 403.7,
    "production_change_percent": 0.0,
    "anomalies": [
      {
        "field": "revenue",
        "previous_value": 592.1,
        "current_value": 2982.6,
        "change_percent": 403.7,
        "type": "large_increase"
      }
    ]
  }
}
```

---

### 5. Health Check

**Endpoint:** `GET /api/health`

Sistem sağlamlığını yoxlamaq.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Səhv input |
| 404 | Not Found - Hesabat tapılmadı |
| 500 | Internal Server Error |
| 413 | File Too Large |
| 415 | Unsupported Media Type |

---

## Rate Limiting

- 100 request/dəqiqə (hər IP üçün)
- Maksimum fayl ölçüsü: 10MB

---

## Security

- **Authentication:** Yoxdur (MVP üçün açıq)
- **Input Validation:** Bütün input-lar yoxlanılır
- **File Scanning:** Fayl tipi yoxlanılır

---

*Son update: 2026-02-01*
