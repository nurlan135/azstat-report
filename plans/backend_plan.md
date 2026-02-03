# Backend Development Plan

**Layihə:** azstat-report  
**Versiya:** 1.0  
**Tarix:** 2026-02-02  
**Hədəf:** Week 1 (Backend Core)  

---

## Overview

Bu plan azstat-report backend-inin inkişafını əhatə edir. Backend Python ilə yazılacaq və 3 əsas moduldan ibarət olacaq:
- **Parser** - HTML formadan məlumat çıxarır
- **Validator** - 4 kateqoriya üzrə yoxlama aparır  
- **Database** - SQLite ilə işləyir

---

## 1. Project Structure

```
azstat-report/
├── backend/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── parser.py            # HTML Parser
│   ├── validator.py         # Validation Engine
│   ├── database.py          # SQLite Database Handler
│   ├── models.py            # Data models (Pydantic)
│   ├── config.py            # Configuration
│   └── requirements.txt     # Dependencies
├── data/
│   └── reports.db           # SQLite database
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_validator.py
│   └── test_database.py
└── plans/
    └── backend_plan.md      # Bu fayl
```

---

## 2. Dependencies (requirements.txt)

```txt
# Core
python>=3.10

# HTML Parsing
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Data Validation
pydantic>=2.0.0

# Web API
fastapi>=0.100.0
uvicorn>=0.23.0

# CLI
click>=8.0.0

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# Utilities
python-dateutil>=2.8.0
```

---

## 3. Module Details

### 3.1 config.py

```python
# Konfiqurasiya faylı

class Config:
    """Application configuration."""
    
    # Database
    DB_PATH = "data/reports.db"
    
    # File limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".html", ".htm"}
    
    # Validation
    ANOMALY_THRESHOLD = 0.5  # 50% dəyişiklik
    
    # Paths
    UPLOAD_DIR = "data/uploads"
```

### 3.2 models.py

```python
# Pydantic modelləri

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OrganizationInfo(BaseModel):
    """Organization info from form header."""
    code: str                      # VÖEN
    name: str
    region: int
    property_type: str
    activity_code: str
    organization_type: int

class SectionIRow(BaseModel):
    """Section I row data."""
    row_code: str
    row_name: str
    current_year: float
    previous_year: float

class SectionI(BaseModel):
    """Section I data."""
    rows: List[SectionIRow]

class ProductRow(BaseModel):
    """Section II product row."""
    product_code: str
    product_name: str
    unit: str
    produced: float
    internal_use: float
    sold_quantity: float
    sold_value: float
    year_end_stock: float
    import_value: float

class SectionII(BaseModel):
    """Section II products data."""
    products: List[ProductRow]

class ReportData(BaseModel):
    """Complete parsed report."""
    organization: OrganizationInfo
    report_type: str              # '1-isth' or '12-isth'
    report_period: str            # '2025' or '2025-12'
    section_i: SectionI
    section_ii: SectionII
    uploaded_at: datetime

class ValidationIssue(BaseModel):
    """Single validation issue."""
    category: str                 # 'error', 'warning', 'info'
    field: str
    message: str
    severity: str                 # 'blocking', 'logical', 'consistency', 'anomaly'

class ValidationResult(BaseModel):
    """Validation result summary."""
    status: str                   # 'passed', 'warning', 'failed'
    error_count: int
    warning_count: int
    info_count: int
    issues: List[ValidationIssue]

class ReportRecord(BaseModel):
    """Full report record for database."""
    organization_code: str
    organization_name: str
    report_type: str
    report_period: str
    section_i_data: str           # JSON string
    section_ii_data: str          # JSON string
    validation_results: str       # JSON string
    validation_status: str
    uploaded_at: datetime
```

### 3.3 parser.py

