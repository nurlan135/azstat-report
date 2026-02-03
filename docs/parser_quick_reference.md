# AzStat Form Parser - Quick Reference Guide

## Form Codes Quick Reference

| Form | Code | Frequency | Login Param | Status |
|------|------|-----------|-------------|---------|
| 12-isth (Industrial) | 03104047 | Monthly/Quarterly | pr03104047 | ✅ Verified 2026-02-03 |
| 1-isth (Industrial) | 03104055 | Annual | pr03104055 | ✅ Verified 2026-02-03 |

## Verified Input Patterns (2026-02-03)

### 12-isth (pr03104047) - Monthly
**Section I (ng_i1):** `ng_i1:{row}:j_idt{col}:j_idt{col+3}`

| Column | j_idt ID | Month |
|--------|-----------|-------|
| 1 | j_idt58 → j_idt61 | Yanvar |
| 2 | j_idt64 → j_idt67 | Fevral |
| 3 | j_idt70 → j_idt73 | Mart |
| 4 | j_idt76 → j_idt79 | Aprel |
| 5 | j_idt82 → j_idt85 | May |
| 6 | j_idt88 → j_idt91 | İyun |
| 7 | j_idt94 → j_idt97 | İyul |
| 8 | j_idt100 → j_idt103 | Avqust |
| 9 | j_idt106 → j_idt109 | Sentyabr |
| 10 | j_idt112 → j_idt115 | Oktyabr |
| 11 | j_idt118 → j_idt121 | Noyabr |
| 12 | j_idt124 → j_idt127 | Dekabr |

**Example:** `ng_i1:0:j_idt58:j_idt61` (Row 0, Yanvar)

### 1-isth (pr03104055) - Annual
**Section I (tab1):** `tab1:{row}:j_idt{j_idt51|j_idt59}:j_idt{55|63}`

| Column | j_idt ID | Period |
|--------|-----------|--------|
| 1 | j_idt51 → j_idt55 | Hesabat ilində |
| 2 | j_idt59 → j_idt63 | Əvvəlki il |

**Example:** `tab1:0:j_idt51:j_idt55` (Row 0, Cari il)

### Row Counts
- 12-isth: 12 rows (data-ri="0" to "11")
- 1-isth: 16 rows (data-ri="0" to "15")

## URLs Quick Reference

```bash
# Main Portal
https://www.stat.gov.az

# Industrial Forms Page
https://www.stat.gov.az/menu/4/e-reports/az/04/004.php

# Login Pages
https://www.azstat.gov.az/azstatLogin/selectAuth.php?param=pr03104047  # 12-isth
https://www.azstat.gov.az/azstatLogin/selectAuth.php?param=pr03104055  # 1-isth

# Metadata Pages
https://www.azstat.gov.az/MetaDataW/bchaphes.jsp?prkod=03104047  # 12-isth
https://www.azstat.gov.az/MetaDataW/bchaphes.jsp?prkod=03104055  # 1-isth

# Download Forms
https://www.azstat.gov.az/onlinedoc/d03104047.rar  # 12-isth
https://www.azstat.gov.az/onlinedoc/d03104055.rar  # 1-isth
```

## HTML Structure Patterns

### Form Selector Patterns
```python
# Find login form
form = soup.find('form', {'id': 'j_idt7'})

# Find organization code input
voen_input = soup.find('input', {'id': 'login'})

# Find password input
password_input = soup.find('input', {'id': 'passwd'})

# Find ViewState (anti-CSRF)
viewstate = soup.find('input', {'name': 'javax.faces.ViewState'})
```

### Data Table Patterns
```python
# Find data tables
tables = soup.find_all('table')

# Find table headers
headers = soup.find_all('th')

# Find table rows
rows = soup.find_all('tr')
```

## Expected Form Fields

### Section I - Organization Info
- `voen` - Organization code (10 digits)
- `org_name` - Organization name
- `address` - Address
- `region` - Region/Rayon

### Section II - Period Info
- `report_year` - Report year (YYYY)
- `report_month` - Report month (1-12)
- `report_quarter` - Report quarter (1-4)

