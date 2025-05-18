from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex,BTreeIndex, Index


class Product(models.Model):
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    description_en = models.TextField()
    description_ar = models.TextField()
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        indexes = [
            GinIndex(
                fields=['name_ar'],
                name='name_ar_gin_idx',
                opclasses=['gin_trgm_ops']
            ),
            GinIndex(
                fields=['name_en'],
                name='name_en_gin_idx',
                opclasses=['gin_trgm_ops']
            ),
            Index(
                fields=['name_ar'],
                name='name_ar_prefix_idx',
                opclasses=['varchar_pattern_ops']
            ),
            Index(
                fields=['name_en'],
                name='name_en_prefix_idx',
                opclasses=['varchar_pattern_ops']
            ),
            GinIndex(fields=['search_vector'])
        ]

    def __str__(self):
        return self.name_en

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_search_vector()

    def update_search_vector(self):
        from django.contrib.postgres.search import SearchVector
        Product.objects.filter(pk=self.pk).update(
            search_vector=(
                SearchVector('name_ar', weight='A', config='arabic') +
                SearchVector('description_ar', weight='B', config='arabic') +
                SearchVector('name_en', weight='A', config='english') +
                SearchVector('description_en', weight='B', config='english')
            )
        )

    # def __str__(self):
    #     return self.name_en

class MyFile(models.Model):
    file = models.FileField(upload_to='uploads/')