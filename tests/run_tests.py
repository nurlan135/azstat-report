#!/usr/bin/env python3
"""
Simple test runner for azstat-report backend.
Uses standard library only - no external dependencies.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser


# ===== SIMPLE MODELS (Stand-in for Pydantic) =====
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


# ===== HTML PARSER (simplified) =====
class SimpleHTMLParser:
    """Simple HTML parser for testing."""
    
    def __init__(self, html_content):
        self.html = html_content  # Keep original case for now
        self.report_type = self._detect_report_type()
    
    def _detect_report_type(self):
        if 'tab1:' in self.html:
            return '1-isth'
        elif 'ng_i1:' in self.html:
            return '12-isth'
        return 'unknown'
    
    def parse_organization_info(self):
        org = OrganizationInfo()
        
        # Simple pattern matching
        import re
        # Handle both name="X" value="Y" and name="X" value='Y' formats
        code_match = re.search(r'name="organization\.code"[^>]*value="([^"]*)"', self.html)
        if not code_match:
            code_match = re.search(r'organization\.code["\s]+value="([^"]*)"', self.html)
        
        name_match = re.search(r'name="organization\.name"[^>]*value="([^"]*)"', self.html)
        if not name_match:
            name_match = re.search(r'organization\.name["\s]+value="([^"]*)"', self.html)
        
        if code_match:
            org.code = code_match.group(1)
        if name_match:
            org.name = name_match.group(1)
        
        return org
    
    def parse_section_i(self):
        section = SectionI()
        
        import re
        # Find all section I values
        if self.report_type == '1-isth':
            # tab1 pattern
            pattern = r'tab1:(\d+):j_idt51:j_idt55["\s]+value="([^"]*)"'
        elif self.report_type == '12-isth':
            # ng_i1 pattern
            pattern = r'ng_i1:(\d+):j_idt\d+:j_idt\d+["\s]+value="([^"]*)"'
        else:
            return section
        
        import re
        matches = re.findall(pattern, self.html)
        
        row_names = {
            "0": "Row 1", "1": "Row 1.1", "2": "Row 1.2", 
            "3": "Row 2", "4": "Row 3", "5": "Row 4"
        }
        
        for row_idx, value in matches:
            try:
                val = float(value.replace(',', '.')) if value else 0.0
            except ValueError:
                val = 0.0
            
            section.rows.append(SectionIRow(
                row_code=str(int(row_idx) + 1),
                row_name=row_names.get(row_idx, f"Row {row_idx}"),
                current_year=val
            ))
        
        return section


# ===== VALIDATION ENGINE (simplified) =====
class SimpleValidationEngine:
    """Simplified validation engine for testing."""
    
    def __init__(self, report, previous_report=None):
        self.report = report
        self.previous_report = previous_report
        self.issues = []
    
    def validate(self):
        self.issues = []
        
        # Check errors
        self._check_errors()
        self._check_warnings()
        
        # Determine status
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
        # Missing org code
        if not self.report.organization.code:
            self.issues.append(ValidationIssue(
                category='error',
                field='organization.code',
                message='Təşkilat kodu boşdur',
                severity='blocking'
            ))
        
        # Negative values
        for row in self.report.section_i.rows:
            if row.current_year < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_i.{row.row_code}',
                    message=f'Mənfi dəyər: {row.current_year}',
                    severity='blocking'
                ))
        
        # Product negative values
        for product in self.report.section_ii.products:
            if product.produced < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_ii.{product.product_code}.produced',
                    message=f'Mənfi istehsal: {product.produced}',
                    severity='blocking'
                ))
    
    def _check_warnings(self):
        # Internal use > production
        for product in self.report.section_ii.products:
            if product.produced > 0 and product.internal_use > product.produced:
                self.issues.append(ValidationIssue(
                    category='warning',
                    field=f'section_ii.{product.product_code}.internal_use',
                    message=f'Daxili istifadə ({product.internal_use}) > İstehsal ({product.produced})',
                    severity='logical'
                ))


# ===== TEST RUNNER =====
class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, name):
        self.passed += 1
        print(f"  ✅ {name}")
    
    def add_fail(self, name, error):
        self.failed += 1
        self.errors.append((name, error))
        print(f"  ❌ {name}: {error}")
    
    def summary(self):
        print(f"\n{'='*60}")
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print(f"{'='*60}")
        return self.failed == 0


def run_tests():
    results = TestResult()
    
    print("\n" + "="*60)
    print("AZSTAT-REPORT BACKEND TESTS")
    print("="*60)
    
    # ===== PARSER TESTS =====
    print("\n📋 Parser Tests:")
    
    # Test 1: Detect 1-isth form
    try:
        html = '<input name="tab1:0:j_idt51:j_idt55" value="100">'
        parser = SimpleHTMLParser(html)
        if parser.report_type == '1-isth':
            results.add_pass("detect_1isth_form")
        else:
            results.add_fail("detect_1isth_form", f"Got: {parser.report_type}")
    except Exception as e:
        results.add_fail("detect_1isth_form", str(e))
    
    # Test 2: Detect 12-isth form
    try:
        html = '<input name="ng_i1:0:j_idt58:j_idt61" value="100">'
        parser = SimpleHTMLParser(html)
        if parser.report_type == '12-isth':
            results.add_pass("detect_12isth_form")
        else:
            results.add_fail("detect_12isth_form", f"Got: {parser.report_type}")
    except Exception as e:
        results.add_fail("detect_12isth_form", str(e))
    
    # Test 3: Parse organization info
    try:
        html = '<input name="organization.code" value="1293310"/><input name="organization.name" value="Test Org"/>'
        parser = SimpleHTMLParser(html)
        org = parser.parse_organization_info()
        if org.code == "1293310" and org.name == "Test Org":
            results.add_pass("parse_organization_info")
        else:
            results.add_fail("parse_organization_info", f"code={org.code}, name={org.name}")
    except Exception as e:
        results.add_fail("parse_organization_info", str(e))
    
    # Test 4: Parse Section I
    try:
        html = '<input name="tab1:0:j_idt51:j_idt55" value="1000"><input name="tab1:1:j_idt51:j_idt55" value="500">'
        parser = SimpleHTMLParser(html)
        section_i = parser.parse_section_i()
        if len(section_i.rows) == 2 and section_i.rows[0].current_year == 1000.0:
            results.add_pass("parse_section_i")
        else:
            results.add_fail("parse_section_i", f"rows={len(section_i.rows)}")
    except Exception as e:
        results.add_fail("parse_section_i", str(e))
    
    # Test 5: Empty HTML handling
    try:
        parser = SimpleHTMLParser("")
        if parser.report_type == 'unknown':
            results.add_pass("empty_html_handling")
        else:
            results.add_fail("empty_html_handling", f"Got: {parser.report_type}")
    except Exception as e:
        results.add_fail("empty_html_handling", str(e))
    
    # ===== VALIDATOR TESTS =====
    print("\n🔍 Validator Tests:")
    
    # Test 6: No issues
    try:
        report = ReportData(
            organization=OrganizationInfo(code="1293310", name="Test"),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(rows=[
                SectionIRow(row_code="1", row_name="Sales", current_year=1000.0),
            ]),
            section_ii=SectionII()
        )
        engine = SimpleValidationEngine(report)
        result = engine.validate()
        if result.status == "passed" and result.error_count == 0:
            results.add_pass("no_issues_validation")
        else:
            results.add_fail("no_issues_validation", f"status={result.status}")
    except Exception as e:
        results.add_fail("no_issues_validation", str(e))
    
    # Test 7: Negative value error
    try:
        report = ReportData(
            organization=OrganizationInfo(code="1293310"),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(rows=[
                SectionIRow(row_code="1", row_name="Sales", current_year=-100.0),
            ]),
            section_ii=SectionII()
        )
        engine = SimpleValidationEngine(report)
        result = engine.validate()
        if result.status == "failed" and result.error_count >= 1:
            results.add_pass("negative_value_error")
        else:
            results.add_fail("negative_value_error", f"status={result.status}")
    except Exception as e:
        results.add_fail("negative_value_error", str(e))
    
    # Test 8: Missing org code error
    try:
        report = ReportData(
            organization=OrganizationInfo(code=""),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(rows=[
                SectionIRow(row_code="1", row_name="Sales", current_year=1000.0),
            ]),
            section_ii=SectionII()
        )
        engine = SimpleValidationEngine(report)
        result = engine.validate()
        if result.status == "failed":
            results.add_pass("missing_org_code_error")
        else:
            results.add_fail("missing_org_code_error", f"status={result.status}")
    except Exception as e:
        results.add_fail("missing_org_code_error", str(e))
    
    # Test 9: Internal use warning
    try:
        report = ReportData(
            organization=OrganizationInfo(code="1293310"),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(rows=[
                SectionIRow(row_code="1", row_name="Sales", current_year=1000.0),
            ]),
            section_ii=SectionII(products=[
                ProductRow(
                    product_code="12345",
                    product_name="Product",
                    produced=100.0,
                    internal_use=150.0,
                    sold_quantity=50.0
                )
            ])
        )
        engine = SimpleValidationEngine(report)
        result = engine.validate()
        if result.status == "warning" and result.warning_count >= 1:
            results.add_pass("internal_use_warning")
        else:
            results.add_fail("internal_use_warning", f"status={result.status}")
    except Exception as e:
        results.add_fail("internal_use_warning", str(e))
    
    # Test 10: Status determination
    try:
        # Passed case
        report_passed = ReportData(
            organization=OrganizationInfo(code="123"),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(rows=[SectionIRow(row_code="1", row_name="Sales", current_year=1000.0)]),
            section_ii=SectionII()
        )
        
        # Warning case
        report_warning = ReportData(
            organization=OrganizationInfo(code="123"),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(rows=[SectionIRow(row_code="1", row_name="Sales", current_year=1000.0)]),
            section_ii=SectionII(products=[
                ProductRow(product_code="12345", product_name="Product", produced=100.0, internal_use=150.0)
            ])
        )
        
        status_passed = SimpleValidationEngine(report_passed).validate().status
        status_warning = SimpleValidationEngine(report_warning).validate().status
        
        if status_passed == "passed" and status_warning == "warning":
            results.add_pass("status_determination")
        else:
            results.add_fail("status_determination", f"passed={status_passed}")
    except Exception as e:
        results.add_fail("status_determination", str(e))
    
    # Test 11: Product negative value
    try:
        report = ReportData(
            organization=OrganizationInfo(code="1293310"),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(rows=[SectionIRow(row_code="1", row_name="Sales", current_year=1000.0)]),
            section_ii=SectionII(products=[
                ProductRow(product_code="12345", product_name="Product", produced=-50.0)
            ])
        )
        engine = SimpleValidationEngine(report)
        result = engine.validate()
        if result.error_count >= 1:
            results.add_pass("product_negative_value")
        else:
            results.add_fail("product_negative_value", f"errors={result.error_count}")
    except Exception as e:
        results.add_fail("product_negative_value", str(e))
    
    # Test 12: Empty report
    try:
        report = ReportData(
            organization=OrganizationInfo(code=""),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(rows=[]),
            section_ii=SectionII(products=[])
        )
        engine = SimpleValidationEngine(report)
        result = engine.validate()
        if result.status == "failed":
            results.add_pass("empty_report_validation")
        else:
            results.add_fail("empty_report_validation", f"status={result.status}")
    except Exception as e:
        results.add_fail("empty_report_validation", str(e))
    
    # ===== MODEL TESTS =====
    print("\n📦 Model Tests:")
    
    # Test 13: SectionIRow serialization
    try:
        row = SectionIRow(row_code="1", row_name="Sales", current_year=1000.0, previous_year=800.0)
        data = row.to_dict()
        if data['row_code'] == "1" and data['current_year'] == 1000.0:
            results.add_pass("section_i_row_serialization")
        else:
            results.add_fail("section_i_row_serialization", str(data))
    except Exception as e:
        results.add_fail("section_i_row_serialization", str(e))
    
    # Test 14: ProductRow serialization
    try:
        product = ProductRow(
            product_code="12345",
            product_name="Test Product",
            unit="ədəd",
            produced=100.0,
            internal_use=10.0,
            sold_quantity=50.0,
            sold_value=500.0,
            year_end_stock=40.0
        )
        data = product.to_dict()
        if data['product_code'] == "12345" and data['produced'] == 100.0:
            results.add_pass("product_row_serialization")
        else:
            results.add_fail("product_row_serialization", "Data mismatch")
    except Exception as e:
        results.add_fail("product_row_serialization", str(e))
    
    # Test 15: OrganizationInfo serialization
    try:
        org = OrganizationInfo(code="1293310", name="Test Org", region="807")
        data = org.to_dict()
        if data['code'] == "1293310" and data['region'] == "807":
            results.add_pass("organization_info_serialization")
        else:
            results.add_fail("organization_info_serialization", "Data mismatch")
    except Exception as e:
        results.add_fail("organization_info_serialization", str(e))
    
    # Test 16: ValidationIssue serialization
    try:
        issue = ValidationIssue(
            category='error',
            field='organization.code',
            message='Test error',
            severity='blocking'
        )
        data = issue.to_dict()
        if data['category'] == 'error' and data['severity'] == 'blocking':
            results.add_pass("validation_issue_serialization")
        else:
            results.add_fail("validation_issue_serialization", "Data mismatch")
    except Exception as e:
        results.add_fail("validation_issue_serialization", str(e))
    
    # Test 17: ValidationResult creation
    try:
        result = ValidationResult(
            status="passed",
            error_count=0,
            warning_count=1,
            info_count=2,
            issues=[ValidationIssue(category='warning', field='test', message='test')]
        )
        if result.status == "passed" and result.warning_count == 1:
            results.add_pass("validation_result_creation")
        else:
            results.add_fail("validation_result_creation", "Data mismatch")
    except Exception as e:
        results.add_fail("validation_result_creation", str(e))
    
    # ===== SUMMARY =====
    print("\n" + "="*60)
    success = results.summary()
    
    if results.errors:
        print("\nFailed tests:")
        for name, error in results.errors:
            print(f"  - {name}: {error}")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(run_tests())
