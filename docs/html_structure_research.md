# AzStat.gov.az HTML Form Structure Research Report
## 1-isth and 12-isth Industrial Statistical Report Forms

**Research Date:** 2026-02-01 (updated 2026-02-03)
**Researcher:** Automated Research Agent
**Status:** Complete with Actual HTML Snapshots

---

## Executive Summary

This report provides a detailed analysis of the HTML form structure for the Azerbaijan State Statistical Committee's electronic reporting system, specifically focusing on the 1-isth (annual) and 12-isth (monthly/quarterly) industrial production forms. The research covers authentication mechanisms, form submission systems, and potential data extraction patterns.

**Key Findings:**
- The system uses JavaServer Faces (JSF) with PrimeFaces components
- Two authentication methods: Digital Login (electronic signature) and Code/Password
- Form metadata accessible at: `https://www.azstat.gov.az/MetaDataW/bchaphes.jsp?prkod={form_code}`
- Actual form submission requires authentication
- Session-based authentication with JSESSIONID

**Updated 2026-02-03:** Actual HTML snapshots captured for both form types with verified input patterns.

---

## Form Snapshots (2026-02-03)

| Form Type | Form Code | Year/Period | HTML Snapshot |
|----------|-----------|-------------|--------------|
| 12-isth (aylıq) | pr03104047 | Dekabr 2025 | `/home/ubuntu/.openclaw/media/inbound/file_52---a1e50ad5...` |
| 1-isth (illik) | pr03104055 | 2024 | `/home/ubuntu/.openclaw/media/inbound/file_53---a7609ac5...` |

## Verified Input Patterns

### 12-isth (Monthly) - pr03104047
```html
<!-- Section I (I bölmə) - Ümumi iqtisadi göstəricilər -->
<!-- Input pattern: ng_i1:{row}:j_idt{col_start}:j_idt{col_end} -->
<!-- Columns: Yanvar(57), Fevral(63), Mart(69), Aprel(75), May(81), İyun(87), 
           İyul(93), Avqust(99), Sentyabr(105), Oktyabr(111), Noyabr(117), Dekabr(123) -->

<input type="text" name="ng_i1:0:j_idt58:j_idt61" value="61">
<input type="text" name="ng_i1:1:j_idt58:j_idt61" value="59.9">

<!-- Row indicators: data-ri="0" to "11" (12 rows) -->
```

### 1-isth (Annual) - pr03104055
```html
<!-- Section I (I bölmə) - Ümumi iqtisadi göstəricilər -->
<!-- Input pattern: tab1:{row}:j_idt{j_idt51|j_idt59}:j_idt{55|63} -->
<!-- Columns: Hesabat ilində (j_idt51→j_idt55), Əvvəlki il (j_idt59→j_idt63) -->

<input type="text" name="tab1:0:j_idt51:j_idt55" value="682.3">
<input type="text" name="tab1:0:j_idt59:j_idt63" value="0.0">

<!-- Row indicators: data-ri="0" to "15" (16 rows) -->
```

### Section II (II bölmə) - Products

#### 12-isth - ng_i2
```html
<!-- Dynamic product rows with autocomplete -->
<input id="ng_i2:0:j_idt151" name="ng_i2:0:j_idt151">

<!-- Product code: 016110430 - A seksiyası.Torpaqların suvarılması -->
```

#### 1-isth - tab2
```html
<!-- Dynamic product rows with autocomplete -->
<input id="tab2:0:j_idt155_input" name="tab2:0:j_idt155_input" 
       value="016110430 - A seksiyası.Torpaqların suvarılması">
```

---

## 1. Form Identification

### 1.1 Form Codes and Details

#### 12-isth (Monthly/Quarterly Industrial Production Form)
- **Form Code:** 03104047
- **Form Name:** 12-istehsal (sənaye) №-li forma
- **Full Name:** Malların istehsalı, təqdim edilməsi və xidmətlərin göstərilməsi haqqında
- **Frequency:** Monthly (for medium/large enterprises), Quarterly (for micro enterprises)
- **Submission Deadline:** 
  - Monthly: 5th working day of the following month by 13:00
  - Quarterly: 5th working day of the month following the quarter by 13:00
