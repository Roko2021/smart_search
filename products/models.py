from django.db import models
from django.contrib.postgres.search import SearchVectorField

class Product(models.Model):
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    calories = models.IntegerField()
    search_vector = SearchVectorField(null=True)  # أضف هذا الحقل الجديد

    class Meta:
        app_label = 'products'

    def __str__(self):
        return self.name_en

class MyFile(models.Model):
    file = models.FileField(upload_to='uploads/')