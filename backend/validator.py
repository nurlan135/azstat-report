# Validation Engine for azstat-report

from typing import List, Optional, Dict
from models import (
    ReportData, ValidationResult, ValidationIssue,
    SectionIRow, ProductRow
)
from config import Config


class ValidationEngine:
    """Report validation engine."""
    
    def __init__(self, report: ReportData, previous_report: ReportData = None):
        self.report = report
        self.previous_report = previous_report
        self.issues: List[ValidationIssue] = []
    
    def validate(self) -> ValidationResult:
        """Run all validation checks."""
        self.issues = []
        
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
        # 1. Negative values check
        for row in self.report.section_i.rows:
            if row.current_year < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_i.{row.row_code}.current_year',
                    message=f'Mənfi dəyər: {row.current_year}',
                    severity='blocking'
                ))
            if row.previous_year < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_i.{row.row_code}.previous_year',
                    message=f'Mənfi dəyər (əvvəlki il): {row.previous_year}',
                    severity='blocking'
                ))
        
        # 2. Check organization code
        if not self.report.organization.code:
            self.issues.append(ValidationIssue(
                category='error',
                field='organization.code',
                message='Təşkilat kodu boşdur',
                severity='blocking'
            ))
        
        # 3. Check report type
        if not self.report.report_type or self.report.report_type == 'unknown':
            self.issues.append(ValidationIssue(
                category='error',
                field='report_type',
                message='Hesabat növü təyin edilə bilmir',
                severity='blocking'
            ))
        
        # 4. Product table validation - negative values
        for product in self.report.section_ii.products:
            if product.produced < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_ii.{product.product_code}.produced',
                    message=f'Mənfi istehsal: {product.produced}',
                    severity='blocking'
                ))
            if product.internal_use < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_ii.{product.product_code}.internal_use',
                    message=f'Mənfi daxili istifadə: {product.internal_use}',
                    severity='blocking'
                ))
            if product.sold_quantity < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_ii.{product.product_code}.sold_quantity',
                    message=f'Mənfi satış miqdarı: {product.sold_quantity}',
                    severity='blocking'
                ))
            if product.sold_value < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_ii.{product.product_code}.sold_value',
                    message=f'Mənfi satış dəyəri: {product.sold_value}',
                    severity='blocking'
                ))
            if product.year_end_stock < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_ii.{product.product_code}.year_end_stock',
                    message=f'Mənfi anbar qalığı: {product.year_end_stock}',
                    severity='blocking'
                ))
            if product.import_value < 0:
                self.issues.append(ValidationIssue(
                    category='error',
                    field=f'section_ii.{product.product_code}.import_value',
                    message=f'Mənfi idxal dəyəri: {product.import_value}',
                    severity='blocking'
                ))
    
    def _check_logical_warnings(self):
        """WARNING: Logical consistency issues."""
        # 1. Revenue check: Row 1 should be >= Row 1.1
        row_1 = self._get_row_by_code("1")
        row_1_1 = self._get_row_by_code("1.1")
        
        if row_1 and row_1_1:
            if row_1.current_year < row_1_1.current_year:
                self.issues.append(ValidationIssue(
                    category='warning',
                    field='section_i.1',
                    message=f'Ümumi satış ({row_1.current_year}) < Öz istehsal satışı ({row_1_1.current_year})',
                    severity='logical'
                ))
        
        # 2. Internal use check: Internal Use should not exceed Production
        for product in self.report.section_ii.products:
            if product.produced > 0 and product.internal_use > product.produced:
                self.issues.append(ValidationIssue(
                    category='warning',
                    field=f'section_ii.{product.product_code}.internal_use',
                    message=f'Daxili istifadə ({product.internal_use}) > İstehsal ({product.produced})',
                    severity='logical'
                ))
        
        # 3. Inventory continuity check
        # Stock at end = Stock at beginning + Production - Sold
        # We don't have beginning stock in current form, so skip for now
        
        # 4. Sold + Stock should not exceed Production + Beginning Stock
        # Without beginning stock data, we can only check if Sold > Production + 10% buffer
        for product in self.report.section_ii.products:
            if product.produced > 0 and product.sold_quantity > product.produced * 1.1:
                self.issues.append(ValidationIssue(
                    category='warning',
                    field=f'section_ii.{product.product_code}.sold_quantity',
                    message=f'Satış miqdarı ({product.sold_quantity}) istehsalı ({product.produced}) 10%-dən çox üstələyir',
                    severity='logical'
                ))
    
    def _check_consistency_warnings(self):
        """WARNING: Column/field consistency issues."""
        # 1. Section I: Row relationships
        row_2 = self._get_row_by_code("2")
        row_2_1 = self._get_row_by_code("2.1")
        row_2_2 = self._get_row_by_code("2.2")
        
        if row_2_1 and row_2_2:
            # Row 2 should be approximately Row 2.2 - Row 2.1
            expected_2 = row_2_2.current_year - row_2_1.current_year
            if row_2 and abs(row_2.current_year - expected_2) > 1:
                self.issues.append(ValidationIssue(
                    category='warning',
                    field='section_i.2',
                    message=f'Satış üçün hazır məhsul qalığı ({row_2.current_year}) ilkin ({row_2_1.current_year}) və son ({row_2_2.current_year}) fərqi ilə uyğun deyil',
                    severity='consistency'
                ))
        
        # 2. Section II: Sold + Stock <= Production + Beginning Stock
        # We don't have beginning stock, so this is a soft check
        for product in self.report.section_ii.products:
            if product.sold_quantity > 0 and product.year_end_stock > 0:
                total_used = product.sold_quantity + product.year_end_stock
                # Allow some buffer for production during period
                if total_used > product.produced * 1.5 and product.produced > 0:
                    self.issues.append(ValidationIssue(
                        category='warning',
                        field=f'section_ii.{product.product_code}',
                        message=f'Satış ({product.sold_quantity}) + Anbar ({product.year_end_stock}) istehsalı ({product.produced}) çox üstələyir',
                        severity='consistency'
                    ))
        
        # 3. Export without import check (soft)
        if self.report.report_type == '1-isth':
            row_6 = self._get_row_by_code("6")  # Import
            row_8 = self._get_row_by_code("8")  # Export
            
            if row_6 and row_8:
                if row_8.current_year > 0 and row_6.current_year == 0:
                    # Export exists but no import - might be OK if using own materials
                    pass  # This is not necessarily an error
    
    def _check_anomalies(self):
        """INFO: Anomaly detection."""
        # 1. Revenue change > 50% compared to previous period
        if self.previous_report:
            current_revenue = self._get_row_by_code("1")
            previous_revenue = self._get_row_by_code("1")
            
            if current_revenue and previous_revenue:
                if previous_revenue.current_year > 0:
                    change = abs(current_revenue.current_year - previous_revenue.current_year) / previous_revenue.current_year
                    if change > Config.ANOMALY_THRESHOLD:
                        pct = change * 100
                        direction = "artım" if current_revenue.current_year > previous_revenue.current_year else "azalma"
                        self.issues.append(ValidationIssue(
                            category='info',
                            field='section_i.1',
                            message=f'Gəlir dəyişikliyi: {pct:.1f}% {direction} (əvvəlki dövr: {previous_revenue.current_year})',
                            severity='anomaly'
                        ))
        
        # 2. Zero values where there were values before
        if self.previous_report:
            for row in self.report.section_i.rows:
                prev_row = self._get_row_by_code_from_report(row.row_code, self.previous_report)
                if prev_row and prev_row.current_year > 1000 and row.current_year == 0:
                    self.issues.append(ValidationIssue(
                        category='info',
                        field=f'section_i.{row.row_code}',
                        message=f'Əvvəlki dövrdə dəyər var idi ({prev_row.current_year}), indi 0-dır',
                        severity='anomaly'
                    ))
        
        # 3. New products added
        if self.previous_report:
            current_codes = set(p.product_code for p in self.report.section_ii.products if p.product_code)
            prev_codes = set(p.product_code for p in self.previous_report.section_ii.products if p.product_code)
            new_codes = current_codes - prev_codes
            
            if new_codes:
                product_names = []
                for code in list(new_codes)[:3]:  # Show max 3
                    for p in self.report.section_ii.products:
                        if p.product_code == code:
                            product_names.append(p.product_name or code)
                            break
                
                self.issues.append(ValidationIssue(
                    category='info',
                    field='section_ii',
                    message=f'Yeni məhsullar əlavə olunub: {", ".join(product_names)}',
                    severity='anomaly'
                ))
        
        # 4. Products removed
        if self.previous_report:
            current_codes = set(p.product_code for p in self.report.section_ii.products if p.product_code)
            prev_codes = set(p.product_code for p in self.previous_report.section_ii.products if p.product_code)
            removed_codes = prev_codes - current_codes
            
            if removed_codes:
                product_names = []
                for code in list(removed_codes)[:3]:
                    for p in self.previous_report.section_ii.products:
                        if p.product_code == code:
                            product_names.append(p.product_name or code)
                            break
                
                self.issues.append(ValidationIssue(
                    category='info',
                    field='section_ii',
                    message=f'Məhsullar silinib: {", ".join(product_names)}',
                    severity='anomaly'
                ))
        
        # 5. Large single product dominance
        total_revenue = sum(p.sold_value for p in self.report.section_ii.products)
        if total_revenue > 0:
            for product in self.report.section_ii.products:
                if product.sold_value > total_revenue * 0.8:
                    self.issues.append(ValidationIssue(
                        category='info',
                        field=f'section_ii.{product.product_code}',
                        message=f'Məhsul ümumi satışın 80%-dən çoxunu təşkil edir ({product.sold_value / total_revenue * 100:.1f}%)',
                        severity='anomaly'
                    ))
                    break
    
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
    
    def _get_row_by_code(self, code: str) -> Optional[SectionIRow]:
        """Get Section I row by row code."""
        for row in self.report.section_i.rows:
            if row.row_code == code:
                return row
        return None
    
    def _get_row_by_code_from_report(self, code: str, report: ReportData) -> Optional[SectionIRow]:
        """Get Section I row by code from a specific report."""
        for row in report.section_i.rows:
            if row.row_code == code:
                return row
        return None
    
    def _get_previous_stock(self, product_code: str) -> float:
        """Get previous year end stock for product."""
        if self.previous_report:
            for product in self.previous_report.section_ii.products:
                if product.product_code == product_code:
                    return product.year_end_stock
        return 0.0
    
    def _get_total_revenue(self, report: ReportData = None) -> float:
        """Get total revenue from Section I."""
        target_report = report if report else self.report
        for row in target_report.section_i.rows:
            if row.row_code == "1":
                return row.current_year
        return 0.0