- **Actual URL:** https://azstat.gov.az/pr03104047/faces/inputpage.xhtml?cid=1

#### 1-isth (Annual Industrial Production Form)
- **Form Code:** 03104055
- **Form Name:** 1-istehsal (sənaye) №-li forma
- **Full Name:** Malların istehsalı, təqdim edilməsi və xidmətlərin göstərilməsi haqqında
- **Frequency:** Annual
- **Submission Deadline:** March 15th
- **Actual URL:** https://azstat.gov.az/pr03104055/faces/inputpage.xhtml?cid=2
- **Metadata URL:** https://www.azstat.gov.az/MetaDataW/bchaphes.jsp?prkod=03104047
- **Download URL:** https://www.azstat.gov.az/onlinedoc/d03104047.rar
- **Login URL:** https://www.azstat.gov.az/azstatLogin/selectAuth.php?param=pr03104047

#### 1-isth (Annual Industrial Production Form)
- **Form Code:** 03104055
- **Form Name:** 1-istehsal (sənaye) №-li forma
- **Full Name:** Malların istehsalı, təqdim edilməsi və xidmətlərin göstərilməsi haqqında
- **Frequency:** Annual
- **Submission Deadline:** March 15th
- **Metadata URL:** https://www.azstat.gov.az/MetaDataW/bchaphes.jsp?prkod=03104055
- **Download URL:** https://www.azstat.gov.az/onlinedoc/d03104055.rar
- **Login URL:** https://www.azstat.gov.az/azstatLogin/selectAuth.php?param=pr03104055

### 1.2 Scope and Coverage
- **Observation Unit:** Legal entities (Hüquqi şəxs)
- **Coverage:** All industrial enterprises (ISIC Rev. 4 sections 05-39)
- **Data Subject:** Production of goods, provision of services

---

## 2. Authentication System Structure

### 2.1 Authentication Entry Points

#### Method 1: Digital Login (Electronic Signature)
```html
<form id="main_form" method="post" action="https://www.azstat.gov.az/azstatLogin/">
    <input type="hidden" name="param" value="pr03104047">
    <button type="submit" class="btn btn-primary">
        "Digital login" vasitəsilə davam etmək
    </button>
</form>
```

#### Method 2: Code and Password (Traditional)
```html
<form id="main_form" method="post" action="https://azstat.gov.az/loginControl/">
    <input type="hidden" name="param" value="pr03104047">
    <button type="submit" class="btn btn-primary">
        Kod və parol vasitəsilə davam etmək
    </button>
</form>
```

### 2.2 Login Form Structure (Traditional Method)

**URL:** https://azstat.gov.az/loginControl/

**Technology Stack:**
- JavaServer Faces (JSF) with Mojarra
- PrimeFaces 5.3 Component Library
- Session-based authentication (JSESSIONID)

**HTML Form Structure:**
```html
<form id="j_idt7" 
      name="j_idt7" 
      method="post" 
      action="/loginControl/faces/main.xhtml;jsessionid={session_id}?cid=1"
      enctype="application/x-www-form-urlencoded">
    <input type="hidden" name="j_idt7" value="j_idt7" />
    
    <!-- Login Fields -->
    <input id="login" 
           type="text" 
           name="login" 
           autocomplete="off" 
           style="font-size: 0.8em; width: 84px" />
    
    <input id="passwd" 
           type="password" 
           name="passwd" 
           value="" 
           style="width: 84px" />
    
    <input id="j_idt21" 
           type="submit" 
           name="j_idt21" 
           value="Daxil olun" 
           style="width: 120px" />
    
    <!-- Hidden ViewState Field -->
    <input type="hidden" 
           name="javax.faces.ViewState" 
           id="j_id1:javax.faces.ViewState:0" 
           value="{viewstate_value}" 
           autocomplete="off" />
</form>
```

### 2.3 Registration Form Structure

**HTML Elements:**
```html
<!-- Password Creation Dialog -->
<input type="password" name="j_idt50" value="******" />
<input type="password" name="j_idt52" value="******" />
<input id="maile" type="text" name="maile" autocomplete="off" />

<!-- Submit Buttons -->
<input id="j_idt55" type="submit" name="j_idt55" value="İmtina" />
<input id="j_idt56" type="submit" name="j_idt56" value="OK" />

<!-- Error Message Display -->
<span id="errmese" style="color: #FF0000"></span>
```