```python
# HTML Parser - azstat.gov.az formalarını parse edir

from bs4 import BeautifulSoup
from models import OrganizationInfo, SectionIRow, SectionI, ProductRow, SectionII, ReportData

class AzstatParser:
    """Parser for azstat.gov.az HTML reports."""
    
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')
        self.report_type = self._detect_report_type()
    
    def _detect_report_type(self) -> str:
        """Detect 1-isth (annual) or 12-isth (monthly)."""
        # Form koduna əsasən təyin et
        form_code = self.soup.find('input', {'name': 'formCode'})
        if form_code:
            code = form_code.get('value', '')
            if code == '03104055':
                return '1-isth'
            elif code == '03104047':
                return '12-isth'
        return 'unknown'
    
    def parse_organization_info(self) -> OrganizationInfo:
        """Parse organization header info."""
        # Form structure:
        # name="organization.code" → VÖEN
        # name="organization.name" → Ad
        # name="organization.region" → Region
        
        code_input = self.soup.find('input', {'name': lambda x: x and 'code' in x.lower()})
        # ... daha ətraflı implementasiya
        
    def parse_section_i(self) -> SectionI:
        """Parse Section I - financial data."""
        rows = []
        # tab1:0:j_idt51:j_idt55 formatında inputlar
        # 16 rows (1, 1.1, 1.1.1, 2, 2.1, 2.2, 3, 3.1, 3.2, 4, 5, 6, 7, 8, 9)
        
    def parse_section_ii(self) -> SectionII:
        """Parse Section II - products table."""
        products = []
        # Dinamik cədvəl - 9 columns
        # Product Code, Name, Unit, Produced, Internal Use, Sold Qty, 
        # Sold Value, Year End Stock, Import Value
        
    def parse(self) -> ReportData:
        """Parse complete report."""
        return ReportData(
            organization=self.parse_organization_info(),
            report_type=self.report_type,
            report_period=self._extract_period(),
            section_i=self.parse_section_i(),
            section_ii=self.parse_section_ii(),
            uploaded_at=datetime.now()
        )
    
    def _extract_period(self) -> str:
        """Extract report period from form."""
        # 1-isth → illik (2025)
        # 12-isth → aylıq (2025-12)
```

### 3.4 validator.py

