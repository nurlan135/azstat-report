# HTML Parser for azstat.gov.az forms

from bs4 import BeautifulSoup
from typing import Optional, List, Dict
from models import (
    OrganizationInfo, SectionIRow, SectionI, 
    ProductRow, SectionII, ReportData
)
from config import Config


class AzstatParser:
    """Parser for azstat.gov.az HTML reports."""
    
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'lxml')
        self.report_type = self._detect_report_type()
        self.report_period = ""
    
    def _detect_report_type(self) -> str:
        """Detect 1-isth (annual) or 12-isth (monthly)."""
        # Check for form code in various places
        form_code = None
        
        # Try finding form code in hidden inputs or scripts
        for input_tag in self.soup.find_all('input'):
            name = input_tag.get('name', '')
            if 'formCode' in name or 'formcode' in name.lower():
                form_code = input_tag.get('value', '')
                break
        
        # Try finding in page content
        page_text = self.soup.get_text()
        if '03104055' in page_text or '1-istehsal' in page_text.lower():
            return '1-isth'
        elif '03104047' in page_text or '12-istehsal' in page_text.lower():
            return '12-isth'
        
        # Check input name patterns
        if self.soup.find_all('input', {'name': lambda x: x and x.startswith('tab1:')}):
            return '1-isth'
        elif self.soup.find_all('input', {'name': lambda x: x and x.startswith('ng_i1:')}):
            return '12-isth'
        
        return 'unknown'
    
    def parse(self) -> ReportData:
        """Parse complete report."""
        return ReportData(
            organization=self.parse_organization_info(),
            report_type=self.report_type,
            report_period=self._extract_period(),
            section_i=self.parse_section_i(),
            section_ii=self.parse_section_ii(),
        )
    
    def parse_organization_info(self) -> OrganizationInfo:
        """Parse organization header info."""
        org_info = OrganizationInfo()
        
        # Try to find organization info from various patterns
        # Pattern 1: organization.code, organization.name, etc.
        for input_tag in self.soup.find_all('input', {'name': lambda x: x and 'organization' in x.lower()}):
            name = input_tag.get('name', '').lower()
            value = input_tag.get('value', '')
            
            if 'code' in name and 'property' not in name:
                org_info.code = value
            elif 'name' in name:
                org_info.name = value
            elif 'region' in name:
                org_info.region = value
            elif 'property' in name:
                org_info.property_type = value
            elif 'activity' in name:
                org_info.activity_code = value
            elif 'type' in name:
                org_info.organization_type = value
        
        # Try parsing from table structure
        if not org_info.code:
            # Look for table with organization info
            for table in self.soup.find_all('table'):
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    for i, cell in enumerate(cells):
                        cell_text = cell.get_text(strip=True)
                        # Look for code patterns (10 digits)
                        if cell_text.isdigit() and len(cell_text) >= 7:
                            org_info.code = cell_text
                            # Check next cell for name
                            if i + 1 < len(cells):
                                org_info.name = cells[i + 1].get_text(strip=True)
                            break
        
        return org_info
    
    def parse_section_i(self) -> SectionI:
        """Parse Section I - financial data."""
        section_i = SectionI()
        
        if self.report_type == '1-isth':
            section_i.rows = self._parse_section_i_1isth()
        elif self.report_type == '12-isth':
            section_i.rows = self._parse_section_i_12isth()
        else:
            # Try both patterns
            rows = self._parse_section_i_1isth()
            if rows:
                section_i.rows = rows
            else:
                section_i.rows = self._parse_section_i_12isth()
        
        return section_i
    
    def _parse_section_i_1isth(self) -> List[SectionIRow]:
        """Parse Section I for 1-isth (annual) form."""
        rows = []
        
        # Row codes for 1-isth
        row_codes = [
            "1", "1.1", "1.1.1", "2", "2.1", "2.2", 
            "3", "3.1", "3.2", "4", "5", "6", "7", "8", "9"
        ]
        
        # Input pattern: tab1:{row}:j_idt51:j_idt55 (current year)
        #               tab1:{row}:j_idt59:j_idt63 (previous year)
        
        for row_index in range(16):  # 0 to 15
            row_code = row_codes[row_index] if row_index < len(row_codes) else str(row_index)
            row_name = self._get_row_name_1isth(row_code)
            
            current_year = 0.0
            previous_year = 0.0
            
            # Current year column
            current_input = self.soup.find('input', {
                'name': f'tab1:{row_index}:j_idt51:j_idt55'
            })
            if current_input:
                try:
                    current_year = float(current_input.get('value', '0').replace(',', '.'))
                except ValueError:
                    current_year = 0.0
            
            # Previous year column
            prev_input = self.soup.find('input', {
                'name': f'tab1:{row_index}:j_idt59:j_idt63'
            })
            if prev_input:
                try:
                    previous_year = float(prev_input.get('value', '0').replace(',', '.'))
                except ValueError:
                    previous_year = 0.0
            
            # Alternative pattern: j_idt51:j_idt55 without prefix
            if current_year == 0:
                alt_input = self.soup.find('input', {
                    'name': lambda x: x and f'tab1:{row_index}:' in x and 'j_idt55' in x
                })
                if alt_input:
                    try:
                        current_year = float(alt_input.get('value', '0').replace(',', '.'))
                    except ValueError:
                        pass
            
            rows.append(SectionIRow(
                row_code=row_code,
                row_name=row_name,
                current_year=current_year,
                previous_year=previous_year
            ))
        
        return rows
    
    def _parse_section_i_12isth(self) -> List[SectionIRow]:
        """Parse Section I for 12-isth (monthly) form."""
        rows = []
        
        # Row codes for 12-isth
        row_codes = [
            "1", "1.1", "1.2", "1.3", "2", "3", "4", 
            "5", "6", "6.1", "7", "7.1"
        ]
        
        # Input pattern: ng_i1:{row}:j_idt58:j_idt61 (January)
        # Columns: j_idt57, j_idt63, j_idt69, j_idt75, j_idt81, j_idt87,
        #          j_idt93, j_idt99, j_idt105, j_idt111, j_idt117, j_idt123
        
        # For now, we only extract December (last column) as the main value
        dec_col = 123
        
        for row_index in range(12):  # 0 to 11
            row_code = row_codes[row_index] if row_index < len(row_codes) else str(row_index)
            row_name = self._get_row_name_12isth(row_code)
            
            value = 0.0
            input_name = f'ng_i1:{row_index}:j_idt{dec_col-3}:j_idt{dec_col}'
            input_tag = self.soup.find('input', {'name': input_name})
            
            if input_tag:
                try:
                    value = float(input_tag.get('value', '0').replace(',', '.'))
                except ValueError:
                    value = 0.0
            
            # Try alternative pattern
            if value == 0:
                input_name = f'ng_i1:{row_index}:j_idt58:j_idt61'
                input_tag = self.soup.find('input', {'name': input_name})
                if input_tag:
                    try:
                        value = float(input_tag.get('value', '0').replace(',', '.'))
                    except ValueError:
                        pass
            
            rows.append(SectionIRow(
                row_code=row_code,
                row_name=row_name,
                current_year=value,
                previous_year=0.0  # Monthly form doesn't have previous year in section I
            ))
        
        return rows
    
    def _get_row_name_1isth(self, row_code: str) -> str:
        """Get row name for 1-isth form."""
        row_names = {
            "1": "Malların satışı (cəmi)",
            "1.1": "...müəsisənin öz istehsalı məhsullarının satışı",
            "1.1.1": "....yerinə yetirilmiş işlərin və göstərilmiş xidmətlərin dəyəri",
            "2": "Öz istehsalı hazır məhsul və bitməmiş istehsalın qalığı",
            "2.1": "...hesabat ilinin əvvəlinə",
            "2.2": "...hesabat ilinin sonuna",
            "3": "Bitməmiş istehsalın dəyəri",
            "3.1": "...hesabat ilinin əvvəlinə",
            "3.2": "...hesabat ilinin sonuna",
            "4": "Sifarişçiyə məxsus xammal, material və yarımfabrikatların dəyəri",
            "5": "Digər hüquqi şəxslərə emal üçün verilmiş materialların dəyəri",
            "6": "Malların idxalı",
            "7": "Xidmətlərin idxalı",
            "8": "Malların ixracı",
            "9": "Xidmətlərin ixracı"
        }
        return row_names.get(row_code, f"Row {row_code}")
    
    def _get_row_name_12isth(self, row_code: str) -> str:
        """Get row name for 12-isth form."""
        row_names = {
            "1": "Malların təqdim edilməsi və xidmətlərin göstərilməsi (cəmi)",
            "1.1": "...müəsisənin öz istehsalı məhsullarının satışı",
            "1.2": "1-ci sətirdən: ixrac üçün",
            "1.3": "1.1-ci sətirdən: xidmətlərin göstərilməsi",
            "2": "Hesabat dövrünün sonuna hazır məhsul və bitməmiş istehsalın qalığı",
            "3": "...satış üçün alınmış malların dəyəri",
            "4": "Pərakəndə ticarətin dövriyyəsi",
            "5": "İctimai iaşənin dövriyyəsi",
            "6": "Əhaliyə göstərilən xidmətlərin həcmi",
            "6.1": "...onlayn (elektron) ödəmələrin həcmi",
            "7": "Gələcək dövrlər üçün sifarişlər",
            "7.1": "...xarici ölkələrdən"
        }
        return row_names.get(row_code, f"Row {row_code}")
    
    def parse_section_ii(self) -> SectionII:
        """Parse Section II - products table."""
        section_ii = SectionII()
        section_ii.products = self._parse_products()
        return section_ii
    
    def _parse_products(self) -> List[ProductRow]:
        """Parse product rows from Section II."""
        products = []
        
        # Find product table based on report type
        if self.report_type == '1-isth':
            # Look for tab2 pattern
            products = self._parse_products_generic('tab2', 'j_idt155')
        elif self.report_type == '12-isth':
            # Look for ng_i2 pattern
            products = self._parse_products_generic('ng_i2', 'j_idt151')
        else:
            # Try both patterns
            products = self._parse_products_generic('tab2', 'j_idt155')
            if not products:
                products = self._parse_products_generic('ng_i2', 'j_idt151')
        
        return products
    
    def _parse_products_generic(self, table_prefix: str, col_prefix: str) -> List[ProductRow]:
        """Generic product parser."""
        products = []
        
        # Column names for Section II
        # 0: Product Code
        # 1: Product Name
        # 2: Unit
        # 3: Produced
        # 4: Internal Use
        # 5: Sold Quantity
        # 6: Sold Value
        # 7: Year End Stock
        # 8: Import Value
        
        row_index = 0
        while True:
            product = ProductRow()
            found = False
            
            # Product code input
            code_input = self.soup.find('input', {
                'name': f'{table_prefix}:{row_index}:{col_prefix}'
            })
            
            # Product name (might be in autocomplete input)
            name_input = self.soup.find('input', {
                'name': f'{table_prefix}:{row_index}:{col_prefix}_input'
            })
            
            if code_input or name_input:
                found = True
                if code_input:
                    product.product_code = code_input.get('value', '')
                if name_input:
                    product.product_name = name_input.get('value', '')
            
            # If we found a product row, extract other fields
            if found:
                # Try to find unit (next columns)
                unit_col = int(col_prefix.replace('j_idt', '')) + 3
                unit_input = self.soup.find('input', {
                    'name': f'{table_prefix}:{row_index}:j_idt{unit_col}'
                })
                if unit_input:
                    product.unit = unit_input.get('value', '')
                
                # Produced (col + 4)
                prod_col = unit_col + 1
                prod_input = self.soup.find('input', {
                    'name': f'{table_prefix}:{row_index}:j_idt{prod_col}'
                })
                if prod_input:
                    try:
                        product.produced = float(prod_input.get('value', '0').replace(',', '.'))
                    except ValueError:
                        pass
                
                # Internal Use (col + 5)
                internal_col = prod_col + 1
                internal_input = self.soup.find('input', {
                    'name': f'{table_prefix}:{row_index}:j_idt{internal_col}'
                })
                if internal_input:
                    try:
                        product.internal_use = float(internal_input.get('value', '0').replace(',', '.'))
                    except ValueError:
                        pass
                
                # Sold Quantity (col + 6)
                qty_col = internal_col + 1
                qty_input = self.soup.find('input', {
                    'name': f'{table_prefix}:{row_index}:j_idt{qty_col}'
                })
                if qty_input:
                    try:
                        product.sold_quantity = float(qty_input.get('value', '0').replace(',', '.'))
                    except ValueError:
                        pass
                
                # Sold Value (col + 7)
                value_col = qty_col + 1
                value_input = self.soup.find('input', {
                    'name': f'{table_prefix}:{row_index}:j_idt{value_col}'
                })
                if value_input:
                    try:
                        product.sold_value = float(value_input.get('value', '0').replace(',', '.'))
                    except ValueError:
                        pass
                
                # Year End Stock (col + 8)
                stock_col = value_col + 1
                stock_input = self.soup.find('input', {
                    'name': f'{table_prefix}:{row_index}:j_idt{stock_col}'
                })
                if stock_input:
                    try:
                        product.year_end_stock = float(stock_input.get('value', '0').replace(',', '.'))
                    except ValueError:
                        pass
                
                # Import Value (col + 9)
                import_col = stock_col + 1
                import_input = self.soup.find('input', {
                    'name': f'{table_prefix}:{row_index}:j_idt{import_col}'
                })
                if import_input:
                    try:
                        product.import_value = float(import_input.get('value', '0').replace(',', '.'))
                    except ValueError:
                        pass
                
                products.append(product)
                row_index += 1
            else:
                # Check if we hit the limit or really no more rows
                if row_index > 100:  # Safety limit
                    break
                if row_index == 0:
                    break
                # Try one more time to be sure
                test_input = self.soup.find('input', {
                    'name': f'{table_prefix}:{row_index}:{col_prefix}'
                })
                if not test_input:
                    break
                row_index += 1
        
        return products
    
    def _extract_period(self) -> str:
        """Extract report period from form."""
        if self.report_type == '1-isth':
            # Try to find year
            year = ""
            for input_tag in self.soup.find_all('input'):
                name = input_tag.get('name', '').lower()
                if 'year' in name or 'il' in name:
                    year = input_tag.get('value', '')
                    break
            
            if not year:
                # Try finding in select options
                for select in self.soup.find_all('select'):
                    if 'year' in select.get('name', '').lower():
                        selected = select.find('option', selected=True)
                        if selected:
                            year = selected.get('value', '')
                        break
            
            return year if year else "2024"
        
        elif self.report_type == '12-isth':
            # Try to find year and month
            year = ""
            month = ""
            
            for input_tag in self.soup.find_all('input'):
                name = input_tag.get('name', '').lower()
                if 'year' in name or 'il' in name:
                    year = input_tag.get('value', '')
                elif 'month' in name or 'ay' in name:
                    month = input_tag.get('value', '')
            
            if not year:
                for select in self.soup.find_all('select'):
                    name = select.get('name', '').lower()
                    if 'year' in name:
                        selected = select.find('option', selected=True)
                        if selected:
                            year = selected.get('value', '')
                    elif 'month' in name:
                        selected = select.find('option', selected=True)
                        if selected:
                            month = selected.get('value', '')
            
            month = month.zfill(2) if month else "12"
            return f"{year}-{month}" if year else "2024-12"
        
        return "2024"