---

## 3. Website Navigation Structure

### 3.1 Main Navigation Menu

**Main Website:** https://www.stat.gov.az

**Key Menu Items:**
1. **Baş səhifə** (Home)
2. **Haqqımızda** (About) → Structure, Board, Reports, etc.
3. **Qanunvericilik** (Legislation) → Laws, Regulations
4. **E-xidmətlər** (E-services) → Electronic Reports
5. **Təsnifatlar** (Classifications) → Electronic Classification System
6. **Statistik nəşrlər** (Statistical Publications)
7. **Metaməlumatlar** (Metadata)
8. **Bizimlə əlaqə** (Contact Us)

### 3.2 E-Services Section

**URL:** https://www.stat.gov.az/menu/4/

**Key Electronic Services:**
- **Rəsmi statistik hesabatların təqdim edilməsi** (Submission of Official Statistical Reports)
- **Statistik məlumatların verilməsi** (Provision of Statistical Data)
- **Statistik nəşrlərin onlayn satışı** (Online Sale of Statistical Publications)

### 3.3 Industrial Forms Navigation

**URL:** https://www.stat.gov.az/menu/4/e-reports/az/04/004.php

**Form Table Structure:**
```html
<table>
    <tr>
        <th width="6%">Formanın kodu (Form Code)</th>
        <th width="50%">Formanın nömrəsi, adı (Form Number, Name)</th>
        <th width="12%">Hesabatları təqdim etmək üçün proqram təminatı (Software)</th>
        <th width="18%">Təqdim edilmə müddəti (Submission Deadline)</th>
    </tr>
    <!-- Form rows -->
</table>
```

---

## 4. HTML Structure Analysis

### 4.1 General HTML Patterns

**DOCTYPE and Encoding:**
```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
```

**Common CSS Framework:**
- Bootstrap 4.x (for newer interfaces)
- Custom CSS with class names like:
  - `.modal` - Modal dialogs
  - `.modal-dialog` - Modal window
  - `.modal-content` - Modal content area
  - `.modal-header`, `.modal-body`, `.modal-footer`
  - `.btn`, `.btn-primary` - Buttons
  - `.form-control` - Form inputs

### 4.2 Modal Dialog Structure

**Authentication Modal:**
```html
<div class="modal" 
     style="background:#B8B8B8; font-size:0.9rem;" 
     id="myModal" 
     data-backdrop="static" 
     data-keyboard="false" 
     tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">B İ L D İ R İ Ş</h5>
            </div>
            <div class="modal-body" style="padding:10px 50px;">
                <!-- Notification text -->
            </div>
            <div class="modal-footer">
                <!-- Authentication forms -->
            </div>
        </div>
    </div>
</div>
```

### 4.3 Form Element Patterns

**Input Fields:**
```html
<input type="text" 
       id="element_id" 
       name="element_name" 
       autocomplete="off" 
       style="font-size: 0.8em; width: 84px" />

<input type="password" 
       id="passwd" 
       name="passwd" 
       value="" 
       style="width: 84px" />
```

**Select/Radio Elements:**
```html
<table id="sorgu">
    <tr>
        <td>
            <input type="radio" 
                   name="sorgu" 
                   id="sorgu:0" 
                   value="1" 
                   onclick="text(this.value);" />
            <label for="sorgu:0"> Option text</label>
        </td>
    </tr>
</table>
```

**Textarea Elements:**
```html
<textarea id="textcv" 
          name="textcv" 
          style="resize: none; width: 90%; height: 96px" 
          placeholder="Placeholder text">
</textarea>
```

---

## 5. Expected Form Data Structure

### 5.1 Organization Information Fields

Based on the form metadata and typical statistical reporting patterns, the following fields are expected:

**Organization Identification:**
- **VÖEN** (Organization Code/TIN) - 10-digit numeric code
- **Organization Name** (Müəsisənin adı)
- **Address** (Ünvan)
- **Region/Rayon** (Rayon)
- **Economic Activity Code** (İqtisadi fəaliyyət növü)

