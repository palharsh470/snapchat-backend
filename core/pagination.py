from rest_framework.pagination import CursorPagination


class SpotlightPagination(CursorPagination):
    page_size = 10
    ordering = "-id"