```python
# Validation Engine - 4 kateqoriya üzrə yoxlama

from models import ReportData, ValidationResult, ValidationIssue
from typing import List

class ValidationEngine:
    """Report validation engine."""
    
    def __init__(self, report: ReportData, previous_report: ReportData = None):
        self.report = report
        self.previous_report = previous_report
        self.issues: List[ValidationIssue] = []
    
    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        self._check_errors()
        self._check_logical_warnings()
        self._check_consistency_warnings()
        self._check_anomalies()
        
        status = self._determine_status()
        return ValidationResult(
            status=status,
            error_count=len([i for i in self.issues if i.category == 'error']),
            warning_count=len([i for i in self.issues if i.category == 'warning']),
            info_count=len([i for i in self.issues if i.category == 'info']),
            issues=self.issues
        )
    
    def _check_errors(self):
        """ERROR: Blocking errors - report cannot be submitted."""
        # 1. Mənfi dəyərlər yoxlaması
        for row in self.report.section_i.rows:
            if row.current_year < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_i.{row.row_code}.current_year',
                    message=f'Negative value: {row.current_year}',
                    severity='blocking'
                ))
        
        # 2. Boş köhnə sahələr (kod, ad)
        if not self.report.organization.code:
            self.issues.append(ValidationIssue(
                category='error',
                field='organization.code',
                message='Organization code is missing',
                severity='blocking'
            ))
        
        # 3. Səhv data tipi (əgər string varsa float yerində)
    
    def _check_logical_warnings(self):
        """WARNING: Logical consistency issues."""
        # 1. Gəlir < Öz istehsalı + Ticarət əlavəsi
        # row 1 = row 1.1 + row 1.2 (əgər mövcuddursa)
        
        # 2. Anbar continuity
        # row 3 (Year End Stock) = row 1 (Prev Year) + Production - Shipped
        
        # 3. Daxili ehtiyac > Ümumi istehsal
        
        # 4. Sold + Stock > Production + Previous (mümkün deyil)
    
    def _check_consistency_warnings(self):
        """WARNING: Column consistency."""
        # 1. Sütun 4 (internal_use) <= Sütun 3 (produced)
        for product in self.report.section_ii.products:
            if product.internal_use > product.produced:
                self.issues.append(ValidationIssue(
                    category='warning',
                    field=f'section_ii.{product.product_code}.internal_use',
                    message=f'Internal use ({product.internal_use}) > Production ({product.produced})',
                    severity='consistency'
                ))
        
        # 2. Shipped + Stock <= Production + Previous
        for product in self.report.section_ii.products:
            total_available = product.produced + self._get_previous_stock(product)
            total_used = product.sold_quantity + product.year_end_stock
            if total_used > total_available:
                self.issues.append(ValidationIssue(
                    category='warning',
                    field=f'section_ii.{product.product_code}',
                    message=f'Sold + Stock ({total_used}) > Available ({total_available})',
                    severity='consistency'
                ))
    
    def _check_anomalies(self):
        """INFO: Anomaly detection."""
        # 1. Gəlir dəyişikliyi > 50%
        if self.previous_report:
            current_revenue = self._get_total_revenue()
            previous_revenue = self._get_previous_revenue()
            if previous_revenue > 0:
                change = abs(current_revenue - previous_revenue) / previous_revenue
                if change > 0.5:
                    self.issues.append(ValidationIssue(
                        category='info',
                        field='total_revenue',
                        message=f'Revenue changed by {change*100:.1f}%',
                        severity='anomaly'
                    ))
        
        # 2. İxrac/idxal uyğunsuzluğu
        # Əgər ixrac varsa, idxal da olmalıdır (və ya əksinə)
        
        # 3. Sıfır dəyərlər (məlumat itkisi?)
        # Əgər əvvəlki dövrdə dəyər varsa və indi 0-dır
        
        # 4. Sifarişlərin kəskin azalması
    
    def _determine_status(self) -> str:
        """Determine overall validation status."""
        has_errors = any(i.category == 'error' for i in self.issues)
        has_warnings = any(i.category == 'warning' for i in self.issues)
        
        if has_errors:
            return 'failed'
        elif has_warnings:
            return 'warning'
        else:
            return 'passed'
    
    def _get_total_revenue(self) -> float:
        """Get total revenue from Section I."""
        # row 1 - "Malların satışı"
        return self.report.section_i.rows[0].current_year if self.report.section_i.rows else 0
    
    def _get_previous_revenue(self) -> float:
        """Get previous period revenue."""
        if self.previous_report:
            return self._get_total_revenue()
        return self.report.section_i.rows[0].previous_year if self.report.section_i.rows else 0
    
    def _get_previous_stock(self, product) -> float:
        """Get previous year end stock for product."""
        if self.previous_report:
            for prev_product in self.previous_report.section_ii.products:
                if prev_product.product_code == product.product_code:
                    return prev_product.year_end_stock
        return 0
```

### 3.5 database.py

