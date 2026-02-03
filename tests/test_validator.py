# Unit tests for validator

import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models import (
    OrganizationInfo, SectionIRow, SectionI, 
    ProductRow, SectionII, ReportData, ValidationIssue
)
from backend.validator import ValidationEngine


class TestValidationEngine:
    """Tests for ValidationEngine."""
    
    def create_test_report(
        self, 
        org_code="1293310",
        rows_data=None,
        products_data=None
    ) -> ReportData:
        """Create a test report."""
        if rows_data is None:
            rows_data = [
                ("1", "Malların satışı", 1000.0, 800.0),
                ("1.1", "...müəsisənin öz istehsalı", 800.0, 600.0),
                ("2", "Hazır məhsul", 100.0, 80.0),
            ]
        
        if products_data is None:
            products_data = []
        
        return ReportData(
            organization=OrganizationInfo(
                code=org_code,
                name="Test Organization",
                region="807"
            ),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(
                rows=[
                    SectionIRow(
                        row_code=code,
                        row_name=name,
                        current_year=current,
                        previous_year=prev
                    )
                    for code, name, current, prev in rows_data
                ]
            ),
            section_ii=SectionII(
                products=[
                    ProductRow(**prod) for prod in products_data
                ]
            )
        )
    
    def test_no_issues(self):
        """Test validation with no issues."""
        report = self.create_test_report()
        engine = ValidationEngine(report)
        result = engine.validate()
        
        assert result.status == "passed"
        assert result.error_count == 0
        assert result.warning_count == 0
    
    def test_negative_value_error(self):
        """Test detection of negative values."""
        rows_data = [
            ("1", "Malların satışı", -100.0, 800.0),
        ]
        report = self.create_test_report(rows_data=rows_data)
        engine = ValidationEngine(report)
        result = engine.validate()
        
        assert result.status == "failed"
        assert result.error_count >= 1
        
        # Check that negative value was caught
        has_negative_error = any(
            'Negative' in issue.message or 'Mənfi' in issue.message
            for issue in result.issues
        )
        assert has_negative_error
    
    def test_missing_org_code_error(self):
        """Test detection of missing organization code."""
        report = self.create_test_report(org_code="")
        engine = ValidationEngine(report)
        result = engine.validate()
        
        assert result.status == "failed"
        has_org_error = any(
            'code' in issue.field and 'missing' in issue.message.lower() or 'boş' in issue.message.lower()
            for issue in result.issues
        )
        assert has_org_error
    
    def test_internal_use_warning(self):
        """Test internal use exceeds production warning."""
        products_data = [
            {
                "product_code": "12345",
                "product_name": "Test Product",
                "unit": "ədəd",
                "produced": 100.0,
                "internal_use": 150.0,  # Greater than production
                "sold_quantity": 50.0,
                "sold_value": 500.0,
                "year_end_stock": 20.0,
                "import_value": 0.0
            }
        ]
        report = self.create_test_report(products_data=products_data)
        engine = ValidationEngine(report)
        result = engine.validate()
        
        assert result.status == "warning"
        has_internal_use_warning = any(
            'internal_use' in issue.field or 'daxili istifadə' in issue.message.lower()
            for issue in result.issues
        )
        assert has_internal_use_warning
    
    def test_revenue_consistency_warning(self):
        """Test revenue less than own production warning."""
        rows_data = [
            ("1", "Malların satışı", 500.0, 800.0),  # Less than row 1.1
            ("1.1", "...müəsisənin öz istehsalı", 800.0, 600.0),
        ]
        report = self.create_test_report(rows_data=rows_data)
        engine = ValidationEngine(report)
        result = engine.validate()
        
        has_revenue_warning = any(
            '1' in issue.field and 'satış' in issue.message.lower()
            for issue in result.issues
        )
        assert has_revenue_warning
    
    def test_product_negative_values(self):
        """Test negative values in products."""
        products_data = [
            {
                "product_code": "12345",
                "product_name": "Test Product",
                "unit": "ədəd",
                "produced": -50.0,  # Negative
                "internal_use": 0.0,
                "sold_quantity": 100.0,
                "sold_value": 1000.0,
                "year_end_stock": 10.0,
                "import_value": 0.0
            }
        ]
        report = self.create_test_report(products_data=products_data)
        engine = ValidationEngine(report)
        result = engine.validate()
        
        assert result.error_count >= 1
    
    def test_anomaly_detection_with_previous(self):
        """Test anomaly detection with previous period."""
        # Current report with high change
        current_report = self.create_test_report(
            rows_data=[("1", "Malların satışı", 1500.0, 800.0)]  # 87.5% increase
        )
        
        # Previous report
        previous_report = self.create_test_report(
            rows_data=[("1", "Malların satışı", 1000.0, 800.0)]
        )
        
        engine = ValidationEngine(current_report, previous_report)
        result = engine.validate()
        
        # Should have an info anomaly about revenue change
        has_anomaly = any(
            issue.category == 'info' and 'change' in issue.message.lower()
            for issue in result.issues
        )
        assert has_anomaly
    
    def test_status_determination(self):
        """Test status determination logic."""
        # No issues -> passed
        report = self.create_test_report()
        engine = ValidationEngine(report)
        assert engine._determine_status() == "passed"
        
        # Only warnings -> warning
        # Add a warning by having internal_use > produced
        products_data = [
            {
                "product_code": "12345",
                "product_name": "Test Product",
                "unit": "ədəd",
                "produced": 100.0,
                "internal_use": 150.0,
                "sold_quantity": 0.0,
                "sold_value": 0.0,
                "year_end_stock": 0.0,
                "import_value": 0.0
            }
        ]
        report_with_warning = self.create_test_report(products_data=products_data)
        engine = ValidationEngine(report_with_warning)
        assert engine._determine_status() == "warning"
        
        # Errors present -> failed
        report_with_error = self.create_test_report(org_code="")
        engine = ValidationEngine(report_with_error)
        assert engine._determine_status() == "failed"
    
    def test_get_row_by_code(self):
        """Test _get_row_by_code helper."""
        rows_data = [
            ("1", "Row 1", 100.0, 80.0),
            ("1.1", "Row 1.1", 50.0, 40.0),
            ("2", "Row 2", 30.0, 25.0),
        ]
        report = self.create_test_report(rows_data=rows_data)
        engine = ValidationEngine(report)
        
        row_1 = engine._get_row_by_code("1")
        assert row_1 is not None
        assert row_1.row_code == "1"
        assert row_1.current_year == 100.0
        
        row_1_1 = engine._get_row_by_code("1.1")
        assert row_1_1 is not None
        assert row_1_1.current_year == 50.0
        
        row_nonexistent = engine._get_row_by_code("99")
        assert row_nonexistent is None
    
    def test_multiple_issues(self):
        """Test report with multiple issues."""
        products_data = [
            {
                "product_code": "12345",
                "product_name": "Product 1",
                "unit": "ədəd",
                "produced": 100.0,
                "internal_use": 150.0,  # Warning
                "sold_quantity": 50.0,
                "sold_value": 500.0,
                "year_end_stock": 20.0,
                "import_value": 0.0
            },
            {
                "product_code": "67890",
                "product_name": "Product 2",
                "unit": "ədəd",
                "produced": 200.0,
                "internal_use": 50.0,
                "sold_quantity": 0.0,
                "sold_value": 0.0,
                "year_end_stock": 0.0,
                "import_value": -10.0,  # Error
            }
        ]
        report = self.create_test_report(products_data=products_data)
        engine = ValidationEngine(report)
        result = engine.validate()
        
        assert result.error_count >= 1  # Negative import
        assert result.warning_count >= 1  # Internal use warning


