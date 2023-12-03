from .models import SubCatalog


def custom_context_processor(request):
    context = {'catalogs': SubCatalog.objects.filter(author=request.user.pk)}
    # следующий код позволяет избежать возврата в изначальный список при возврате после поиска и открытия деталей урока
    context['keyword'] = ''
    context['all'] = ''
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context['keyword']
    if 'page' in request.GET:
        page = request.GET['page']
        if page != '1':
            if context['all']:
                context['all'] += '&page=' + page
            else:
                context['all'] = '?page=' + page
    return context