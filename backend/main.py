# CLI Entry Point and Web API for azstat-report

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

import click
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import Config
from parser import AzstatParser
from validator import ValidationEngine
from database import DatabaseHandler
from models import ReportData, ValidationResult


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
@click.option('--output', '-o', type=click.Choice(['text', 'json']), default='text', help='Output format')
def validate(file_path: str, compare: bool, output: str):
    """Validate an HTML report file."""
    click.echo(f"Validating: {file_path}")
    
    # Parse HTML
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    parser = AzstatParser(html_content)
    report = parser.parse()
    
    click.echo(f"Report type: {report.report_type}")
    click.echo(f"Period: {report.report_period}")
    click.echo(f"Organization: {report.organization.name} ({report.organization.code})")
    
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
            # Convert record to ReportData
            try:
                prev_section_i = json.loads(prev_record.section_i_data) if prev_record.section_i_data else []
                prev_section_ii = json.loads(prev_record.section_ii_data) if prev_record.section_ii_data else []
                
                from models import SectionI, SectionII, SectionIRow, ProductRow
                
                previous_report = ReportData(
                    organization=report.organization,  # Use current org info
                    report_type=prev_record.report_type,
                    report_period=prev_record.report_period,
                    section_i=SectionI(rows=[SectionIRow(**row) for row in prev_section_i]),
                    section_ii=SectionII(products=[ProductRow(**prod) for prod in prev_section_ii]),
                )
                click.echo(f"Previous report found: {prev_record.report_period}")
            except Exception as e:
                click.echo(f"Warning: Could not load previous report: {e}")
    
    # Validate
    engine = ValidationEngine(report, previous_report)
    result = engine.validate()
    
    # Prepare output
    if output == 'json':
        output_data = {
            'report_type': report.report_type,
            'period': report.report_period,
            'organization': report.organization.name,
            'status': result.status,
            'summary': {
                'errors': result.error_count,
                'warnings': result.warning_count,
                'infos': result.info_count
            },
            'issues': [issue.model_dump() for issue in result.issues]
        }
        click.echo(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        click.echo(f"\nValidation Status: {result.status.upper()}")
        click.echo(f"Errors: {result.error_count}")
        click.echo(f"Warnings: {result.warning_count}")
        click.echo(f"Infos: {result.info_count}")
        
        if result.issues:
            click.echo("\nIssues:")
            for issue in result.issues:
                icon = "🔴" if issue.category == 'error' else "🟡" if issue.category == 'warning' else "🔵"
                click.echo(f"  {icon} [{issue.category.upper()}] {issue.field}: {issue.message}")
    
    # Save to database
    db = DatabaseHandler()
    report_id = db.save_report(report, result)
    click.echo(f"\nSaved to database (ID: {report_id})")


@cli.command()
@click.option('--org', 'organization_code', help='Filter by organization code')
@click.option('--type', 'report_type', help='Filter by report type (1-isth or 12-isth)')
@click.option('--limit', default=20, help='Number of reports to show')
@click.option('--status', help='Filter by validation status')
def history(organization_code: str, report_type: str, limit: int, status: str):
    """Show report history."""
    db = DatabaseHandler()
    reports = db.get_history(
        org_code=organization_code,
        report_type=report_type,
        limit=limit,
        status=status
    )
    
    if not reports:
        click.echo("No reports found.")
        return
    
    click.echo("\nReport History:")
    click.echo("-" * 120)
    click.echo(f"{'ID':>4} | {'Type':<8} | {'Period':<8} | {'Organization':<25} | {'Status':<8} | {'Uploaded':<19}")
    click.echo("-" * 120)
    
    for r in reports:
        org_name = (r.organization_name[:22] + '...') if len(r.organization_name) > 25 else r.organization_name
        click.echo(
            f"{r.id:>4} | {r.report_type:<8} | {r.report_period:<8} | {org_name:<25} | {r.validation_status:<8} | {r.uploaded_at.strftime('%Y-%m-%d %H:%M:%S') if r.uploaded_at else 'N/A'}"
        )


@cli.command()
@click.option('--org', 'organization_code', help='Organization code for specific stats')
def stats(organization_code: str):
    """Show statistics."""
    db = DatabaseHandler()
    
    if organization_code:
        stats = db.get_org_statistics(organization_code)
        click.echo(f"\nStatistics for organization {organization_code}:")
        click.echo(f"  Total reports: {stats['total_reports']}")
        click.echo(f"  Passed: {stats['passed']}")
        click.echo(f"  Warnings: {stats['warnings']}")
        click.echo(f"  Failed: {stats['failed']}")
        
        if stats.get('last_report'):
            last = stats['last_report']
            click.echo(f"\nLast report:")
            click.echo(f"  Type: {last.report_type}")
            click.echo(f"  Period: {last.report_period}")
            click.echo(f"  Status: {last.validation_status}")
    else:
        stats = db.get_statistics()
        click.echo("\nOverall Statistics:")
        click.echo(f"Total reports: {stats['total']}")
        click.echo(f"Passed: {stats['passed']}")
        click.echo(f"Warnings: {stats['warnings']}")
        click.echo(f"Failed: {stats['failed']}")
        
        if stats['total'] > 0:
            click.echo(f"\nPass rate: {stats['passed'] / stats['total'] * 100:.1f}%")


@cli.command()
@click.argument('report_id', type=int)
@click.option('--format', 'output_format', type=click.Choice(['text', 'json']), default='text')
def show(report_id: int, output_format: str):
    """Show report details."""
    db = DatabaseHandler()
    report = db.get_report(report_id)
    
    if not report:
        click.echo(f"Report {report_id} not found.")
        return
    
    if output_format == 'json':
        output = {
            'id': report.id,
            'organization_code': report.organization_code,
            'organization_name': report.organization_name,
            'report_type': report.report_type,
            'report_period': report.report_period,
            'validation_status': report.validation_status,
            'uploaded_at': report.uploaded_at.isoformat() if report.uploaded_at else None
        }
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        click.echo(f"\nReport #{report.id}")
        click.echo(f"Organization: {report.organization_name} ({report.organization_code})")
        click.echo(f"Type: {report.report_type}")
        click.echo(f"Period: {report.report_period}")
        click.echo(f"Status: {report.validation_status}")
        click.echo(f"Uploaded: {report.uploaded_at}")


@cli.command()
@click.argument('current_id', type=int)
@click.argument('previous_id', type=int, required=False)
def compare(current_id: int, previous_id: int = None):
    """Compare two reports."""
    db = DatabaseHandler()
    result = db.compare_reports(current_id, previous_id)
    
    if 'error' in result:
        click.echo(f"Error: {result['error']}")
        return
    
    current = result['current']
    previous = result['previous']
    comparison = result['comparison']
    
    click.echo(f"\nComparing Report #{current.id} vs #{previous.id}")
    click.echo(f"Current: {current.report_period} | Previous: {previous.report_period}")
    click.echo("-" * 60)
    
    if comparison['section_i_changes']:
        click.echo("\nSection I Changes:")
        for change in comparison['section_i_changes'][:10]:
            direction = "↑" if change['change'] > 0 else "↓" if change['change'] < 0 else "="
            click.echo(f"  {change['row_code']}: {direction} {abs(change['change']):.2f} ({change['change_pct']:.1f}%)")
    
    if comparison['products_added']:
        click.echo(f"\nProducts Added ({len(comparison['products_added'])}):")
        for name in comparison['products_added'][:5]:
            click.echo(f"  + {name}")
    
    if comparison['products_removed']:
        click.echo(f"\nProducts Removed ({len(comparison['products_removed'])}):")
        for name in comparison['products_removed'][:5]:
            click.echo(f"  - {name}")


@cli.command()
@click.argument('query')
@click.option('--limit', default=10)
def search(query: str, limit: int):
    """Search reports by organization name or code."""
    db = DatabaseHandler()
    reports = db.search_reports(query, limit=limit)
    
    if not reports:
        click.echo("No reports found.")
        return
    
    click.echo(f"\nSearch results for '{query}':")
    for r in reports:
        click.echo(f"  #{r.id} | {r.report_type} | {r.report_period} | {r.organization_name}")


# ========================
# Web API (FastAPI)
# ========================

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
    """API health check."""
    return {"status": "ok", "message": "azstat-report API working"}


@app.get("/api/health")
def health_check():
    """Detailed health check."""
    db = DatabaseHandler()
    stats = db.get_statistics()
    
    return {
        "status": "healthy",
        "api_version": "1.0.0",
        "database": "connected",
        "total_reports": stats['total']
    }


@app.post("/api/upload")
async def upload_report(
    file: UploadFile = File(...),
    compare: bool = Query(False, description="Compare with previous period")
):
    """
    HTML fayl yükləmək və validasiya etmək.
    
    - file: HTML fayl
    - compare: Əvvəlki dövr ilə müqayisə
    """
    # Fayl tipi yoxlaması
    if not file.filename.endswith(('.html', '.htm')):
        raise HTTPException(status_code=400, detail="Only HTML files allowed")
    
    # Fayl oxumaq
    content = await file.read()
    html_content = content.decode('utf-8')
    
    # Parse
    parser = AzstatParser(html_content)
    report = parser.parse()
    
    # Əvvəlki hesabatı tap (müqayisə üçün)
    previous_report = None
    if compare:
        db = DatabaseHandler()
        prev_record = db.get_latest_report(
            report.organization.code,
            report.report_type,
            report.report_period
        )
        if prev_record:
            # Convert record to ReportData
            try:
                prev_section_i = json.loads(prev_record.section_i_data) if prev_record.section_i_data else []
                prev_section_ii = json.loads(prev_record.section_ii_data) if prev_record.section_ii_data else []
                
                from models import SectionI, SectionII, SectionIRow, ProductRow
                
                previous_report = ReportData(
                    organization=report.organization,
                    report_type=prev_record.report_type,
                    report_period=prev_record.report_period,
                    section_i=SectionI(rows=[SectionIRow(**row) for row in prev_section_i]),
                    section_ii=SectionII(products=[ProductRow(**prod) for prod in prev_section_ii]),
                )
            except Exception:
                pass  # Skip comparison if parse fails
    
    # Validate
    engine = ValidationEngine(report, previous_report)
    result = engine.validate()
    
    # Save
    db = DatabaseHandler()
    report_id = db.save_report(report, result)
    
    return {
        "report_id": report_id,
        "status": result.status,
        "organization": {
            "code": report.organization.code,
            "name": report.organization.name
        },
        "report_type": report.report_type,
        "report_period": report.report_period,
        "summary": {
            "errors": result.error_count,
            "warnings": result.warning_count,
            "infos": result.info_count
        },
        "issues": [issue.model_dump() for issue in result.issues]
    }


@app.get("/api/reports/{report_id}")
def get_report(report_id: int):
    """Hesabat detallarını götürmək."""
    db = DatabaseHandler()
    report = db.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "id": report.id,
        "organization_code": report.organization_code,
        "organization_name": report.organization_name,
        "report_type": report.report_type,
        "report_period": report.report_period,
        "validation_status": report.validation_status,
        "uploaded_at": report.uploaded_at.isoformat() if report.uploaded_at else None,
        "section_i_data": json.loads(report.section_i_data) if report.section_i_data else [],
        "section_ii_data": json.loads(report.section_ii_data) if report.section_ii_data else [],
        "validation_results": json.loads(report.validation_results) if report.validation_results else {}
    }