```python
# SQLite Database Handler

import sqlite3
import json
from datetime import datetime
from models import ReportData, ReportRecord, ValidationResult
from pathlib import Path

class DatabaseHandler:
    """SQLite database operations."""
    
    def __init__(self, db_path: str = "data/reports.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_code TEXT NOT NULL,
                    organization_name TEXT,
                    report_type TEXT NOT NULL,
                    report_period TEXT NOT NULL,
                    section_i_data TEXT,
                    section_ii_data TEXT,
                    validation_results TEXT,
                    validation_status TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(organization_code, report_type, report_period)
                )
            ''')
            
            # Indexes
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_org_period 
                ON reports(organization_code, report_type, report_period)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_uploaded_at 
                ON reports(uploaded_at DESC)
            ''')
    
    def save_report(self, report: ReportData, validation: ValidationResult) -> int:
        """Save report to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO reports (
                    organization_code, organization_name, report_type, 
                    report_period, section_i_data, section_ii_data,
                    validation_results, validation_status, uploaded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                report.organization.code,
                report.organization.name,
                report.report_type,
                report.report_period,
                report.section_i.model_dump_json(),
                report.section_ii.model_dump_json(),
                validation.model_dump_json(),
                validation.status,
                report.uploaded_at
            ))
            return conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    def get_report(self, report_id: int) -> ReportRecord:
        """Get report by ID."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                'SELECT * FROM reports WHERE id = ?', (report_id,)
            ).fetchone()
            if row:
                return ReportRecord(*row)
            return None
    
    def get_latest_report(self, org_code: str, report_type: str, period: str):
        """Get previous report for comparison."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute('''
                SELECT * FROM reports 
                WHERE organization_code = ? 
                  AND report_type = ?
                  AND report_period < ?
                ORDER BY report_period DESC
                LIMIT 1
            ''', (org_code, report_type, period)).fetchone()
            if row:
                return ReportRecord(*row)
            return None
    
    def get_history(self, org_code: str = None, limit: int = 10):
        """Get report history."""
        with sqlite3.connect(self.db_path) as conn:
            if org_code:
                return conn.execute('''
                    SELECT * FROM reports 
                    WHERE organization_code = ?
                    ORDER BY uploaded_at DESC
                    LIMIT ?
                ''', (org_code, limit)).fetchall()
            return conn.execute('''
                SELECT * FROM reports 
                ORDER BY uploaded_at DESC
                LIMIT ?
            ''', (limit,)).fetchall()
    
    def get_statistics(self):
        """Get overall statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute('SELECT COUNT(*) FROM reports').fetchone()[0]
            passed = conn.execute(
                "SELECT COUNT(*) FROM reports WHERE validation_status = 'passed'"
            ).fetchone()[0]
            warnings = conn.execute(
                "SELECT COUNT(*) FROM reports WHERE validation_status = 'warning'"
            ).fetchone()[0]
            failed = conn.execute(
                "SELECT COUNT(*) FROM reports WHERE validation_status = 'failed'"
            ).fetchone()[0]
            
            return {
                'total': total,
                'passed': passed,
                'warnings': warnings,
                'failed': failed
            }
```

### 3.6 main.py