class TestValidationEdgeCases:
    """Edge case tests for validation."""
    
    def create_report(self, **kwargs) -> ReportData:
        """Helper to create reports."""
        return ReportData(
            organization=kwargs.get('organization', OrganizationInfo(code="123")),
            report_type=kwargs.get('report_type', "1-isth"),
            report_period=kwargs.get('period', "2024"),
            section_i=kwargs.get('section_i', SectionI(rows=[])),
            section_ii=kwargs.get('section_ii', SectionII(products=[]))
        )
    
    def test_empty_report(self):
        """Test validation of empty report."""
        report = self.create_report()
        engine = ValidationEngine(report)
        result = engine.validate()
        
        # Should have error for missing org code
        assert result.status == "failed"
    
    def test_zero_values_no_issues(self):
        """Test that zero values don't trigger errors."""
        report = self.create_report(
            section_i=SectionI(rows=[
                SectionIRow(row_code="1", row_name="Row 1", current_year=0.0, previous_year=0.0)
            ])
        )
        engine = ValidationEngine(report)
        result = engine.validate()
        
        # Zero values should be valid
        assert result.error_count == 0
    
    def test_previous_period_comparison_no_previous(self):
        """Test comparison when no previous report exists."""
        report = ReportData(
            organization=OrganizationInfo(code="123"),
            report_type="1-isth",
            report_period="2024",
            section_i=SectionI(rows=[
                SectionIRow(row_code="1", row_name="Row 1", current_year=1500.0, previous_year=1000.0)
            ]),
            section_ii=SectionII(products=[])
        )
        
        # No previous report
        engine = ValidationEngine(report, previous_report=None)
        result = engine.validate()
        
        # Should not crash, should not have anomaly about comparison
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
