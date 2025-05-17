from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from difflib import get_close_matches
import googletrans

translator = googletrans.Translator()

def advanced_search(query, lang='en'):
    # الترجمة الآلية للاستعلامات
    if lang != 'en':
        translated = translator.translate(query, dest='en').text
    else:
        translated = query
    
    # البحث الضبابي باستخدام PostgreSQL
    vector = SearchVector('name_en', 'name_ar', weight='A') + \
             SearchVector('description_en', 'description_ar', weight='B')
    
    search_query = SearchQuery(translated, search_type='websearch')
    results = Product.objects.annotate(
        rank=SearchRank(vector, search_query)
    ).filter(rank__gte=0.3).order_by('-rank')
    
    # دعم الأخطاء الإملائية
    if len(results) < 5:
        all_names = list(Product.objects.values_list('name_en', flat=True))
        close_matches = get_close_matches(query, all_names, n=3, cutoff=0.6)
        close_results = Product.objects.filter(name_en__in=close_matches)
        results = results | close_results
    
    return results.distinct()