**Contact Information:**
- **Phone** (Telefon)
- **Email** (Elektron poçt)
- **Contact Person** (Əlaqəli şəxs)

### 5.2 Report Period Fields

**Date Selection:**
- **Year** (İl) - 4-digit year
- **Month** (Ay) - 1-12
- **Quarter** (Rüb) - 1-4

### 5.3 Section I - Production Data (Expected Fields)

Based on typical industrial production forms:

**Revenue and Sales:**
- **Total Revenue** (Ümumi gəlir) - Column 1
- **Own Production** (Öz istehsalı) - Column 2
- **Trade Margin** (Ticarət əlavəsi) - Column 3
- **Services Provided** (Göstərilən xidmətlər) - Column 4

**Production Details:**
- **Previous Month Inventory** (Əvvəlki ayın anbarı)
- **Production During Month** (Ay ərzində istehsal)
- **Shipped/Sold** (Göndərilmiş/Satılmış)
- **Internal Use** (Daxili ehtiyac)
- **Current Inventory** (Cari anbar)

### 5.4 Section II - Detailed Rows (Expected Fields)

Based on ISIC Rev. 4 Sections 05-39:

**Industrial Categories:**
- Mining and quarrying (05-09)
- Manufacturing (10-33)
- Electricity, gas, steam (35)
- Water supply (36-39)

**Product-Level Data:**
- Product code (Məhsul kodu)
- Product name (Məhsulun adı)
- Unit of measurement (Ölçü vahidi)
- Quantity (Miqdar)
- Price per unit (Qiymət)
- Total value (Ümumi dəyər)

### 5.5 Previous Period Comparison (Expected Fields)

**Comparison Columns:**
- **Previous Month** (Əvvəlki ay)
- **Same Month Last Year** (Keçən ilin eyni ayı)
- **Year to Date** (İlin əvvəlindən)
- **Percentage Change** (Faiz dəyişmə)

---

## 6. Technical Implementation Patterns

### 6.1 Session Management

**Session ID Pattern:**
```
JSESSIONID={32-character-hex-string}
```

**ViewState Pattern:**
```html
<input type="hidden" 
       name="javax.faces.ViewState" 
       id="j_id1:javax.faces.ViewState:0" 
       value="{numeric-value}:{numeric-value}" 
       autocomplete="off" />
```

### 6.2 Form Submission Patterns

**POST Request Structure:**
```
POST /loginControl/faces/main.xhtml;jsessionid={session_id}?cid={conversation_id}
Content-Type: application/x-www-form-urlencoded

j_idt7=j_idt7
&login={voen_code}
&passwd={password}
&javax.faces.ViewState={viewstate_value}
&j_idt21=Daxil+olun
```

### 6.3 URL Patterns

**Base URLs:**
- Main portal: `https://www.stat.gov.az/`
- E-services: `https://www.stat.gov.az/menu/4/`
- Form login: `https://www.azstat.gov.az/azstatLogin/selectAuth.php?param={form_code}`
- Login control: `https://azstat.gov.az/loginControl/`
- Metadata: `https://www.azstat.gov.az/MetaDataW/bchaphes.jsp?prkod={form_code}`

**Form Codes:**
- 12-isth: `pr03104047`
- 1-isth: `pr03104055`

---

## 7. Data Extraction Patterns for Parser

### 7.1 Authentication Bypass Strategy

Since direct authentication requires valid credentials, consider:

1. **API Analysis:** Monitor network traffic during form submission
2. **Downloaded Forms:** Extract RAR files to understand field structure
3. **Public Documentation:** Review metadata pages for field descriptions
4. **Sample Forms:** Request sample forms from the committee

### 7.2 HTML Parsing Recommendations

**Parsing Libraries:**
- **Python:** BeautifulSoup4, lxml, html5lib
- **Java:** Jsoup, HTMLParser
- **JavaScript:** Cheerio, JSDOM

**Key Selectors:**
```python
# Example BeautifulSoup selectors
form = soup.find('form', {'id': 'j_idt7'})
login_input = soup.find('input', {'id': 'login'})
password_input = soup.find('input', {'id': 'passwd'})
viewstate = soup.find('input', {'name': 'javax.faces.ViewState'})
```

