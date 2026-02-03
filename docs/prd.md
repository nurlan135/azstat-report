# Product Requirement Document (PRD)

**Layihə:** azstat-report  
**Versiya:** 1.0  
**Tarix:** 2026-02-01  
**Author:** Nurlan Murad  

---

## 1. Background (Arxa Plan)

### 1.1 Problem Statement

Azərbaycan Respublikası Dövlət Statistika Komitəsinə təqdim edilən sənaye hesabatlarında (1-isth, 12-isth) aşağıdakı problemlər mövcuddur:

- **Vaxt itkisi** - Hesabatların manual yoxlanması uzun vaxt alır
- **Uyğun olmayan rəqəmlər** - Məntiqi səhvlər, uyğunsuzluqlar aşkarlanmır
- **Səhv faizi yüksəkdir** - Formalar təslim ediləndən sonra geri qaytarılır
- **Effektivlik aşağıdır** - Eyni səhvlər təkrarlanır

### 1.2 Market Opportunity

- Azərbaycanda **minlərlə sənaye müəssisi** statistika hesabatı təqdim edir
- Hazırda **manual yoxlama** prosesi mövcuddur
- Avtomatik validasiya sistemi **bazar boşluğu** təmsil edir
- Komitə işçiləri və müəssislər üçün **value** yaratmaq potensialı var

### 1.3 User Personas

| Persona | Rol | Ehtiyaclar |
|---------|-----|------------|
| **Komitə İşçisi** | Hesabatları yoxlayan | Səhvləri tez tapmaq, vizual nəticə |
| **Mühasib/Statistik** | Hesabat dolduran | Səhv yoxlaması, düzəliş göstərişi |
| **Auditor** | Nəticələri analiz edən | Anomaliya trendləri, report tarixcəsi |

### 1.4 Vision Statement

"azstat-report" - Azərbaycan statistika hesabatlarının avtomatik validasiya platforması. Müəssislər və Komitə işçiləri üçün səhv-free, vaxt-qənaətli, şəffaf hesabat prosesi təmin etmək.

---

## 2. Objectives (Hədəflər)

### 2.1 SMART Goals

| Hədəf | Metrika | Hedef |
|-------|---------|-------|
| Səhv azalması | Geri qaytarılan hesabat faizi | 50% azalma |
| Vaxt qənaəti | Manual yoxlama vaxtı | 70% azalma |
| Anomaliya aşkarlama | Aşkarlanan səhv sayı | 100% kritik səhv |
| İstifadəçi memnuniyyəti | İstifadəçi feedback | 4.5/5 |

### 2.2 Key Performance Indicators (KPIs)

- **Upload success rate** - Uğurlu fayl parse %
- **Validation accuracy** - Düzgün aşkarlama %
- **Processing time** - Analiz müddəti (< 5 saniyə)
- **Error detection rate** - Tapılan səhv sayı/ümumi səhv

### 2.3 Risk Mitigation

| Risk | Ehtimal | Həll |
|------|---------|------|
| HTML strukturu dəyişəcək | Orta | Modular parser, tez adaptasiya |
| Performans problemi | Aşağı | SQLite optimizasiya, caching |
| User resistance | Orta | Training, feedback integration |

---

## 3. Features (Funksionallıq)

### 3.1 Core Features

| Feature | Prioritet | Təsvir |
|---------|-----------|--------|
| **HTML File Upload** | Must Have | Hesabat faylı yükləmək |
| **Parse HTML** | Must Have | Formadan məlumat çıxarmaq |
| **Validate Report** | Must Have | 4 kateqoriya üzrə yoxlama |
| **Compare with Previous** | Must Have | Əvvəlki dövr ilə müqayisə |
| **Show Results** | Must Have | Qırmızı/yaşıl vizualizasiya |
| **SQLite Storage** | Should Have | Hesabatları saxlamaq |

### 3.2 Validation Rules

#### ERROR (Bloklayan) - Hesabat təslim edilə bilməz
- Mənfi dəyərlər
- Boş köhnə sahələr (kod, ad)
- Səhv data tipi

#### WARNING (Məntiqi) - Diqqət tələb edir
- Gəlir < Öz istehsalı + Ticarət əlavəsi
- Anbar = Əvvəlki + İstehsal - Göndərilmiş
- Daxili ehtiyac > Ümumi istehsal

#### WARNING (Konsistentlik) - Ziddiyyət yoxlaması
- Sütun 4 <= Sütun 3 (daxili ehtiyac <= istehsal)
- Göndərilmiş + Qalıq <= İstehsal + Əvvəlki

#### INFO (Anomaliya) - Diqqət çəkir
- Gəlir dəyişikliyi > 50%
- İxrac/idxal uyğunsuzluğu
- Sıfır dəyər (məlumat itkisi?)
- Sifarişlərin kəskin azalması

