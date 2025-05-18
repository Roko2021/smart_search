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
from django.db.models.functions import Greatest,Length
from django.conf import settings

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
        lang = request.GET.get('lang', 'both').lower()  # 'ar', 'en', or 'both'

        # إعدادات البحث
        MIN_CHARS = getattr(settings, 'SEARCH_MIN_CHARS', 2)
        SIMILARITY_THRESHOLD = getattr(settings, 'SEARCH_SIMILARITY_THRESHOLD', 0.1)

        if len(query) < MIN_CHARS:
            return Response({
                'error': f'Search term too short. Minimum {MIN_CHARS} characters required.'
            }, status=400)

        cache_key = f"product_search:{lang}:{query}"
        cached_results = cache.get(cache_key)
        if cached_results:
            return Response(json.loads(cached_results))

        try:
            products = self.search_products(query, lang, SIMILARITY_THRESHOLD)
            serializer = ProductSerializer(products, many=True)
            
            response_data = {
                'query': query,
                'count': products.count(),
                'results': serializer.data
            }
            
            cache.set(cache_key, json.dumps(response_data), 3600)  # Cache for 1 hour
            return Response(response_data)

        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            return Response({'error': 'Search failed'}, status=500)

    def search_products(self, query, lang, threshold):
        vector = (
            SearchVector('name_ar', weight='A', config='arabic') +
            SearchVector('description_ar', weight='B', config='arabic') +
            SearchVector('name_en', weight='A', config='english') +
            SearchVector('description_en', weight='B', config='english')
        )
        
        search_query = SearchQuery(query)
        similarity_ar = TrigramSimilarity('name_ar', query)
        similarity_en = TrigramSimilarity('name_en', query)

        qs = Product.objects.annotate(
            search=vector,
            rank=SearchRank(vector, search_query),
            similarity=Greatest(similarity_ar, similarity_en),
            name_length=Length('name_en')
        )

        # فلترة حسب اللغة
        if lang == 'ar':
            qs = qs.filter(Q(name_ar__trigram_similar=query) | Q(similarity__gt=threshold))
        elif lang == 'en':
            qs = qs.filter(Q(name_en__trigram_similar=query) | Q(similarity__gt=threshold))
        else:  # both
            qs = qs.filter(
                Q(name_ar__trigram_similar=query) |
                Q(name_en__trigram_similar=query) |
                Q(similarity__gt=threshold)
            )

        return qs.order_by('-similarity', '-rank')[:20]