```python
# CLI Entry Point (FastAPI + Click)

import click
from pathlib import Path
from parser import AzstatParser
from validator import ValidationEngine
from database import DatabaseHandler

# ========================
# CLI Commands (Click)
# ========================

@click.group()
def cli():
    """azstat-report CLI tool."""
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--compare/--no-compare', default=False, help='Compare with previous report')
def validate(file_path: str, compare: bool):
    """Validate an HTML report file."""
    click.echo(f"Validating: {file_path}")
    
    # Parse HTML
    with open(file_path) as f:
        html_content = f.read()
    
    parser = AzstatParser(html_content)
    report = parser.parse()
    
    click.echo(f"Report type: {report.report_type}")
    click.echo(f"Period: {report.report_period}")
    click.echo(f"Organization: {report.organization.name}")
    
    # Get previous report for comparison
    previous_report = None
    if compare:
        db = DatabaseHandler()
        prev_record = db.get_latest_report(
            report.organization.code,
            report.report_type,
            report.report_period
        )
        if prev_record:
            previous_report = prev_record
    
    # Validate
    engine = ValidationEngine(report, previous_report)
    result = engine.validate()
    
    # Print results
    click.echo(f"\nValidation Status: {result.status.upper()}")
    click.echo(f"Errors: {result.error_count}")
    click.echo(f"Warnings: {result.warning_count}")
    click.echo(f"Infos: {result.info_count}")
    
    if result.issues:
        click.echo("\nIssues:")
        for issue in result.issues:
            click.echo(f"  [{issue.category.upper()}] {issue.field}: {issue.message}")
    
    # Save to database
    db = DatabaseHandler()
    report_id = db.save_report(report, result)
    click.echo(f"\nSaved to database (ID: {report_id})")

@cli.command()
def history():
    """Show report history."""
    db = DatabaseHandler()
    reports = db.get_history(limit=20)
    
    click.echo("\nReport History:")
    click.echo("-" * 80)
    for r in reports:
        click.echo(f"{r[0]:3} | {r[3]:8} | {r[4]:7} | {r[8][:10]} | {r[7]:8}")

@cli.command()
def stats():
    """Show statistics."""
    db = DatabaseHandler()
    stats = db.get_statistics()
    
    click.echo("\nStatistics:")
    click.echo(f"Total reports: {stats['total']}")
    click.echo(f"Passed: {stats['passed']}")
    click.echo(f"Warnings: {stats['warnings']}")
    click.echo(f"Failed: {stats['failed']}")


# ========================
# Web API (FastAPI)
# ========================

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI(
    title="azstat-report API",
    description="Azərbaycan statistik hesabatlarının validasiya sistemi",
    version="1.0.0"
)

# CORS (frontend üçün)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """API sağlamlıq yoxlaması."""
    return {"status": "ok", "message": "azstat-report API working"}


@app.post("/api/upload")
async def upload_report(file: UploadFile = File(...)):
    """
    HTML fayl yükləmək və validasiya etmək.
    
    - file: HTML fayl
    - compare: Əvvəlki dövr ilə müqayisə (query param)
    """
    # Fayl tipi yoxlaması
    if not file.filename.endswith(('.html', '.htm')):
        raise HTTPException(status_code=400, detail="Only HTML files allowed")
    
    # Fayl oxumaq
    content = await file.read()
    
    # Parse
    parser = AzstatParser(content.decode('utf-8'))
    report = parser.parse()
    
    # Əvvəlki hesabatı tap (müqayisə üçün)
    db = DatabaseHandler()
    previous_record = db.get_latest_report(
        report.organization.code,
        report.report_type,
        report.report_period
    )
    previous_report = previous_record  # Deserialize lazımdır
    
    # Validate
    engine = ValidationEngine(report, previous_report)
    result = engine.validate()
    
    # Save
    report_id = db.save_report(report, result)
    
    return {
        "report_id": report_id,
        "status": result.status,
        "organization": report.organization.name,
        "report_type": report.report_type,
        "report_period": report.report_period,
        "summary": {
            "errors": result.error_count,
            "warnings": result.warning_count,
            "infos": result.info_count
        },
        "issues": result.issues
    }


@app.get("/api/reports/{report_id}")
def get_report(report_id: int):
    """Hesabat detallarını götürmək."""
    db = DatabaseHandler()
    report = db.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/api/reports")
def list_reports(limit: int = 10, organization_code: Optional[str] = None):
    """Hesabat siyahısı."""
    db = DatabaseHandler()
    reports = db.get_history(org_code=organization_code, limit=limit)
    return {"reports": reports}


@app.get("/api/reports/compare")
def compare_reports(current_id: int, previous_id: int = None):
    """İki hesabatı müqayisə etmək."""
    db = DatabaseHandler()
    
    current = db.get_report(current_id)
    if not current:
        raise HTTPException(status_code=404, detail="Current report not found")
    
    if previous_id:
        previous = db.get_report(previous_id)
    else:
        # Əvvəlki dövrü avtomatik tap
        previous = db.get_latest_report(
            current.organization_code,
            current.report_type,
            current.report_period
        )
    
    if not previous:
        return {"message": "No previous report found for comparison"}
    
    return {
        "current": current,
        "previous": previous,
        "comparison": {
            "revenue_change": "...",
            "products_added": "...",
            "products_removed": "..."
        }
    }


@app.get("/api/stats")
def get_statistics():
    """Ümumi statistika."""
    db = DatabaseHandler()
    return db.get_statistics()


# ========================
# Main Entry Point
# ========================

if __name__ == '__main__':
    import uvicorn
    # CLI və ya Server modu
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        cli()
```

---

## 4. Implementation Steps

### Phase 1: Setup (Day 1-2)

- [ ] Create backend directory structure
- [ ] Create requirements.txt
- [ ] Setup virtual environment
- [ ] Create config.py with all settings
- [ ] Create models.py with Pydantic models
- [ ] Initialize git repository

### Phase 2: Parser (Day 3-4)

- [ ] Implement AzstatParser class
- [ ] Parse organization info from HTML header
- [ ] Parse Section I (16 rows × 2 columns)
- [ ] Parse Section II (dynamic product table)
- [ ] Test with real HTML files
- [ ] Add error handling for malformed HTML

### Phase 3: Validator (Day 5-6)

- [ ] Implement ValidationEngine class
- [ ] Implement ERROR checks (negative values, missing fields)
- [ ] Implement logical WARNING checks
- [ ] Implement consistency WARNING checks
- [ ] Implement anomaly INFO checks
- [ ] Add previous period comparison logic
- [ ] Test all validation rules

