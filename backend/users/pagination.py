from rest_framework.pagination import PageNumberPagination
from backend.settings import PAGE_SIZE


class LimitPagePagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
