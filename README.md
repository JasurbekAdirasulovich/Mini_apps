# AI Test Generator

Universitet o'qituvchilari uchun sun'iy intellekt (Gemini API) yordamida fanlar va mavzular bo'yicha professional ko'p variantli testlarni yaratish va eksport qilish tizimi.

---

## 🌟 Imkoniyatlari

- **Tezkor AI Generatsiya:** Fan nomi, mavzular va savollar soni hamda til parametrlari asosida professional testlarni bir zumda shakllantirish.
- **Variantlar (Shuffle Engine):** Talabalar orasida ko'chirish (shpargalka) holatlarini kamaytirish uchun savollar va javob variantlarini aralashtirish orqali alohida variantlar (Variant A, B, C, D...) yaratish.
- **Mukammal Hujjatlar Eksporti:**
  - **Microsoft Word (DOCX):** Har bir variant alohida sahifada boshlanadi.
  - **Adobe PDF (A4):** Chop etishga tayyor, chiroyli va qulay tartib.
  - **Javoblar kaliti (Answer Keys):** Hujjatning oxirgi sahifasida jadval ko'rinishida taqdim etiladi.
- **Offline / Mock Mode:** Gemini API kaliti mavjud bo'lmasa, dastur avtomatik ravishda simulyatsiya rejimiga o'tadi va to'liq tezlikda barcha funksiyalarni ishlatishga imkon beradi.

---

## 📁 Loyiha Tuzilishi (Folder Structure)

```text
AI_Test_Generator/
├── manage.py               # Django loyihani boshqarish skripti
├── requirements.txt        # Kerakli Python kutubxonalari ro'yxati
├── README.md               # Loyiha hujjatlari va yo'riqnoma
├── .env.example            # Muhit o'zgaruvchilari uchun namuna
├── .env                    # Faol muhit o'zgaruvchilari (API key va h.k.)
├── config/                 # Loyiha asosiy sozlamalari
│   ├── settings.py         # Django konfiguratsiyasi (bazasiz, file sessions)
│   ├── urls.py             # Global marshrutlar
│   ├── wsgi.py / asgi.py   # Web server interfeyslari
│   └── __init__.py
└── generator/              # Ilova (App) kodi
    ├── apps.py             # App ro'yxatdan o'tishi
    ├── urls.py             # Ilova marshrutlari
    ├── views.py            # So'rovlarni qayta ishlovchi viewlar
    ├── models.py           # Ma'lumotlar bazasi modellari (bo'sh)
    ├── tests.py            # Avtomatlashtirilgan testlar (Unit Tests)
    ├── services/           # Mustaqil yordamchi modullar
    │   ├── __init__.py
    │   ├── prompt_builder.py   # Professional prompt tayyorlovchi modul
    │   ├── ai_service.py       # Gemini API va Mock xizmati
    │   ├── response_parser.py  # AI matnli javobini tozalovchi va JSONga o'giruvchi modul
    │   ├── json_validator.py   # JSON strukturasi to'g'riligini tekshiruvchi modul
    │   ├── shuffle_engine.py   # Variantlarni aralashtirib beruvchi modul
    │   ├── word_exporter.py    # python-docx orqali Word yaratish
    │   └── pdf_exporter.py     # reportlab orqali PDF yaratish
    ├── templates/
    │   └── generator/
    │       ├── base.html       # Umumiy shablon (Spinner, Header, Footer)
    │       ├── home.html       # Fan/mavzu kiritish bosh sahifasi
    │       ├── preview.html    # Savollarni ko'rib chiqish sahifasi
    │       ├── shuffle.html    # Variantlar yaratish sozlamalari
    │       └── export.html     # Yuklab olish sahifasi
    └── static/
        ├── css/
        │   └── style.css       # Premium, minimalist, responsive CSS
        └── js/
            └── main.js         # JavaScript validatsiya va Loading spinner
```

---

## 🚀 Ishga Tushirish Yo'riqnomasi

### 1. Talablarni o'rnatish
Loyiha jildida virtual muhit yarating va kerakli kutubxonalarni o'rnating:

```bash
pip install -r requirements.txt
```

### 2. Muhit o'zgaruvchilarini sozlash
`.env` faylini oching va o'zgaruvchilarni kiriting:

```env
SECRET_KEY=django-insecure-ai-test-generator-dev-key-2026
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GEMINI_API_KEY=your_gemini_api_key_here
```
*Eslatma: Agar `GEMINI_API_KEY` bo'sh qoldirilsa, tizim avtomatik ravishda lokal simulyatsiya (Mock Mode) rejimida ishlaydi.*

### 3. Serverni ishga tushirish

Lokal serverni ishga tushirish uchun quyidagi buyruqni bering:

```bash
python manage.py runserver
```

Brauzerda [http://127.0.0.1:8000/](http://127.0.0.1:8000/) manziliga kiring.

---

## 🧪 Avtomatlashtirilgan Testlarni Ishga Tushirish

Prompt sozlash, javoblarni tozalash, JSON strukturasi va eksport modullari to'liq qamrab olingan testlarni ishga tushirish uchun:

```bash
python manage.py test
```

Barcha testlar muvaffaqiyatli yakunlanishi kerak (`OK`).

---

## 🏗️ Arxitektura va Dizayn Qarorlari

1. **Ma'lumotlar Bazasisiz Dizayn:** O'qituvchilar ma'lumotlarini keraksiz saqlamaslik va tezkorlik uchun barcha ma'lumotlar foydalanuvchi sessiyasida (Django File Sessions) saqlanadi.
2. **Kengaytiriluvchanlik (Scalability):** `ai_service.py` moduli mustaqil loyihalanib, kelajakda OpenAI yoki DeepSeek kabi boshqa modellarni qo'shish jarayonida tizim arxitekturasini o'zgartirmasdan faqat ushbu modulni to'ldirish imkoniyatini beradi.
3. **Vanilla JS & CSS:** Dasturni yuklash tezligini oshirish va ortiqcha kutubxonalarga tobe bo'lmaslik uchun hech qanday framework (Tailwind, React va h.k.) ishlatilmagan.
