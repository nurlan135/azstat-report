# Unit tests for parser

import pytest
from pathlib import Path

# Add backend to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.parser import AzstatParser


class TestAzstatParser:
    """Tests for AzstatParser."""
    
    def test_detect_1isth_form(self):
        """Test detection of 1-isth form."""
        html = """
        <html>
        <body>
            <input name="tab1:0:j_idt51:j_idt55" value="100">
            <input name="tab1:1:j_idt51:j_idt55" value="50">
            <input name="tab1:0:j_idt59:j_idt63" value="80">
        </body>
        </html>
        """
        parser = AzstatParser(html)
        assert parser.report_type == '1-isth'
    
    def test_detect_12isth_form(self):
        """Test detection of 12-isth form."""
        html = """
        <html>
        <body>
            <input name="ng_i1:0:j_idt58:j_idt61" value="100">
            <input name="ng_i1:1:j_idt58:j_idt61" value="50">
        </body>
        </html>
        """
        parser = AzstatParser(html)
        assert parser.report_type == '12-isth'
    
    def test_parse_1isth_section_i(self):
        """Test parsing Section I for 1-isth form."""
        html = """
        <html>
        <body>
            <input name="tab1:0:j_idt51:j_idt55" value="100">
            <input name="tab1:0:j_idt59:j_idt63" value="80">
            <input name="tab1:1:j_idt51:j_idt55" value="50">
            <input name="tab1:1:j_idt59:j_idt63" value="40">
        </body>
        </html>
        """
        parser = AzstatParser(html)
        section_i = parser.parse_section_i()
        
        assert len(section_i.rows) >= 2
        # First row should have values
        row_0 = section_i.rows[0]
        assert row_0.current_year == 100.0
        assert row_0.previous_year == 80.0
    
    def test_parse_12isth_section_i(self):
        """Test parsing Section I for 12-isth form."""
        html = """
        <html>
        <body>
            <input name="ng_i1:0:j_idt122:j_idt123" value="150">
            <input name="ng_i1:1:j_idt122:j_idt123" value="75">
        </body>
        </html>
        """
        parser = AzstatParser(html)
        section_i = parser.parse_section_i()
        
        assert len(section_i.rows) >= 2
    
    def test_parse_organization_info(self):
        """Test parsing organization info."""
        html = """
        <html>
        <body>
            <input name="organization.code" value="1293310">
            <input name="organization.name" value="Test Organization">
            <input name="organization.region" value="807">
        </body>
        </html>
        """
        parser = AzstatParser(html)
        org = parser.parse_organization_info()
        
        assert org.code == "1293310"
        assert org.name == "Test Organization"
        assert org.region == "807"
    
    def test_extract_period_1isth(self):
        """Test period extraction for 1-isth."""
        html = """
        <html>
        <body>
            <input name="tab1:0:j_idt51:j_idt55" value="100">
            <input name="year_select" value="2024">
        </body>
        </html>
        """
        parser = AzstatParser(html)
        period = parser._extract_period()
        
        assert period == "2024" or "2024" in period
    
    def test_unknown_form_type(self):
        """Test handling of unknown form type."""
        html = """
        <html>
        <body>
            <p>Some random content</p>
        </body>
        </html>
        """
        parser = AzstatParser(html)
        # Should not crash, should return 'unknown'
        assert parser.report_type == 'unknown'
    
    def test_parse_full_report(self):
        """Test parsing a complete report."""
        html = """
        <html>
        <body>
            <input name="organization.code" value="1293310">
            <input name="organization.name" value="Test Org">
            <input name="tab1:0:j_idt51:j_idt55" value="1000">
            <input name="tab1:0:j_idt59:j_idt63" value="800">
        </body>
        </html>
        """
        parser = AzstatParser(html)
        report = parser.parse()
        
        assert report.organization.code == "1293310"
        assert report.report_type == '1-isth'
        assert len(report.section_i.rows) > 0


class TestParserEdgeCases:
    """Edge case tests for parser."""
    
    def test_empty_html(self):
        """Test handling of empty HTML."""
        parser = AzstatParser("")
        report = parser.parse()
        
        assert report.report_type == 'unknown'
        assert report.organization.code == ""
    
    def test_malformed_values(self):
        """Test handling of malformed numeric values."""
        html = """
        <html>
        <body>
            <input name="tab1:0:j_idt51:j_idt55" value="not-a-number">
            <input name="tab1:0:j_idt59:j_idt63" value="1,5">
        </body>
        </html>
        """
        parser = AzstatParser(html)
        section_i = parser.parse_section_i()
        
        # Should default to 0.0 for invalid values
        assert section_i.rows[0].current_year == 0.0
    
    def test_empty_section_i(self):
        """Test when Section I has no data."""
        html = "<html><body></body></html>"
        parser = AzstatParser(html)
        section_i = parser.parse_section_i()
        
        assert section_i.rows == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