### 7.3 Expected Table Structure

**Data Table Pattern:**
```html
<table>
    <thead>
        <tr>
            <th>Header 1</th>
            <th>Header 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
        </tr>
    </tbody>
</table>
```

---

## 8. Security and Access Considerations

### 8.1 Access Restrictions

- **Authentication Required:** Form submission requires valid credentials
- **Session Management:** JSESSIONID-based session tracking
- **ViewState Validation:** Anti-CSRF tokens
- **Digital Signature:** Moving to electronic signature authentication

### 8.2 Data Privacy

- **Confidentiality:** Statistical data is confidential
- **Aggregated Use:** Data used only in aggregated form
- **Legal Protection:** Protected by "Official Statistics Law"

### 8.3 Compliance Requirements

- **Submission Deadlines:** Strict adherence required
- **Penalty:** Administrative fines for late/missing submissions (300-500 AZN)
- **Data Accuracy:** Legal responsibility for data accuracy

---

## 9. Recommendations for Parser Development

### 9.1 Immediate Actions

1. **Download Form Templates:** Get the RAR files for both forms
2. **Analyze Form Structure:** Extract field names and types
3. **Document Validation Rules:** Based on PRD specifications
4. **Build Prototype Parser:** Start with metadata extraction

### 9.2 Authentication Strategy

**Option A: Manual Authentication**
- User provides credentials
- Parser handles session management
- Requires user interaction

**Option B: API Integration**
- Request official API access
- Follow data exchange protocols
- Ensure legal compliance

**Option C: Document Analysis**
- Analyze downloaded forms only
- No authentication required
- Limited to form structure

### 9.3 Parser Architecture

```python
class AzstatFormParser:
    def __init__(self, form_code):
        self.form_code = form_code
        self.metadata_url = f"https://www.azstat.gov.az/MetaDataW/bchaphes.jsp?prkod={form_code}"
        
    def get_metadata(self):
        # Extract form metadata
        pass
    
    def parse_form_structure(self, html_content):
        # Parse HTML structure
        pass
    
    def extract_data(self, html_content):
        # Extract form data
        pass
    
    def validate_data(self, data):
        # Apply validation rules
        pass
```

---

## 10. Appendix

### 10.1 Key URLs Reference

| Purpose | URL |
|---------|-----|
| Main Portal | https://www.stat.gov.az |
| E-Services | https://www.stat.gov.az/menu/4/ |
| Industrial Forms | https://www.stat.gov.az/menu/4/e-reports/az/04/004.php |
| 12-isth Metadata | https://www.azstat.gov.az/MetaDataW/bchaphes.jsp?prkod=03104047 |
| 1-isth Metadata | https://www.azstat.gov.az/MetaDataW/bchaphes.jsp?prkod=03104055 |
| 12-isth Login | https://www.azstat.gov.az/azstatLogin/selectAuth.php?param=pr03104047 |
| 1-isth Login | https://www.azstat.gov.az/azstatLogin/selectAuth.php?param=pr03104055 |
| Login System | https://azstat.gov.az/loginControl/ |
| Video Instructions | https://www.stat.gov.az/menu/4/hesabat_video_telimat.php |

### 10.2 Contact Information

- **Support Phone:** (012) 377-10-70 (internal: 22-80, 34-01)
- **Department:** Statistics Department
- **Legal Basis:** "Official Statistics Law" of Azerbaijan Republic

### 10.3 Document References

- **Form 12-isth Approval:** Decision No. 140/14 dated December 17, 2013
- **Form 1-isth Approval:** Decision No. 26/14 dated May 31, 2023
- **Legal Framework:** Administrative Offences Code, Article 389 (300-500 AZN fine)

---

## 11. Research Limitations

1. **Authentication Required:** Full form access requires valid credentials
2. **Dynamic Content:** Form structure may vary based on user type and permissions
3. **JavaScript Rendering:** Some interfaces may require JavaScript execution
4. **Session Expiration:** Sessions expire, requiring re-authentication
5. **Form Updates:** Form structure may change with regulatory updates

---

## 12. Conclusion

