import django_filters
from .models import StockLog

class StockLogFilter(django_filters.FilterSet):
    """Filter stock logs by product, change type, specific date, and date range."""

    product = django_filters.NumberFilter(field_name="product__id", lookup_expr="exact")
    change_type = django_filters.CharFilter(field_name="change_type", lookup_expr="iexact")  # Case-insensitive
    specific_date = django_filters.DateFilter(field_name="timestamp", lookup_expr="date")  # Filter by exact date
    start_date = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")  # Greater than or equal to (>=)
    end_date = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte") # Less than or equal to (<=)

    class Meta:
        model = StockLog
        fields = ["product", "change_type", "specific_date", "start_date", "end_date"]

"""Routes"""
# http://localhost:8000/products/stock-logs/?product=1
# http://localhost:8000/products/stock-logs/?change_type=Stock%20Added
# http://localhost:8000/products/stock-logs/?date_from=2025-02-20&date_to=2025-02-20
# http://localhost:8000/products/stock-logs/?change_type=Stock%20Added&date_from=2025-02-20&date_to=2025-02-20
# 
