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
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

class LevenshteinDistance(Func):
    function = 'LEVENSHTEIN'

class SearchThrottle(UserRateThrottle):
    rate = '100/hour'

class ProductSearchAPI(APIView):
    # authentication_classes = [JWTAuthentication]  # يمكن تفعيلها لاحقًا
    # permission_classes = [IsAuthenticated]       # يمكن تفعيلها لاحقًا
    throttle_classes = [SearchThrottle]
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        lang = request.GET.get('lang', 'en').lower()
        
        if not query:
            return Response({'error': 'كلمة البحث مطلوبة'}, status=400)
        
        if len(query) < 2:
            return Response({'error': 'كلمة البحث قصيرة جدًا (يجب ألا تقل عن حرفين)'}, status=400)

        cache_key = f"search:{lang}:{query}"
        cached_results = cache.get(cache_key)
        if cached_results:
            return Response(json.loads(cached_results))

        try:
            # البحث الأولي باستخدام TrigramSimilarity
            products = self.primary_search(query, lang)
            
            # إذا لم توجد نتائج، جرب البحث الثانوي
            if not products.exists():
                products = self.secondary_search(query, lang)
            
            serializer = ProductSerializer(products, many=True)
            response_data = {
                'query': query,
                'count': products.count(),
                'results': serializer.data
            }
            
            cache.set(cache_key, json.dumps(response_data), 3600)
            return Response(response_data)

        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            return Response({'error': 'حدث خطأ أثناء البحث'}, status=500)

    def primary_search(self, query, lang):
        """البحث الأساسي باستخدام TrigramSimilarity"""
        if lang == 'ar':
            return Product.objects.annotate(
                similarity=TrigramSimilarity('name_ar', query)
            ).filter(
                similarity__gt=0.3
            ).order_by('-similarity')[:20]
        else:
            return Product.objects.annotate(
                similarity=TrigramSimilarity('name_en', query)
            ).filter(
                similarity__gt=0.3
            ).order_by('-similarity')[:20]

    def secondary_search(self, query, lang):
        """بحث ثانوي عند فشل البحث الأساسي"""
        if lang == 'ar':
            return Product.objects.filter(
                Q(name_ar__icontains=query) |
                Q(description_ar__icontains=query)
            )[:10]
        else:
            return Product.objects.filter(
                Q(name_en__icontains=query) |
                Q(description_en__icontains=query)
            )[:10]