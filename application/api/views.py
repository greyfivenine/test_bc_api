from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 200


class PaginatedResponseMixin:
    """
    Интерфейс (миксин) для организации необходимого окружения представления API для постраничного вывода.
    """
    pagination_class = StandardResultsSetPagination

    def get_paginated_ads_response(self, queryset, custom_serializer_class=None, *args, **kwargs):
        context = kwargs.get('context', {})
        context['request'] = self.request

        page = self.paginate_queryset(queryset) or queryset

        serializer_class = custom_serializer_class or self.get_serializer
        serializer = serializer_class(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)
