# 📦 Malzeme Yönetim Sistemi - Mikro Hizmet Mimarisi

Bu proje, bulut bilişim standartlarına uygun olarak tasarlanmış, üç bağımsız mikro hizmetten oluşan bir arka uç (backend) uygulamasıdır. Geleneksel monolitik yapıların aksine, sistemin her bir bileşeni kendi izole Docker konteynerinde çalışacak şekilde yapılandırılmıştır.

##  Sistem Mimarisi (Mikro Hizmetler)

Uygulama, `docker-compose` ile orkestre edilen aşağıdaki servislerden oluşmaktadır:

1. **Backend (FastAPI):** Sistemin ana motoru ve API Gateway'idir. İş mantığını yürütür ve diğer servislerle iletişimi sağlar.
2. **Database (PostgreSQL):** Kullanıcı, malzeme ve sistem verilerini ilişkisel olarak saklayan veri katmanıdır.
3. **Storage (MinIO):** Görseller ve 3D modeller gibi yapılandırılmamış büyük dosyaları barındıran, S3 uyumlu nesne depolama servisidir.

##  Kurulum ve Çalıştırma

Projenin bilgisayarınızda veya herhangi bir bulut sunucusunda çalışabilmesi için **Docker** ve **Docker Compose** yüklü olmalıdır.

### Adım 1: Projeyi Başlatma
Terminal veya komut satırını açarak proje ana dizinine gidin ve aşağıdaki komutu çalıştırın:

```bash
docker-compose up --build -d
```

###  Adım 2: Servislere Erişim
Sistem ayağa kalktıktan sonra aşağıdaki bağlantılar üzerinden servislere erişebilirsiniz:

Ana Uygulama (Vitrin): http://localhost:8000

API Dokümantasyonu (Swagger UI): http://localhost:8000/docs

MinIO Depolama Paneli: http://localhost:9001
### Adım 3: Sistemi Durdurma
Sistemi kapatmak ve konteynerleri durdurmak için şu komutu çalıştırabilirsiniz:
docker-compose down
# 📁 Proje Dizin Yapısı
```bash
.
├── backend/            # FastAPI kaynak kodları ve Dockerfile
│   ├── main.py         # Ana API yönlendirmeleri
│   ├── models.py       # Veritabanı şemaları
│   ├── requirements.txt# Python bağımlılıkları
│   └── static/         # Frontend HTML/CSS dosyaları
├── db/                 # PostgreSQL sarmalayıcı Dockerfile
├── minio/              # MinIO sarmalayıcı Dockerfile
├── docker-compose.yml  # Servis orkestrasyon dosyası
└── README.md           # Proje dökümantasyonu
```
