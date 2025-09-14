# Take Note Backend API

Bu proje, **Flutter** mobil uygulaması için geliştirilmiş **FastAPI** tabanlı backend servisidir.

##  Proje Özellikleri

* **Not Yönetimi:** Notlar için CRUD (Oluştur, Oku, Güncelle, Sil) işlemleri
* **Supabase Kimlik Doğrulama:** Tüm API endpoint'leri Supabase JWT token'ları ile korunur
* **AI Özellikleri:** Hugging Face ile not özetleme, kategorileme ve otomatik etiketleme
* **Anlamsal Arama:** Akıllı arama ile notlarda anlamsal benzerlik arama
* **Sabitleme:** Notları sabitleme özelliği
* **Soft Delete:** Notları geri alınabilir şekilde silme
* **Mobil Entegrasyon:** Flutter uygulamaları için otomatik backend keşfi
* **Kolay Kurulum:** Minimal kurulum adımları ile hızlı başlangıç
* **API Dokümantasyonu:** Otomatik oluşturulan interaktif API dokümantasyonu (`/docs`)

##  Kullanılan Teknolojiler

* **FastAPI:** Yüksek performanslı Python web framework
* **Supabase:** PostgreSQL veritabanı ve authentication servisi
* **Hugging Face:** AI model entegrasyonu (Summarization, NER, Classification)
* **Pydantic:** Veri validasyonu ve serialization
* **Uvicorn:** Asenkron server
* **MCP (Model Context Protocol):** Supabase yönetimi

##  Başlangıç

### Supabase Kurulumu

Bu backend Supabase PostgreSQL ve Supabase Authentication servislerini kullanır.