@app.get("/api/reports")
def list_reports(
    limit: int = Query(10, ge=1, le=100),
    organization_code: str = None,
    report_type: str = None,
    status: str = None
):
    """Hesabat siyahısı."""
    db = DatabaseHandler()
    reports = db.get_history(
        org_code=organization_code,
        report_type=report_type,
        limit=limit,
        status=status
    )
    
    return {
        "reports": [
            {
                "id": r.id,
                "organization_code": r.organization_code,
                "organization_name": r.organization_name,
                "report_type": r.report_type,
                "report_period": r.report_period,
                "validation_status": r.validation_status,
                "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None
            }
            for r in reports
        ]
    }


@app.get("/api/reports/compare")
def compare_reports(
    current_id: int = Query(..., description="Current report ID"),
    previous_id: int = Query(None, description="Previous report ID (optional)")
):
    """İki hesabatı müqayisə etmək."""
    db = DatabaseHandler()
    result = db.compare_reports(current_id, previous_id)
    
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    
    return result


@app.get("/api/stats")
def get_statistics(organization_code: str = None):
    """Ümumi statistika."""
    db = DatabaseHandler()
    
    if organization_code:
        stats = db.get_org_statistics(organization_code)
        return stats
    else:
        return db.get_statistics()


@app.get("/api/search")
def search_reports(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100)
):
    """Axtarış."""
    db = DatabaseHandler()
    reports = db.search_reports(q, limit=limit)
    
    return {
        "results": [
            {
                "id": r.id,
                "organization_code": r.organization_code,
                "organization_name": r.organization_name,
                "report_type": r.report_type,
                "report_period": r.report_period,
                "validation_status": r.validation_status
            }
            for r in reports
        ]
    }


# ========================
# Main Entry Point
# ========================

if __name__ == '__main__':
    import uvicorn
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "serve":
            # Web server mode
            uvicorn.run(app, host="0.0.0.0", port=8000)
        elif sys.argv[1] == "init-db":
            # Initialize database
            db = DatabaseHandler()
            click.echo("Database initialized successfully.")
        else:
            # Pass to CLI
            cli()
    else:
        # Default to CLI
        cli()
