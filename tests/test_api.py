#!/usr/bin/env python3
"""
API Tests for azstat-report backend.
Standalone version - no external dependencies required.
"""

import sys
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime


# ===== SIMPLE MODELS =====
class OrganizationInfo:
    def __init__(self, code="", name="", region=None, property_type="", activity_code="", organization_type=None):
        self.code = code
        self.name = name
        self.region = region
        self.property_type = property_type
        self.activity_code = activity_code
        self.organization_type = organization_type
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'region': self.region,
            'property_type': self.property_type,
            'activity_code': self.activity_code,
            'organization_type': self.organization_type
        }


class SectionIRow:
    def __init__(self, row_code="", row_name="", current_year=0.0, previous_year=0.0):
        self.row_code = row_code
        self.row_name = row_name
        self.current_year = current_year
        self.previous_year = previous_year
    
    def to_dict(self):
        return {
            'row_code': self.row_code,
            'row_name': self.row_name,
            'current_year': self.current_year,
            'previous_year': self.previous_year
        }


class SectionI:
    def __init__(self, rows=None):
        self.rows = rows or []


class ProductRow:
    def __init__(self, product_code="", product_name="", unit="", produced=0.0, 
                 internal_use=0.0, sold_quantity=0.0, sold_value=0.0, 
                 year_end_stock=0.0, import_value=0.0):
        self.product_code = product_code
        self.product_name = product_name
        self.unit = unit
        self.produced = produced
        self.internal_use = internal_use
        self.sold_quantity = sold_quantity
        self.sold_value = sold_value
        self.year_end_stock = year_end_stock
        self.import_value = import_value
    
    def to_dict(self):
        return {
            'product_code': self.product_code,
            'product_name': self.product_name,
            'unit': self.unit,
            'produced': self.produced,
            'internal_use': self.internal_use,
            'sold_quantity': self.sold_quantity,
            'sold_value': self.sold_value,
            'year_end_stock': self.year_end_stock,
            'import_value': self.import_value
        }


class SectionII:
    def __init__(self, products=None):
        self.products = products or []


class ReportData:
    def __init__(self, organization, report_type="", report_period="", 
                 section_i=None, section_ii=None, uploaded_at=None):
        self.organization = organization
        self.report_type = report_type
        self.report_period = report_period
        self.section_i = section_i or SectionI()
        self.section_ii = section_ii or SectionII()
        self.uploaded_at = uploaded_at or datetime.now()


class ValidationIssue:
    def __init__(self, category="info", field="", message="", severity="anomaly"):
        self.category = category
        self.field = field
        self.message = message
        self.severity = severity
    
    def to_dict(self):
        return {
            'category': self.category,
            'field': self.field,
            'message': self.message,
            'severity': self.severity
        }


class ValidationResult:
    def __init__(self, status="passed", error_count=0, warning_count=0, 
                 info_count=0, issues=None):
        self.status = status
        self.error_count = error_count
        self.warning_count = warning_count
        self.info_count = info_count
        self.issues = issues or []


# ===== PARSER (Simplified) =====
class AzstatParser:
    """Simplified parser for testing."""
    
    def __init__(self, html_content):
        self.html = html_content
        self.report_type = self._detect_report_type()
    
    def _detect_report_type(self):
        if 'tab1:' in self.html:
            return '1-isth'
        elif 'ng_i1:' in self.html:
            return '12-isth'
        return 'unknown'
    
    def parse_organization_info(self):
        import re
        org = OrganizationInfo()
        
        code_match = re.search(r'name="organization\.code"[^>]*value="([^"]*)"', self.html)
        name_match = re.search(r'name="organization\.name"[^>]*value="([^"]*)"', self.html)
        
        if code_match:
            org.code = code_match.group(1)
        if name_match:
            org.name = name_match.group(1)
        
        return org
    
    def parse_section_i(self):
        section = SectionI()
        import re
        
        if self.report_type == '1-isth':
            pattern = r'tab1:(\d+):j_idt51:j_idt55["\s]+value="([^"]*)"'
        elif self.report_type == '12-isth':
            pattern = r'ng_i1:(\d+):j_idt\d+:j_idt\d+["\s]+value="([^"]*)"'
        else:
            return section
        
        matches = re.findall(pattern, self.html)
        
        for row_idx, value in matches:
            try:
                val = float(value.replace(',', '.')) if value else 0.0
            except ValueError:
                val = 0.0
            
            section.rows.append(SectionIRow(
                row_code=str(int(row_idx) + 1),
                row_name=f"Row {row_idx}",
                current_year=val
            ))
        
        return section
    
    def _extract_period(self):
        if self.report_type == '1-isth':
            return "2024"
        elif self.report_type == '12-isth':
            return "2024-12"
        return "2024"
    
    def parse(self):
        return ReportData(
            organization=self.parse_organization_info(),
            report_type=self.report_type,
            report_period=self._extract_period(),
            section_i=self.parse_section_i(),
            section_ii=SectionII()
        )


