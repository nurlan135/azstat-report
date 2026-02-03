# SQLite Database Handler

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from models import (
    ReportData, ReportRecord, ValidationResult
)


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
            
            # Indexes for faster queries
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_org_period 
                ON reports(organization_code, report_type, report_period)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_uploaded_at 
                ON reports(uploaded_at DESC)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_status 
                ON reports(validation_status)
            ''')
    
    def save_report(self, report: ReportData, validation: ValidationResult) -> int:
        """Save report to database."""
        section_i_json = json.dumps(
            [row.model_dump() for row in report.section_i.rows],
            ensure_ascii=False, default=str
        )
        section_ii_json = json.dumps(
            [prod.model_dump() for prod in report.section_ii.products],
            ensure_ascii=False, default=str
        )
        validation_json = json.dumps(
            validation.model_dump(),
            ensure_ascii=False, default=str
        )
        
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
                report.uploaded_at
            ))
            
            # Get the ID of inserted/updated row
            cursor = conn.execute('SELECT last_insert_rowid()')
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_report(self, report_id: int) -> Optional[ReportRecord]:
        """Get report by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                'SELECT * FROM reports WHERE id = ?', (report_id,)
            ).fetchone()
            
            if row:
                return self._row_to_record(row)
            return None
    
    def get_latest_report(
        self, 
        org_code: str, 
        report_type: str, 
        period: str
    ) -> Optional[ReportRecord]:
        """Get previous report for comparison (latest before given period)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute('''
                SELECT * FROM reports 
                WHERE organization_code = ? 
                  AND report_type = ?
                  AND report_period < ?
                ORDER BY report_period DESC
                LIMIT 1
            ''', (org_code, report_type, period)).fetchone()
            
            if row:
                return self._row_to_record(row)
            return None
    
    def get_history(
        self, 
        org_code: str = None, 
        report_type: str = None,
        limit: int = 10,
        status: str = None
    ) -> List[ReportRecord]:
        """Get report history with optional filters."""
        query = 'SELECT * FROM reports WHERE 1=1'
        params = []
        
        if org_code:
            query += ' AND organization_code = ?'
            params.append(org_code)
        
        if report_type:
            query += ' AND report_type = ?'
            params.append(report_type)
        
        if status:
            query += ' AND validation_status = ?'
            params.append(status)
        
        query += ' ORDER BY uploaded_at DESC LIMIT ?'
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_record(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, int]:
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
    
    def get_org_statistics(self, org_code: str) -> Dict[str, Any]:
        """Get statistics for specific organization."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute(
                'SELECT COUNT(*) FROM reports WHERE organization_code = ?',
                (org_code,)
            ).fetchone()[0]
            
            passed = conn.execute(
                "SELECT COUNT(*) FROM reports WHERE organization_code = ? AND validation_status = 'passed'",
                (org_code,)
            ).fetchone()[0]
            
            warnings = conn.execute(
                "SELECT COUNT(*) FROM reports WHERE organization_code = ? AND validation_status = 'warning'",
                (org_code,)
            ).fetchone()[0]
            
            failed = conn.execute(
                "SELECT COUNT(*) FROM reports WHERE organization_code = ? AND validation_status = 'failed'",
                (org_code,)
            ).fetchone()[0]
            
            last_report = conn.execute(
                'SELECT * FROM reports WHERE organization_code = ? ORDER BY uploaded_at DESC LIMIT 1',
                (org_code,)
            ).fetchone()
            
            return {
                'organization_code': org_code,
                'total_reports': total,
                'passed': passed,
                'warnings': warnings,
                'failed': failed,
                'last_report': self._row_to_record(last_report) if last_report else None
            }
    
    def delete_report(self, report_id: int) -> bool:
        """Delete a report by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('DELETE FROM reports WHERE id = ?', (report_id,))
            return cursor.rowcount > 0
    
    def compare_reports(
        self, 
        report_id_1: int, 
        report_id_2: int = None
    ) -> Dict[str, Any]:
        """Compare two reports."""
        report1 = self.get_report(report_id_1)
        if not report1:
            return {"error": f"Report {report_id_1} not found"}
        
        if report_id_2:
            report2 = self.get_report(report_id_2)
            if not report2:
                return {"error": f"Report {report_id_2} not found"}
        else:
            # Find previous report automatically
            report2 = self.get_latest_report(
                report1.organization_code,
                report1.report_type,
                report1.report_period
            )
            if not report2:
                return {"error": "No previous report found for comparison"}
        
        # Build comparison
        comparison = self._build_comparison(report1, report2)
        
        return {
            "current": report1,
            "previous": report2,
            "comparison": comparison
        }
    
    def _build_comparison(
        self, 
        current: ReportRecord, 
        previous: ReportRecord
    ) -> Dict[str, Any]:
        """Build comparison data between two reports."""
        # Parse JSON data
        current_i = json.loads(current.section_i_data) if current.section_i_data else []
        prev_i = json.loads(previous.section_i_data) if previous.section_i_data else []
        
        # Build Section I comparison
        section_i_changes = []
        current_dict = {row['row_code']: row for row in current_i}
        prev_dict = {row['row_code']: row for row in prev_i}
        
        for code in set(list(current_dict.keys()) + list(prev_dict.keys())):
            c = current_dict.get(code, {})
            p = prev_dict.get(code, {})
            
            curr_val = c.get('current_year', 0)
            prev_val = p.get('current_year', 0)
            
            if curr_val != prev_val:
                change = prev_val - curr_val
                pct = (abs(change) / prev_val * 100) if prev_val > 0 else 0
                section_i_changes.append({
                    'row_code': code,
                    'row_name': c.get('row_name', p.get('row_name', '')),
                    'current': curr_val,
                    'previous': prev_val,
                    'change': change,
                    'change_pct': round(pct, 2)
                })
        
        # Parse Section II
        current_ii = json.loads(current.section_ii_data) if current.section_ii_data else []
        prev_ii = json.loads(previous.section_ii_data) if previous.section_ii_data else []
        
        # Product comparison
        current_products = {p['product_code']: p for p in current_ii if p.get('product_code')}
        prev_products = {p['product_code']: p for p in prev_ii if p.get('product_code')}
        
        products_added = list(set(current_products.keys()) - set(prev_products.keys()))
        products_removed = list(set(prev_products.keys()) - set(current_products.keys()))
        products_changed = []
        
        for code in set(current_products.keys()) & set(prev_products.keys()):
            c = current_products[code]
            p = prev_products[code]
            
            if c.get('sold_value') != p.get('sold_value'):
                products_changed.append({
                    'product_code': code,
                    'product_name': c.get('product_name', p.get('product_name', '')),
                    'current_sold_value': c.get('sold_value', 0),
                    'previous_sold_value': p.get('sold_value', 0)
                })
        
        return {
            'section_i_changes': section_i_changes,
            'products_added': [current_products.get(code, {}).get('product_name', code) for code in products_added[:5]],
            'products_removed': [prev_products.get(code, {}).get('product_name', code) for code in products_removed[:5]],
            'products_changed_count': len(products_changed)
        }
    
    def _row_to_record(self, row: sqlite3.Row) -> ReportRecord:
        """Convert sqlite3.Row to ReportRecord."""
        return ReportRecord(
            id=row['id'],
            organization_code=row['organization_code'],
            organization_name=row['organization_name'],
            report_type=row['report_type'],
            report_period=row['report_period'],
            section_i_data=row['section_i_data'],
            section_ii_data=row['section_ii_data'],
            validation_results=row['validation_results'],
            validation_status=row['validation_status'],
            uploaded_at=datetime.fromisoformat(row['uploaded_at']) if row['uploaded_at'] else None
        )
    
    def search_reports(
        self, 
        query: str, 
        limit: int = 20
    ) -> List[ReportRecord]:
        """Search reports by organization name or code."""
        search_term = f"%{query}%"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute('''
                SELECT * FROM reports 
                WHERE organization_code LIKE ? OR organization_name LIKE ?
                ORDER BY uploaded_at DESC
                LIMIT ?
            ''', (search_term, search_term, limit)).fetchall()
            
            return [self._row_to_record(row) for row in rows]
