# 🚀 Smart Search API

تطبيق بحث ذكي للمنتجات باستخدام Django وPostgreSQL مع دعم البحث متعدد اللغات والبحث التقريبي.

## 🔍 مميزات النظام
- بحث سريع بدعم PostgreSQL Full-Text Search
- دعم اللغتين العربية والإنجليزية
- تحسين أداء البحث باستخدام Trigram Similarity
- تخزين مؤقت للنتائج (Caching)
- مصادقة باستخدام JWT
- تحديد معدل الطلبات (Rate Limiting)

## 🛠️ متطلبات التشغيل
- Python 3.10+
- PostgreSQL 14+
- Django 4.2+
- Django REST Framework

## 🚀 إعداد البيئة

psql -U postgres -c "CREATE DATABASE miran_fitness;"
psql -U postgres -d miran_fitness -c "CREATE EXTENSION pg_trgm;"


## تشغيل الميجراشن
python manage.py migrate

# بحث بالعربية
curl -X GET "http://localhost:8000/api/search/?q=بروتين&lang=ar"

# بحث بالإنجليزية
curl -X GET "http://localhost:8000/api/search/?q=protein&lang=en"

##بحث باستخدام توكن 

curl -X POST "http://localhost:8000/api/token/" \
-H "Content-Type: application/json" \
-d '{"username":"admin", "password":"admin123"}'
##استخدام التوكن 
curl -X GET "http://localhost:8000/api/search/?q=بروتين" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

### 1. تثبيت المتطلبات:
```bash
pip install -r requirements.txt