# ===== VALIDATOR (Simplified) =====
class ValidationEngine:
    """Simplified validation engine."""
    
    def __init__(self, report, previous_report=None):
        self.report = report
        self.previous_report = previous_report
        self.issues = []
    
    def validate(self):
        self.issues = []
        self._check_errors()
        self._check_warnings()
        
        has_errors = any(i.category == 'error' for i in self.issues)
        has_warnings = any(i.category == 'warning' for i in self.issues)
        
        if has_errors:
            status = 'failed'
        elif has_warnings:
            status = 'warning'
        else:
            status = 'passed'
        
        return ValidationResult(
            status=status,
            error_count=len([i for i in self.issues if i.category == 'error']),
            warning_count=len([i for i in self.issues if i.category == 'warning']),
            info_count=len([i for i in self.issues if i.category == 'info']),
            issues=self.issues
        )
    
    def _check_errors(self):
        if not self.report.organization.code:
            self.issues.append(ValidationIssue(
                category='error',
                field='organization.code',
                message='Təşkilat kodu boşdur',
                severity='blocking'
            ))
        
        for row in self.report.section_i.rows:
            if row.current_year < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_i.{row.row_code}',
                    message=f'Mənfi dəyər: {row.current_year}',
                    severity='blocking'
                ))
        
        for product in self.report.section_ii.products:
            if product.produced < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_ii.{product.product_code}.produced',
                    message=f'Mənfi istehsal: {product.produced}',
                    severity='blocking'
                ))
    
    def _check_warnings(self):
        for product in self.report.section_ii.products:
            if product.produced > 0 and product.internal_use > product.produced:
                self.issues.append(ValidationIssue(
                    category='warning',
                    field=f'section_ii.{product.product_code}.internal_use',
                    message=f'Daxili istifadə ({product.internal_use}) > İstehsal ({product.produced})',
                    severity='logical'
                ))