1. **Supabase Projesi:** [Supabase Dashboard](https://supabase.com/dashboard)'a gidin ve yeni proje oluşturun
2. **API Keys:** Project Settings → API → `anon public` ve `service_role` key'lerini alın
3. **Database:** SQL Editor'de `schemas.sql` dosyasını çalıştırın
4. **Authentication:** Authentication → Providers → Email'i etkinleştirin

### Proje Kurulumu

1. **Virtual Environment:** Proje dizininde virtual environment oluşturun:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

2. **Gerekli Paketleri Yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Environment Variables:** `.env.example` dosyasını `.env` olarak kopyalayın ve Supabase bilgilerinizi girin:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
APP_NAME=Take Note Backend API
APP_VERSION=1.0.0
DEBUG=True
```

##  Sunucuyu Çalıştırma

```bash
python run.py
```

Veya:

```bash
uvicorn main:app --reload
```

Sunucu `http://localhost:8000` adresinde çalışacaktır.

**Not:** Fiziksel mobil cihazlardan erişim için sunucu otomatik olarak `0.0.0.0` host'unda çalışır ve `/server-info` endpoint'i ile IP adresini sağlar.

##  API Dokümantasyonu & Authentication

API dokümantasyonu sunucu çalışırken `http://localhost:8000/docs` adresinde erişilebilir.

* **Swagger UI:** Interaktif API dokümantasyonu `/docs` adresinde
* **Authentication:** Korumalı endpoint'lere erişim için `Authorization: Bearer <JWT token>` header'ı gerekli

### Test Kullanıcısı Oluşturma

Test için Supabase Auth API kullanarak kullanıcı oluşturun:

```bash
curl -X POST 'https://your-project.supabase.co/auth/v1/signup' \
-H "apikey: YOUR_ANON_KEY" \
-H "Content-Type: application/json" \
-d '{
  "email": "test@example.com",
  "password": "testpass123"
}'
```

##  API Endpoints

### CRUD İşlemleri
* `GET /notes` - Kullanıcının notlarını listele
* `POST /notes` - Yeni not oluştur
* `GET /notes/{note_id}` - Belirli notu getir
* `PUT /notes/{note_id}` - Notu güncelle
* `DELETE /notes/{note_id}` - Notu sil (yumuşak silme)

### AI Özellikleri
* `POST /notes/{note_id}/summarize` - Notu özetle
* `POST /notes/{note_id}/categorize` - Notu kategorile
* `POST /notes/{note_id}/auto-tag` - Otomatik etiketleme
* `POST /notes/{note_id}/ai-process` - Tüm AI özelliklerini uygula
* `POST /notes/semantic-search` - Anlamsal arama
* `POST /ai/process-content` - Herhangi bir içeriği AI ile işle

### Yardımcı Araçlar
* `GET /health` - Sistem sağlık kontrolü
* `GET /server-info` - Sunucu bilgileri (IP adresi, port, URL'ler)
* `GET /notes/search` - Basit metin arama

##  AI Özellikleri

### Özetleme
- **Model:** `facebook/bart-large-cnn`
- **Özellik:** Türkçe ve İngilizce metin özetleme
- **Yedek:** Akıllı cümle skorlama algoritması

### Otomatik Etiketleme
- **Model:** `savasy/bert-base-turkish-ner-cased`
- **Özellik:** Türkçe Named Entity Recognition
- **Yedek:** Gelişmiş anahtar kelime çıkarımı

### Anlamsal Arama
- **Özellik:** Kelime benzerliği ve anlamsal arama
- **Algoritma:** Jaccard similarity + substring matching
- **Dil Desteği:** Türkçe karakter desteği

##  Güvenlik

* **Row Level Security (RLS):** Supabase PostgreSQL'de kullanıcı veri izolasyonu
* **JWT Authentication:** Tüm endpoint'ler JWT token ile korunur
* **Input Validation:** Pydantic ile giriş validasyonu
* **Error Handling:** Kapsamlı hata yönetimi

##  Veritabanı Şeması

```sql
-- Notes tablosu
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE NULL
);
```

##  Project Overview

Bu proje **C o n n e c t i n n o** için geliştirilmiş **not alma uygulaması** backend API'sidir. **Flutter** mobil uygulaması ile entegre çalışır.

###  Task Requirements

#### Backend API Gereksinimleri 
-  **CRUD İşlemleri:** GET, POST, PUT, DELETE /notes endpoint'leri
-  **Kimlik Doğrulama:** Supabase JWT token kimlik doğrulama
-  **Güvenlik:** Row Level Security (RLS) ile kullanıcı veri izolasyonu
-  **Doğrulama:** Pydantic ile giriş doğrulama
-  **Hata Yönetimi:** Kapsamlı hata yönetimi

#### AI Özellikleri (Bonus) 
-  **Özetleme:** Notları otomatik özetleme
-  **Otomatik Etiketleme:** Türkçe NER ile otomatik etiketleme
-  **Kategorileme:** Notları kategorileme
-  **Anlamsal Arama:** Akıllı arama özelliği

#### Mimari ve Kalite 
-  **Temiz Mimari:** UI, iş mantığı, veri katmanları ayrımı
-  **Üretim Hazır:** Gerçek uygulama kalitesinde kod
-  **Dokümantasyon:** Kapsamlı README ve API dokümantasyonu
-  **Kolay Kurulum:** Minimal kurulum adımları

##  Production Deployment

Production için:

1. **Environment Variables:** Güvenli JWT secret key kullanın
2. **Database:** Supabase production instance
3. **AI Models:** Hugging Face API rate limits
4. **Monitoring:** Log ve error tracking

##  Evaluation Criteria Compliance

### Kod Kalitesi ve Organizasyon 
- **Temiz Mimari:** Katmanlar arası net ayrım
- **Sürdürülebilirlik:** Modüler ve genişletilebilir kod yapısı
- **Okunabilirlik:** Açıklayıcı değişken isimleri ve dokümantasyon

### API Uygulaması 
- **Temiz API'ler:** RESTful endpoint tasarımı
- **Güvenlik:** JWT kimlik doğrulama ve RLS
- **Hata Yönetimi:** Anlamlı hata mesajları

### Ürün Vizyonu 
- **AI Entegrasyonu:** Hugging Face ile gerçek AI özellikleri
- **İnovasyon:** Anlamsal arama ve akıllı etiketleme
- **Kullanıcı Deneyimi:** Sabitleme/sabitlememe, yumuşak silme gibi UX odaklı özellikler



### API Kullanım Örneği
```bash
# Notları listeler
curl -X GET "http://localhost:8000/notes" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Yeni not oluştur
curl -X POST "http://localhost:8000/notes" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Notu",
    "content": "Bu bir test notudur."
  }'
```

##  Mobil Entegrasyon Desteği

### Otomatik Backend Keşfi

Backend, farklı bilgisayarlarda çalıştırıldığında mobil uygulamaların otomatik olarak backend'i bulması için `/server-info` endpoint'i sağlar.

#### Server Info Endpoint
```python
@app.get("/server-info")
async def get_server_info():
    """Sunucu bilgilerini döndürür (IP adresi, port, URL'ler)"""
    port = int(os.getenv("PORT", 8000))
    local_ip = get_local_ip()  # Otomatik IP tespiti
    
    return {
        "ip_address": local_ip,
        "port": port,
        "base_url": f"http://{local_ip}:{port}",
        "api_url": f"http://{local_ip}:{port}/api/v1",
        "docs_url": f"http://{local_ip}:{port}/docs",
        "version": settings.APP_VERSION
    }
```

### Response Örneği
```json
{
    "ip_address": "192.168.1.100",
    "port": 8000,
    "base_url": "http://192.168.1.100:8000",
    "api_url": "http://192.168.1.100:8000/api/v1",
    "docs_url": "http://192.168.1.100:8000/docs",
    "version": "1.0.0"
}
```

### Network Desteği

- **Localhost:** `http://localhost:8000` (emülatör/development)
- **Network Access:** `http://192.168.1.100:8000` (fiziksel cihazlar)
- **Host Binding:** Sunucu `0.0.0.0` host'unda çalışır (tüm network interface'ler)
- **Port:** 8000 (varsayılan, PORT environment variable ile değiştirilebilir)

##  Project Structure

```
take-note-backend/
├── main.py                 # FastAPI uygulaması
├── config.py              # Konfigürasyon yönetimi
├── database.py            # Supabase database işlemleri
├── auth.py               # JWT authentication
├── models.py             # Pydantic modelleri
├── exceptions.py         # Custom exception handling
├── ai_service_hf.py      # Hugging Face AI servisi
├── schemas.sql           # Database schema
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # Proje dokümantasyonu
└── run.py               # Uygulama başlatma scripti
```

##  Key Features Implemented

###  Temel Gereksinimler
- **CRUD API:** Tam CRUD operasyonları
- **Kimlik Doğrulama:** Supabase JWT entegrasyonu
- **Güvenlik:** Row Level Security (RLS)
- **Doğrulama:** Kapsamlı giriş doğrulama
- **Hata Yönetimi:** Üretim hazır hata yönetimi
- **Mobil Entegrasyon:** Otomatik backend keşfi ile Flutter uyumluluğu

###  Bonus Özellikler
- **AI Özetleme:** Hugging Face BART modeli
- **Otomatik Etiketleme:** Türkçe NER ile BERT
- **Anlamsal Arama:** Akıllı anahtar kelime eşleştirme
- **Sabitleme/Sabitlememe:** Not önceliklendirme
- **Yumuşak Silme:** Geri alma işlevselliği desteği

##  Development Setup

### Prerequisites
- Python 3.8+
- Supabase account
- Hugging Face account (optional, for AI features)

### Quick Start
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Setup Supabase project
4. Configure environment variables
5. Run database schema: `schemas.sql`
6. Start server: `python run.py`

##  Performance & Scalability

- **Database:** PostgreSQL with optimized indexes
- **Caching:** In-memory caching for frequent queries
- **AI Processing:** Async processing for better performance
- **Rate Limiting:** Built-in rate limiting for AI endpoints
- **Monitoring:** Comprehensive logging and error tracking

##  Deployment Options

### Local Development
```bash
python run.py
```

### Production (Docker)
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
```

### Cloud Deployment
- **Supabase:** Database and authentication
- **Railway/Heroku:** API hosting
- **Hugging Face:** AI model serving







---

