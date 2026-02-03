# Database Schema

**Layihə:** azstat-report  
**Versiya:** 1.0  
**Tarix:** 2026-02-01  

---

## Overview

SQLite database istifadə ediləcək. Sadə, portable, serverless həll.

---

## Tables

### 1. reports (Əsas cədvəl)

Bütün yüklənmiş hesabatları saxlayır.

```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Organization Info
    organization_code TEXT NOT NULL,      -- VÖEN (7 rəqəm)
    organization_name TEXT,               -- Müəsisənin adı
    organization_region INTEGER,          -- Ərazi kodu
    organization_property TEXT,           -- Mülkiyyət növü
    organization_activity_code TEXT,      -- Fəaliyyət kodu (NACE)
    
    -- Report Info
    report_type TEXT NOT NULL,            -- '1-isth' və ya '12-isth'
    report_period TEXT NOT NULL,          -- '2025' (1-isth) və ya '2025-12' (12-isth)
    
    -- File Info
    file_path TEXT,                       -- Original HTML fayl yolu
    file_size INTEGER,                    -- Fayl ölçüsü (bytes)
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Parsed Data (JSON)
    section_i_data TEXT,                  -- Section I məlumatları (JSON)
    section_ii_data TEXT,                 -- Section II məlumatları (JSON)
    
    -- Validation Results (JSON)
    validation_results TEXT,              -- Validation nəticələri (JSON)
    validation_status TEXT,               -- 'passed', 'warning', 'failed'
    
    -- Indexes
    UNIQUE(organization_code, report_type, report_period)
);
```

---

## Indexes

```sql
-- Tez axtarış üçün
CREATE INDEX idx_reports_org_period 
ON reports(organization_code, report_type, report_period);

CREATE INDEX idx_reports_uploaded_at 
ON reports(uploaded_at DESC);

CREATE INDEX idx_reports_type 
ON reports(report_type);
```

---

## Data Examples

### Section I Data (JSON format)

```json
{
  "rows": [
    {
      "row_code": "1",
      "row_name": "Malların satışı...",
      "current_year": 2982.6,
      "previous_year": 592.1
    },
    {
      "row_code": "1.1",
      "row_name": "müəsisənin öz istehsalı...",
      "current_year": 2982.6,
      "previous_year": 592.1
    }
  ]
}
```

### Section II Data (JSON format)

```json
{
  "products": [
    {
      "product_code": "352210000",
      "product_name": "Qazşəkilli yanacağın boru kəməri...",
      "unit": "mln. kub metr",
      "produced": 23.6,
      "internal_use": 1.7,
      "sold_quantity": 21.9,
      "sold_value": 2982.6,
      "year_end_stock": 0.0,
      "import_material_value": 0.0
    }
  ]
}
```

### Validation Results (JSON format)

```json
{
  "status": "warning",
  "summary": {
    "error_count": 0,
    "warning_count": 2,
    "info_count": 1
  },
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
```

---

## Example Queries

### Son 10 hesabatı götür

```sql
SELECT * FROM reports 
ORDER BY uploaded_at DESC 
LIMIT 10;
```

### Müəsisənin tarixcəsi

```sql
SELECT * FROM reports 
WHERE organization_code = '1293461' 
  AND report_type = '1-isth'
ORDER BY report_period;
```

### Əvvəlki dövr ilə müqayisə

```sql
SELECT r1.*, r2.report_period as prev_period
FROM reports r1
LEFT JOIN reports r2 
  ON r1.organization_code = r2.organization_code
  AND r1.report_type = r2.report_type
  AND r2.report_period < r1.report_period
WHERE r1.id = ?
ORDER BY r2.uploaded_at DESC
LIMIT 1;
```

---

## File Structure

```
azstat-report/
├── backend/
│   └── database.py        # Database handler
└── data/
    └── reports.db         # SQLite database file
```

---

*Son update: 2026-02-01*