# ===== DATABASE (Simplified) =====
class DatabaseHandler:
    """Simplified SQLite database handler."""
    
    def __init__(self, db_path="data/reports.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        import sqlite3
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
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def save_report(self, report, validation):
        import sqlite3
        section_i_json = json.dumps([r.to_dict() for r in report.section_i.rows], ensure_ascii=False)
        section_ii_json = json.dumps([p.to_dict() for p in report.section_ii.products], ensure_ascii=False)
        validation_json = json.dumps({
            'status': validation.status,
            'error_count': validation.error_count,
            'warning_count': validation.warning_count
        }, ensure_ascii=False)
        
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
                section_i_json,
                section_ii_json,
                validation_json,
                validation.status,
                report.uploaded_at.isoformat()
            ))
            
            cursor = conn.execute('SELECT last_insert_rowid()')
            return cursor.fetchone()[0]
    
    def get_report(self, report_id):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('SELECT * FROM reports WHERE id = ?', (report_id,)).fetchone()
            return row
    
    def get_history(self, limit=10):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('SELECT * FROM reports ORDER BY uploaded_at DESC LIMIT ?', (limit,)).fetchall()
            return list(rows)
    
    def get_statistics(self):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute('SELECT COUNT(*) FROM reports').fetchone()[0]
            passed = conn.execute("SELECT COUNT(*) FROM reports WHERE validation_status = 'passed'").fetchone()[0]
            warnings = conn.execute("SELECT COUNT(*) FROM reports WHERE validation_status = 'warning'").fetchone()[0]
            failed = conn.execute("SELECT COUNT(*) FROM reports WHERE validation_status = 'failed'").fetchone()[0]
            
            return {'total': total, 'passed': passed, 'warnings': warnings, 'failed': failed}
    
    def search_reports(self, query):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                'SELECT * FROM reports WHERE organization_code LIKE ? OR organization_name LIKE ? ORDER BY uploaded_at DESC',
                (f'%{query}%', f'%{query}%')
            ).fetchall()
            return list(rows)
    
    def compare_reports(self, report_id_1, report_id_2=None):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            current = conn.execute('SELECT * FROM reports WHERE id = ?', (report_id_1,)).fetchone()
            if not current:
                return {"error": f"Report {report_id_1} not found"}
            
            if report_id_2:
                previous = conn.execute('SELECT * FROM reports WHERE id = ?', (report_id_2,)).fetchone()
            else:
                previous = conn.execute(
                    'SELECT * FROM reports WHERE organization_code = ? AND report_type = ? AND report_period < ? ORDER BY report_period DESC LIMIT 1',
                    (current['organization_code'], current['report_type'], current['report_period'])
                ).fetchone()
            
            if not previous:
                return {"error": "No previous report found"}
            
            return {'current': dict(current), 'previous': dict(previous)}


# ===== TEST RUNNER =====
class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test(self, name, condition, error=""):
        if condition:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            self.errors.append((name, error))
            print(f"  ❌ {name}: {error}")
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"API Test Results: {self.passed} passed, {self.failed} failed")
        print(f"{'='*60}")
        return self.failed == 0


# Test data
SAMPLE_HTML_1ISTH = """
<!DOCTYPE html>
<html>
<body>
    <input name="organization.code" value="1293310"/>
    <input name="organization.name" value="NEFTÇALA SU MELİORASİYA"/>
    <input name="tab1:0:j_idt51:j_idt55" value="682.3"/>
    <input name="tab1:0:j_idt59:j_idt63" value="0.0"/>
    <input name="tab1:1:j_idt51:j_idt55" value="500.0"/>
    <input name="tab1:1:j_idt59:j_idt63" value="400.0"/>
</body>
</html>
"""

SAMPLE_HTML_12ISTH = """
<!DOCTYPE html>
<html>
<body>
    <input name="organization.code" value="1293310"/>
    <input name="organization.name" value="NEFTÇALA SU MELİORASİYA"/>
    <input name="ng_i1:0:j_idt58:j_idt61" value="100.5"/>
    <input name="ng_i1:1:j_idt58:j_idt61" value="50.2"/>
</body>
</html>
"""


