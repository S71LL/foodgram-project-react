from rest_framework.pagination import PageNumberPagination

from . import constants


class CustomPaginator(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = constants.PAGE_SIZE
