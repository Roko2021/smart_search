## 📡 أمثلة API

### 1. البحث عن المنتجات
**Endpoint**:  
`GET /api/search/?q={query}&lang={ar|en}`

**المعلمات**:
- `q` (مطلوب): كلمة البحث
- `lang` (اختياري): لغة البحث (`ar` أو `en`)، الإفتراضي: `en`

**أمثلة**:

```bash
# بحث بالعربية
curl -X GET "http://localhost:8000/api/search/?q=بروتين&lang=ar"

# بحث بالإنجليزية
curl -X GET "http://localhost:8000/api/search/?q=protein&lang=en"

# بدون تحديد لغة (ستستخدم الإنجليزية افتراضيًا)
curl -X GET "http://localhost:8000/api/search/?q=energy"