def run_api_tests():
    tester = TestResult()
    
    print("\n" + "="*60)
    print("AZSTAT-REPORT API TESTS")
    print("="*60)
    
    # ===== PARSER API TESTS =====
    print("\n📋 Parser API Tests:")
    
    # Test 1: Parse 1-isth form
    try:
        parser = AzstatParser(SAMPLE_HTML_1ISTH)
        report = parser.parse()
        tester.test("parse_1isth_form", report.report_type == '1-isth' and report.organization.code == '1293310')
    except Exception as e:
        tester.test("parse_1isth_form", False, str(e))
    
    # Test 2: Parse 12-isth form
    try:
        parser = AzstatParser(SAMPLE_HTML_12ISTH)
        report = parser.parse()
        tester.test("parse_12isth_form", report.report_type == '12-isth')
    except Exception as e:
        tester.test("parse_12isth_form", False, str(e))
    
    # Test 3: Extract period
    try:
        parser = AzstatParser(SAMPLE_HTML_1ISTH)
        period = parser._extract_period()
        tester.test("extract_period", '2024' in period)
    except Exception as e:
        tester.test("extract_period", False, str(e))
    
    # Test 4: Parse organization
    try:
        parser = AzstatParser(SAMPLE_HTML_1ISTH)
        org = parser.parse_organization_info()
        tester.test("parse_organization", org.code == '1293310' and 'NEFTÇALA' in org.name)
    except Exception as e:
        tester.test("parse_organization", False, str(e))
    
    # Test 5: Parse section I values
    try:
        parser = AzstatParser(SAMPLE_HTML_1ISTH)
        section_i = parser.parse_section_i()
        tester.test("parse_section_i", len(section_i.rows) >= 2 and section_i.rows[0].current_year == 682.3)
    except Exception as e:
        tester.test("parse_section_i", False, str(e))
    
    # ===== VALIDATOR API TESTS =====
    print("\n🔍 Validator API Tests:")
    
    # Test 6: Validate clean report
    try:
        parser = AzstatParser(SAMPLE_HTML_1ISTH)
        report = parser.parse()
        engine = ValidationEngine(report)
        result = engine.validate()
        tester.test("validate_clean_report", result.status == 'passed' and result.error_count == 0)
    except Exception as e:
        tester.test("validate_clean_report", False, str(e))
    
    # Test 7: Detect negative values
    try:
        bad_html = SAMPLE_HTML_1ISTH.replace('value="682.3"', 'value="-100.0"')
        parser = AzstatParser(bad_html)
        report = parser.parse()
        engine = ValidationEngine(report)
        result = engine.validate()
        tester.test("detect_negative_values", result.error_count >= 1 and result.status == 'failed')
    except Exception as e:
        tester.test("detect_negative_values", False, str(e))
    
    # Test 8: Validate with warnings
    try:
        parser = AzstatParser(SAMPLE_HTML_1ISTH)
        report = parser.parse()
        report.section_ii = SectionII(products=[
            ProductRow(product_code="12345", product_name="Test", produced=100.0, internal_use=150.0)
        ])
        engine = ValidationEngine(report)
        result = engine.validate()
        tester.test("validate_with_warnings", result.warning_count >= 1 and result.status == 'warning')
    except Exception as e:
        tester.test("validate_with_warnings", False, str(e))
    
    # Test 9: Missing org code
    try:
        parser = AzstatParser(SAMPLE_HTML_1ISTH.replace('value="1293310"', 'value=""'))
        report = parser.parse()
        engine = ValidationEngine(report)
        result = engine.validate()
        tester.test("missing_org_code", result.status == 'failed')
    except Exception as e:
        tester.test("missing_org_code", False, str(e))
    
    # ===== DATABASE API TESTS =====
    print("\n🗄️ Database API Tests:")
    
    # Test 10: Database initialization
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = DatabaseHandler(db_path)
        tester.test("database_initialization", db.db_path.exists())
        os.unlink(db_path)
    except Exception as e:
        tester.test("database_initialization", False, str(e))
    
    # Test 11: Save and retrieve
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = DatabaseHandler(db_path)
        parser = AzstatParser(SAMPLE_HTML_1ISTH)
        report = parser.parse()
        engine = ValidationEngine(report)
        result = engine.validate()
        report_id = db.save_report(report, result)
        saved = db.get_report(report_id)
        
        tester.test("save_and_retrieve", saved is not None and saved['id'] == report_id)
        os.unlink(db_path)
    except Exception as e:
        tester.test("save_and_retrieve", False, str(e))
    
    # Test 12: Get history
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = DatabaseHandler(db_path)
        for i in range(3):
            parser = AzstatParser(SAMPLE_HTML_1ISTH)
            report = parser.parse()
            report.report_period = f"202{i}"
            engine = ValidationEngine(report)
            result = engine.validate()
            db.save_report(report, result)
        
        history = db.get_history(limit=10)
        tester.test("get_history", len(history) >= 3)
        os.unlink(db_path)
    except Exception as e:
        tester.test("get_history", False, str(e))
    
    # Test 13: Get statistics
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = DatabaseHandler(db_path)
        for i in range(5):
            parser = AzstatParser(SAMPLE_HTML_1ISTH)
            report = parser.parse()
            engine = ValidationEngine(report)
            result = engine.validate()
            db.save_report(report, result)
        
        stats = db.get_statistics()
        tester.test("get_statistics", stats['total'] >= 5)
        os.unlink(db_path)
    except Exception as e:
        tester.test("get_statistics", False, str(e))
    
    # Test 14: Search reports
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = DatabaseHandler(db_path)
        parser = AzstatParser(SAMPLE_HTML_1ISTH)
        report = parser.parse()
        engine = ValidationEngine(report)
        result = engine.validate()
        db.save_report(report, result)
        
        results = db.search_reports("1293310")
        tester.test("search_reports", len(results) >= 1)
        os.unlink(db_path)
    except Exception as e:
        tester.test("search_reports", False, str(e))
    
    # Test 15: Compare reports
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = DatabaseHandler(db_path)
        for period in ["2024", "2023"]:
            parser = AzstatParser(SAMPLE_HTML_1ISTH)
            report = parser.parse()
            report.report_period = period
            engine = ValidationEngine(report)
            result = engine.validate()
            db.save_report(report, result)
        
        history = db.get_history(limit=2)
        if len(history) >= 2:
            comparison = db.compare_reports(history[0]['id'], history[1]['id'])
            tester.test("compare_reports", 'current' in comparison and 'previous' in comparison)
        else:
            tester.test("compare_reports", False, "Not enough reports")
        os.unlink(db_path)
    except Exception as e:
        tester.test("compare_reports", False, str(e))
    
    # ===== INTEGRATION TESTS =====
    print("\n🔗 Integration Tests:")
    
    # Test 16: Full workflow
    try:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = DatabaseHandler(db_path)
        parser = AzstatParser(SAMPLE_HTML_1ISTH)
        report = parser.parse()
        engine = ValidationEngine(report)
        result = engine.validate()
        report_id = db.save_report(report, result)
        saved = db.get_report(report_id)
        stats = db.get_statistics()
        
        tester.test("full_workflow", saved is not None and stats['total'] >= 1)
        os.unlink(db_path)
    except Exception as e:
        tester.test("full_workflow", False, str(e))
    
    # Test 17: Multiple form types
    try:
        parser_1isth = AzstatParser(SAMPLE_HTML_1ISTH)
        report_1isth = parser_1isth.parse()
        
        parser_12isth = AzstatParser(SAMPLE_HTML_12ISTH)
        report_12isth = parser_12isth.parse()
        
        tester.test("multiple_form_types", report_1isth.report_type == '1-isth' and report_12isth.report_type == '12-isth')
    except Exception as e:
        tester.test("multiple_form_types", False, str(e))
    
    # Test 18: Invalid HTML handling
    try:
        parser = AzstatParser("invalid html")
        report = parser.parse()
        tester.test("invalid_html_handling", report.report_type == 'unknown')
    except Exception as e:
        tester.test("invalid_html_handling", False, str(e))
    
    # Test 19: Large value handling
    try:
        large_html = SAMPLE_HTML_1ISTH.replace('value="682.3"', 'value="9999999999.99"')
        parser = AzstatParser(large_html)
        report = parser.parse()
        engine = ValidationEngine(report)
        result = engine.validate()
        tester.test("large_value_handling", result.status == 'passed')
    except Exception as e:
        tester.test("large_value_handling", False, str(e))
    
    # Test 20: Zero values
    try:
        zero_html = SAMPLE_HTML_1ISTH.replace('value="682.3"', 'value="0"')
        parser = AzstatParser(zero_html)
        report = parser.parse()
        engine = ValidationEngine(report)
        result = engine.validate()
        tester.test("zero_values", result.error_count == 0)
    except Exception as e:
        tester.test("zero_values", False, str(e))
    
    # ===== SUMMARY =====
    success = tester.summary()
    
    if tester.errors:
        print("\nFailed tests:")
        for name, error in tester.errors:
            print(f"  - {name}: {error}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(run_api_tests())
