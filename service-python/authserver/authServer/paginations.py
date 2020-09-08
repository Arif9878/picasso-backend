from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 10

class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        totalPage = round(self.page.paginator.count / int(self.request.GET.get('page_size', self.page_size)))
        return Response({
            'results': data,
            '_meta': {
                'totalCount': self.page.paginator.count,
                'totalPage': totalPage,
                'currentPage': int(self.request.GET.get('page', DEFAULT_PAGE)),
                'pageSize': int(self.request.GET.get('page_size', self.page_size)),
            }
        })