from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
import Levenshtein
from django.db.models import Q, Func
from rest_framework.throttling import UserRateThrottle
import logging
from django.core.cache import cache
import json

logger = logging.getLogger(__name__)

class LevenshteinDistance(Func):
    function = 'LEVENSHTEIN'

class SearchThrottle(UserRateThrottle):
    rate = '100/hour'

class ProductSearchAPI(APIView):
    throttle_classes = [SearchThrottle]
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        lang = request.GET.get('lang', '').lower()
        
        # التحقق من صحة المدخلات
        if not query:
            return Response({'error': 'كلمة البحث مطلوبة'}, status=400)
        
        if len(query) < 2:
            return Response({'error': 'كلمة البحث قصيرة جدًا (يجب ألا تقل عن حرفين)'}, status=400)

        # التحقق من التخزين المؤقت
        cache_key = f"search:{lang}:{query}"
        cached_results = cache.get(cache_key)
        if cached_results:
            return Response(json.loads(cached_results))

        try:
            # الطريقة 1: Full-Text Search مع Trigram لتحسين الدقة
            search_config = 'arabic' if lang == 'ar' else 'english'
            search_query = SearchQuery(query, config=search_config)
            
            products = Product.objects.annotate(
                similarity=TrigramSimilarity('name_ar', query) + 
                TrigramSimilarity('name_en', query),
                rank=SearchRank('search_vector', search_query)
            ).filter(
                Q(search_vector=search_query, rank__gte=0.1) |
                Q(similarity__gt=0.3)
            ).order_by('-rank', '-similarity')[:20]

            # إذا لم توجد نتائج، جرب البحث التقريبي
            if not products.exists():
                products = self.fallback_search(query, lang)

            serializer = ProductSerializer(products, many=True)
            response_data = {
                'query': query,
                'search_type': 'full-text' if products.exists() else 'fuzzy-match',
                'count': products.count(),
                'results': serializer.data
            }

            # تخزين النتائج في الكاش لمدة ساعة
            cache.set(cache_key, json.dumps(response_data), 3600)
            return Response(response_data)

        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            return Response({'error': 'حدث خطأ أثناء البحث'}, status=500)

    def fallback_search(self, query, lang):
        """بحث احتياطي عند فشل البحث الأساسي"""
        try:
            # البحث بالتشابه اللغوي
            products = Product.objects.annotate(
                distance=LevenshteinDistance('name_ar', query)
            ).filter(
                Q(distance__lte=3) | 
                Q(name_ar__icontains=query) |
                Q(name_en__icontains=query)
            ).order_by('distance')[:10]

            if not products.exists():
                # إذا لم توجد نتائج، جرب بحث أوسع
                all_products = Product.objects.all()
                products = sorted(
                    all_products,
                    key=lambda p: min(
                        Levenshtein.distance(query, p.name_ar or ""),
                        Levenshtein.distance(query, p.name_en or "")
                    )
                )[:5]

            return products

        except Exception as e:
            logger.error(f"Fallback search error: {str(e)}")
            return Product.objects.none()