This research provides a comprehensive analysis of the AzStat.gov.az electronic reporting system structure. While direct access to the forms requires authentication, the metadata pages and system architecture have been documented in detail. The findings support the development of an HTML parser for form analysis and validation purposes.

**Next Steps:**
1. Obtain sample forms (RAR files) for structural analysis
2. Develop metadata extraction functionality
3. Build validation rule engine based on PRD specifications
4. Consider API integration for automated data access

---

## 13. Actual Form Structures (Verified 2026-02-03)

### 13.1 Organization Header (Both Forms)

```html
<!-- Organization Info Table -->
<table width="45%" align="left" border="1" cellspacing="0">
  <tr style="background-color: #F5F5F5;font-size: 12px">
    <td align="center">Adı</td>
    <td align="center">Kodu</td>
    <td align="center">Ərazi kodu</td>
    <td align="center">Mülkiyyət</td>
    <td align="center">Fəaliyyət növü</td>
    <td align="center">Sahibkarlıq subyekti</td>
  </tr>
  <tr align="center" style="background-color: white">
    <td>NEFTÇALA SU MELİORASİYA...</td>
    <td>1293310</td>
    <td>807</td>
    <td>Dövlət</td>
    <td>36000</td>
    <td>2</td>
  </tr>
</table>
```

### 13.2 Section I - 12-isth (12 columns)

**HTML Table:** `id="ng_i1"`
**Rows:** data-ri="0" to "11" (12 rows)

| Row Code | Indicator Name |
|----------|--------------|
| 1 | Malların təqdim edilməsi... |
| 1.1 | ...müəsisənin öz istehsalı... |
| 1.2 | 1-ci sətirdən: ixrac... |
| 1.3 | 1.1-ci sətirdən: xidmətlərin... |
| 2 | Hesabat dövrünün sonuna hazır məhsul... |
| 3 | ...satış üçün alınmış malların... |
| 4 | Pərakəndə ticarətin dövriyyəsi... |
| 5 | İctimai iaşənin dövriyyəsi... |
| 6 | Əhaliyə göstərilən xidmətlərin... |
| 6.1 | ...elektron ödəmələrin... |
| 7 | Gələcək dövrlər üçün sifarişlər... |
| 7.1 | ...xarici ölkələrdən |

**Column IDs:** j_idt57, j_idt63, j_idt69, j_idt75, j_idt81, j_idt87, j_idt93, j_idt99, j_idt105, j_idt111, j_idt117, j_idt123

### 13.3 Section I - 1-isth (2 columns)

**HTML Table:** `id="tab1"`
**Rows:** data-ri="0" to "15" (16 rows)

| Row Code | Indicator Name |
|----------|--------------|
| 1 | Malların satışı... (cəmi) |
| 1.1 | ...müəsisənin öz istehsalı... |
| 1.1.1 | ...yerinə yetirilmiş işlərin... |
| 2 | Öz istehsalı hazır məhsul... |
| 2.1 | ...hesabat ilinin əvvəlinə |
| 2.2 | ...hesabat ilinin sonuna |
| 3 | Bitməmiş istehsalın dəyəri |
| 3.1 | ...hesabat ilinin əvvəlinə |
| 3.2 | ...hesabat ilinin sonuna |
| 4 | Sifarişçiyə məxsus xammaldan... |
| 5 | Digər hüquqi şəxslərə emal... |
| 6 | Malların idxalı |
| 7 | Xidmətlərin idxalı |
| 8 | Malların ixracı |
| 9 | Xidmətlərin ixracı |

**Columns:** j_idt39 (Hesabat ilində), j_idt40 (Əvvəlki il)

### 13.4 Parser Implementation Notes

```python
# 12-isth parser pattern
def parse_12isth(html):
    # Find table with id="ng_i1"
    # For each row in tbody[data-ri="0" to "11"]
    # Extract input name="ng_i1:{row}:j_idt{col}:j_idt{col+3}"
    pass

# 1-isth parser pattern
def parse_1isth(html):
    # Find table with id="tab1"
    # For each row in tbody[data-ri="0" to "15"]
    # Extract input name="tab1:{row}:j_idt{j_idt51|j_idt59}:j_idt{55|63}"
    pass
```
