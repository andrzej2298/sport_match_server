from rest_framework.pagination import PageNumberPagination


class ResultPagination(PageNumberPagination):
    page_size = 30
