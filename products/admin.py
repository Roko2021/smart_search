from django.contrib import admin
from .models import Product, MyFile  # استبدل Product بنموذجك الفعلي

admin.site.register(Product)  # سجل النموذج هنا
admin.site.register(MyFile)  # سجل النموذج هنا