### 3.3 User Benefits

- **Təslim vaxtı** - Səhvləri əvvəlcədən görüb düzəlt
- **Qaytarılma azalır** - Keyfiyyətli hesabat
- **Vaqt qənaəti** - Avtomatik yoxlama
- **Şəffaflıq** - Aydın səhv siyahısı

### 3.4 Future Enhancements (Phase 2)

- Multi-user authentication
- Report history & trends
- API for external systems
- Email notifications
- PDF export

---

## 4. User Experience (İstifadəçi Təcrübəsi)

### 4.1 User Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Upload     │───▶│  Parse      │───▶│  Validate   │───▶│  Show       │
│  HTML File  │    │  HTML       │    │  Report     │    │  Results    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 4.2 Interface Design

- **Sadə və intuitiv** - 3 addımda nəticə
- **Azərbaycanca** dil dəstəyi
- **Qırmızı/Yaşıl** vizual kodlaşdırma
- **Responsive** - Desktop və tablet

### 4.3 Dashboard Components

- Upload bölməsi (drag & drop)
- Nəticə cədvəli (səhv siyahısı)
- Anomaliya kartları
- Müqayisə göstəriciləri

---

## 5. Technical Requirements

### 5.1 Tech Stack

| Component | Texnologiya | Səbəb |
|-----------|-------------|--------|
| **Backend** | Python | Parser, validator, anomaliya detection |
| **Frontend** | Next.js | React, Vercel deployment |
| **Database** | SQLite | Sadə, portable, serverless |
| **Styling** | Tailwind CSS | Sürətli inkişaf |
| **Deployment** | Vercel | Pulsuz, Next.js native |

### 5.2 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Upload     │  │  Results    │  │  Dashboard          │ │
│  │  Component  │  │  Display    │  │  & History          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (Python)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  HTML       │  │  Validator  │  │  SQLite             │ │
│  │  Parser     │  │  Engine     │  │  Database           │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 API Endpoints (Internal)

| Endpoint | Method | Təsvir |
|----------|--------|--------|
| `/api/upload` | POST | HTML fayl yükləmək |
| `/api/validate` | POST | Validasiya etmək |
| `/api/history` | GET | Hesabat tarixcəsi |

### 5.4 Security Measures

- **Input validation** - Fayl tipi, ölçü yoxlaması
- **XSS protection** - HTML sanitization
- **Rate limiting** - Abuse prevention

### 5.5 Performance Metrics

- **Response time** - < 5 saniyə tam analiz
- **Uptime** - 99%
- **File size limit** - 10MB max

---

## 6. Milestones (Mərhələlər)

### 6.1 Development Phases (1 ay = 4 həftə)

| Həftə | Mərhələ | Çıxış |
|-------|---------|--------|
| **Həftə 1** | Backend Core | HTML Parser + SQLite setup |
| **Həftə 2** | Validation Engine | 4 kateqoriya qaydaları |
| **Həftə 3** | Frontend | Upload + Results UI |
| **Həftə 4** | Integration & Test | End-to-end testing |

### 6.2 Critical Path

1. HTML Parser → 2. Validation Rules → 3. API → 4. Frontend → 5. Test

### 6.3 Review Points

- Həftə 1 sonu: Backend prototype demo
- Həftə 2 sonu: Validation engine test
- Həftə 3 sonu: Frontend beta
- Həftə 4 sonu: MVP release

### 6.4 Launch Plan

- **Internal testing** - Komitə işçiləri ilə
- **Feedback collection** - Iteration üçün
- **Bug fixes** - Release əvvəli
- **Deploy to Vercel** - Production

---

## 7. Appendix (Əlavələr)

### 7.1 Form Codes

| Form | Kod | Dövr |
|------|-----|------|
| 1-isth | 03104055 | İllik |
| 12-isth | 03104047 | Aylıq |

### 7.2 Validation Categories Summary

| Kateqoriya | Səviyyə | Təsir |
|------------|---------|-------|
| Format Error | ERROR | Bloklayıcı |
| Logical Error | WARNING | Məsləhət |
| Consistency Error | WARNING | Diqqət |
| Anomaly | INFO | Məlumat |

### 7.3 References

- **Website:** www.stat.gov.az
- **Email:** hesabat@azstat.org
- **Qərar:** 17 dekabr 2013, №140/14

---

## 8. Approval (Təsdiq)

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Owner | Nurlan Murad | | 2026-02-01 |
| Developer | | | |

---

**Document Version History**
| Versiya | Tarix | Dəyişiklik |
|---------|-------|------------|
| 1.0 | 2026-02-01 | İlk draft |

---

*Bu PRD azstat-report layihəsinin əsas sənədidir. Hər hansı dəyişiklik üçün document update olunmalıdır.*
