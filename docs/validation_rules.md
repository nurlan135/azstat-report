# Validation Rules

**Layihə:** azstat-report  
**Versiya:** 1.0  
**Tarix:** 2026-02-01  

---

## Overview

4 kateqoriyada validation qaydaları tətbiq ediləcək.

---

## Severity Levels

| Level | Icon | Təsir | Action |
|-------|------|-------|--------|
| **ERROR** | ❌ | Bloklayıcı | Hesabat təslim edilə bilməz |
| **WARNING** | ⚠️ | Diqqət tələb edir | Yoxlanılmalı, təslim oluna bilər |
| **INFO** | ℹ️ | Məlumat | Anomaliya, diqqət çəkir |

---

## 1. ERROR Rules (Bloklayıcı)

### 1.1 Required Fields

| Field | Check |
|-------|-------|
| organization_code | Boş və ya null olmamalı |
| report_period | Boş və ya null olmamalı |
| section_i_data | Boş olmamalı |

**Nümunə:**
```python
if not report_data.get('organization_code'):
    result.severity = ERROR
    result.message = "Organization code is required"
```

### 1.2 Negative Values

Mənfi dəyərlər qəbul edilmir.

| Field | Check |
|-------|-------|
| revenue | >= 0 |
| production | >= 0 |
| internal_use | >= 0 |
| shipped | >= 0 |

**Nümunə:**
```python
if section_i.get('revenue', 0) < 0:
    result.severity = ERROR
    result.message = "Revenue cannot be negative"
```

### 1.3 Invalid Data Types

Səhv data tipləri.

| Field | Expected Type |
|-------|---------------|
| revenue | float |
| production | float |
| row_code | string (format: X, X.X, X.X.X) |

**Nümunə:**
```python
if not isinstance(revenue, (int, float)):
    result.severity = ERROR
    result.message = "Revenue must be a number"
```

### 1.4 Organization Code Format

VÖEN 7 rəqəm olmalıdır.

```python
import re

if not re.match(r'^\d{7}$', org_code):
    result.severity = ERROR
    result.message = "Organization code must be 7 digits"
```

---

## 2. WARNING Rules (Logical)

### 2.1 Revenue vs Production

Gəlir istehsaldan kiçik ola bilməz (məntiqi yoxlama).

```python
revenue = section_i.get('revenue', 0)
own_production = section_i.get('own_production', 0)

if own_production > 0 and revenue < own_production * 0.5:
    result.severity = WARNING
    result.message = "Revenue is significantly lower than production"
```

### 2.2 Inventory Continuity

Anbar davamlılığı yoxlaması.

```
İl sonu = İl əvvəli + İstehsal - Daxili istifadə - Satılan
```

```python
# 2.2 = 2.1 + istehsal - daxili_istifade - satilan
eoy = section_i.get('2.2', 0)
boy = section_i.get('2.1', 0)
production = section_i.get('production', 0)
internal_use = section_i.get('internal_use', 0)
shipped = section_i.get('shipped', 0)

expected_eoy = boy + production - internal_use - shipped
if abs(eoy - expected_eoy) > 0.1:  # 0.1 tolerance
    result.severity = WARNING
    result.message = "Inventory calculation mismatch"
```

### 2.3 Internal Use vs Production

Daxili istifadə ümumi istehsalı aşa bilməz.

```python
if internal_use > production * 0.5:
    result.severity = WARNING
    result.message = "Internal use exceeds 50% of production"
```

### 2.4 Export Without Import

İxrac varsa, idxal da olmalıdır (məntiqi).

```python
export_value = section_i.get('export_value', 0)
import_value = section_i.get('import_value', 0)

if export_value > 0 and import_value == 0:
    result.severity = WARNING
    result.message = "Export recorded but no import found"
```

---

## 3. WARNING Rules (Consistency)

### 3.1 Column Consistency

Sütunlar arası uyğunluq.

| Check | Rule |
|-------|------|
| Column 2 | <= Column 1 |
| Column 3 | <= Column 1 |
| Column 4 | <= Column 1 |

```python
col1 = section_i.get('column_1', 0)
col2 = section_i.get('column_2', 0)

if col2 > col1:
    result.severity = WARNING
    result.message = "Column 2 cannot exceed Column 1"
```

### 3.2 Row Totals

Cəmi sətirlərin düzgünlüyü.

```python
# 1 = 1.1 + 1.2 + ...
row_1 = section_i.get('1', 0)
row_1_1 = section_i.get('1.1', 0)
row_1_2 = section_i.get('1.2', 0)

expected_total = row_1_1 + row_1_2
if abs(row_1 - expected_total) > 0.1:
    result.severity = WARNING
    result.message = "Row 1 doesn't match sum of sub-rows"
```

---

## 4. INFO Rules (Anomaly)

### 4.1 Large Changes (>50%)

Əvvəlki dövr ilə müqayisədə kəskin dəyişiklik.

```python
revenue_change = abs(current - previous) / previous * 100

if revenue_change > 50:
    result.severity = INFO
    result.message = f"Revenue changed by {revenue_change:.1f}%"
```

### 4.2 Zero Values

Əvvəlki dövr mövcud idisə, indi sıfır olmamalıdır.

```python
if prev_revenue > 0 and current_revenue == 0:
    result.severity = INFO
    result.message = "Revenue dropped to zero from previous period"
```

### 4.3 Unusual Patterns

Qeyri-adi pattern-lər.

```python
# Eyni dəyər təkrarlanır
if section_i.get('revenue') == section_i.get('own_production'):
    result.severity = INFO
    result.message = "Revenue equals production - check for accuracy"

# Kəskin artış/azalma
if revenue_change > 100:
    result.severity = INFO
    result.message = f"Unusual change: {revenue_change:.1f}% increase"
```

### 4.4 Export/Import Mismatch

İxrac idxaldan çox olmamalıdır.

```python
if export_value > import_value * 2:
    result.severity = INFO
    result.message = "Export significantly exceeds import"
```

---

## Validation Flow

```
┌─────────────────┐
│  Parse HTML     │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Check Required │
│  Fields (ERROR) │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Check Negative │
│  Values (ERROR) │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Check Logical  │
│  Rules (WARNING)│
└────────┬────────┘
         ▼
┌─────────────────┐
│  Check          │
│  Consistency    │
│  (WARNING)      │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Get Previous   │
│  Report (if any)│
└────────┬────────┘
         ▼
┌─────────────────┐
│  Check Anomalies│
│  (INFO)         │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Return Results │
└─────────────────┘
```

---

## Status Determination

| Condition | Final Status |
|-----------|--------------|
| error_count > 0 | **FAILED** |
| warning_count > 0 | **WARNING** |
| error_count == 0 AND warning_count == 0 | **PASSED** |

---

*Son update: 2026-02-01*