### Section III - Production Data
- `revenue_total` - Total revenue
- `own_production` - Own production value
- `trade_margin` - Trade margin
- `services` - Services provided
- `inventory_prev` - Previous month inventory
- `production` - Production during period
- `shipped` - Shipped/sold quantity
- `internal_use` - Internal use
- `inventory_current` - Current inventory

### Section IV - Detailed Rows
- `product_code` - Product code (ISIC)
- `product_name` - Product name
- `unit` - Unit of measurement
- `quantity` - Quantity
- `price` - Price per unit
- `value` - Total value

## Validation Rules Summary

| Category | Type | Action |
|----------|------|--------|
| ERROR | Negative values | Block submission |
| ERROR | Missing required fields | Block submission |
| ERROR | Invalid data type | Block submission |
| WARNING | Logical inconsistency | Show warning |
| WARNING | Revenue < Production | Show warning |
| WARNING | Inventory mismatch | Show warning |
| INFO | Large changes (>50%) | Highlight |
| INFO | Zero values | Flag for review |

## Python Code Snippets

### Basic HTML Fetch
```python
import requests

def fetch_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text
```

### Parse Form Structure
```python
from bs4 import BeautifulSoup

def parse_form_structure(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract form info
    form = soup.find('form', {'id': 'j_idt7'})
    if form:
        action = form.get('action')
        method = form.get('method')
        
    # Extract inputs
    inputs = soup.find_all('input')
    for inp in inputs:
        name = inp.get('name')
        id = inp.get('id')
        type = inp.get('type')
        
    return {
        'action': action,
        'method': method,
        'inputs': [{'name': n, 'id': i, 'type': t} for n, i, t in ...]
    }
```

### Extract Tables
```python
def extract_tables(html):
    soup = BeautifulSoup(html, 'html.parser')
    tables = []
    
    for table in soup.find_all('table'):
        data = []
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)
        tables.append(data)
    
    return tables
```

## Session Management Example
```python
import requests

session = requests.Session()

# Get initial page
response = session.get('https://azstat.gov.az/loginControl/')

# Extract ViewState
soup = BeautifulSoup(response.text, 'html.parser')
viewstate = soup.find('input', {'name': 'javax.faces.ViewState'})
viewstate_value = viewstate.get('value')

# Login
login_data = {
    'j_idt7': 'j_idt7',
    'login': 'VOEN_CODE',
    'passwd': 'PASSWORD',
    'j_idt21': 'Daxil olun',
    'javax.faces.ViewState': viewstate_value
}

response = session.post(
    'https://azstat.gov.az/loginControl/faces/main.xhtml',
    data=login_data
)
```

## Error Handling
```python
class AzstatParserError(Exception):
    """Base exception for parser errors"""
    pass

class AuthenticationError(AzsstatParserError):
    """Failed to authenticate"""
    pass

class FormNotFoundError(AzstatParserError):
    """Form not found"""
    pass

class ParsingError(AzstatParserError):
    """Failed to parse HTML"""
    pass
```

## Next Steps for Development

1. **Week 1 (Backend):**
   - [x] Download form RAR files (actual HTML captured 2026-02-03)
   - [x] Extract and analyze form structure (verified input patterns)
   - [ ] Build basic HTML parser
   - [ ] Test with sample data

2. **Week 2 (Validation):**
   - [ ] Implement validation rules
   - [ ] Build data extraction engine
   - [ ] Test validation logic
   - [ ] Create error handling

3. **Week 3 (Frontend):**
   - [ ] Build web interface
   - [ ] Implement file upload
   - [ ] Create result display
   - [ ] User testing

4. **Week 4 (Integration):**
   - [ ] Integration testing
   - [ ] Bug fixes
   - [ ] Performance optimization
   - [ ] Deployment

## Contact for Support

- **Technical Issues:** Check PRD document
- **Form Questions:** AzStat support at (012) 377-10-70
- **Parser Issues:** Review error logs

---

**Last Updated:** 2026-02-03  
**Version:** 1.1 (with verified patterns)
