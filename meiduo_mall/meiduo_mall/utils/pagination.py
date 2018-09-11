from rest_framework.pagination import PageNumberPagination


class LargeResultsSetPagination(PageNumberPagination):
    """自定义分页后端"""
    # 指定每页最小数据条数
    page_size = 2

    # 指定接受每页条数的字段
    page_size_query_param = 'page_size'

    # 指定每页最大数据条数
    max_page_size = 20
