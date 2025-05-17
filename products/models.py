from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex,BTreeIndex

class Product(models.Model):
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    description_en = models.TextField()
    description_ar = models.TextField()
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    nutritional_info = models.TextField()
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        indexes = [
            BTreeIndex(fields=['name_en']),  # استبدل GinIndex بـ BTreeIndex
            BTreeIndex(fields=['name_ar']),
            BTreeIndex(fields=['brand']),
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return self.name_en

class MyFile(models.Model):
    file = models.FileField(upload_to='uploads/')