# Pydantic models for azstat-report

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class OrganizationInfo(BaseModel):
    """Organization info from form header."""
    code: str = ""                      # VÖEN
    name: str = ""
    region: Optional[str] = None
    property_type: str = ""
    activity_code: str = ""
    organization_type: Optional[str] = None


class SectionIRow(BaseModel):
    """Section I row data."""
    row_code: str
    row_name: str
    current_year: float = 0.0
    previous_year: float = 0.0


class SectionI(BaseModel):
    """Section I data."""
    rows: List[SectionIRow] = []


class ProductRow(BaseModel):
    """Section II product row."""
    product_code: str = ""
    product_name: str = ""
    unit: str = ""
    produced: float = 0.0
    internal_use: float = 0.0
    sold_quantity: float = 0.0
    sold_value: float = 0.0
    year_end_stock: float = 0.0
    import_value: float = 0.0


class SectionII(BaseModel):
    """Section II products data."""
    products: List[ProductRow] = []


class ReportData(BaseModel):
    """Complete parsed report."""
    organization: OrganizationInfo
    report_type: str = ""              # '1-isth' or '12-isth'
    report_period: str = ""            # '2025' or '2025-12'
    section_i: SectionI
    section_ii: SectionII
    uploaded_at: datetime = datetime.now()


class ValidationIssue(BaseModel):
    """Single validation issue."""
    category: str = "info"             # 'error', 'warning', 'info'
    field: str = ""
    message: str = ""
    severity: str = "anomaly"          # 'blocking', 'logical', 'consistency', 'anomaly'


class ValidationResult(BaseModel):
    """Validation result summary."""
    status: str = "passed"             # 'passed', 'warning', 'failed'
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    issues: List[ValidationIssue] = []


class ReportRecord(BaseModel):
    """Full report record for database."""
    id: Optional[int] = None
    organization_code: str = ""
    organization_name: str = ""
    report_type: str = ""
    report_period: str = ""
    section_i_data: str = ""           # JSON string
    section_ii_data: str = ""          # JSON string
    validation_results: str = ""       # JSON string
    validation_status: str = ""
    uploaded_at: datetime = None