### Phase 4: Database (Day 7)

- [ ] Implement DatabaseHandler class
- [ ] Create SQLite schema
- [ ] Implement save/get methods
- [ ] Implement history queries
- [ ] Implement statistics queries

### Phase 5: CLI + API Integration (Day 8-9)

- [ ] Implement main.py with Click CLI
- [ ] Implement FastAPI app
- [ ] Add validate command (CLI)
- [ ] Add history command (CLI)
- [ ] Add stats command (CLI)
- [ ] Implement /api/upload endpoint
- [ ] Implement /api/reports endpoints
- [ ] Implement /api/stats endpoint
- [ ] Test CLI end-to-end
- [ ] Test API with curl/Postman

### Phase 6: Testing (Day 10-11)

- [ ] Write unit tests for parser
- [ ] Write unit tests for validator
- [ ] Write unit tests for database
- [ ] Run all tests
- [ ] Fix bugs and edge cases

---

## 5. HTML Form Structure Reference

### Organization Info Table

| Field | HTML Name Pattern | Example |
|-------|------------------|---------|
| Organization Code | `organization.code` | 1293461 |
| Organization Name | `organization.name` | Salyan Rqii... |
| Region | `organization.region` | 807 |
| Property | `organization.property` | Dövlət |
| Activity Code | `organization.activity` | 35231 |
| Type | `organization.type` | 3 |

### Section I (tab1)

**Rows:** 16 rows (1, 1.1, 1.1.1, 2, 2.1, 2.2, 3, 3.1, 3.2, 4, 5, 6, 7, 8, 9)

**Input Pattern:** `name="tab1:{row_index}:j_idt51:j_idt55"`

**Columns:**
- Current Year
- Previous Year

### Section II (tab2)

**Product Table Columns:**
1. Product Code
2. Product Name  
3. Unit
4. Produced
5. Internal Use
6. Sold Quantity
7. Sold Value
8. Year End Stock
9. Import Value

---

## 6. Testing Strategy

### Unit Tests (pytest)

```python
# test_parser.py
def test_parse_organization_info():
    # Test organization parsing
    pass

def test_parse_section_i_rows():
    # Test Section I parsing
    pass

def test_parse_section_ii_products():
    # Test Section II parsing
    pass

# test_validator.py
def test_negative_value_error():
    # Test error detection
    pass

def test_consistency_warning():
    # Test warning detection
    pass

def test_anomaly_detection():
    # Test anomaly detection
    pass

def test_previous_period_comparison():
    # Test comparison logic
    pass

# test_database.py
def test_save_and_retrieve():
    # Test database save/load
    pass

def test_history_query():
    # Test history retrieval
    pass
```

### Integration Tests

- Test full parse → validate → save flow
- Test with real azstat.gov.az HTML files
- Test edge cases (missing data, malformed HTML)

---

## 7. Success Criteria

### Must Have (MVP)
- [ ] HTML parser extracts all data correctly
- [ ] All 4 validation categories work
- [ ] CLI validate command works
- [ ] SQLite database stores and retrieves reports
- [ ] Response time < 5 seconds

### Should Have
- [ ] History command shows recent reports
- [ ] Stats command shows basic statistics
- [ ] Previous period comparison works

### Nice to Have
- [ ] Web API endpoints
- [ ] CSV/JSON export
- [ ] Batch processing

---

## 8. Known Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| HTML structure changes | Modular parser, easy to update |
| Dynamic table rows | Flexible row parsing |
| Missing previous data | Graceful fallback, no comparison |
| Performance with large files | Stream parsing, lazy evaluation |

---

## 9. Next Steps

1. **Immediately:** Create backend directory structure
2. **Day 2 end:** requirements.txt and models.py ready
3. **Day 4 end:** Parser working with test HTML
4. **Day 6 end:** Validator fully implemented
5. **Day 7 end:** Database complete
6. **Day 9 end:** CLI + API complete
7. **Day 11 end:** All tests passing, ready for Week 2

---

*Son update: 2026-02-02*
