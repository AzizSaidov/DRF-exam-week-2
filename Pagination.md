 # Django REST Framework — Function-Based Views Guide

> Filtering · Search · Pagination

---

## 📌 Table of Contents

- [Filtering](#filtering)
  - [Built-in Filtering](#built-in-filtering)
  - [Custom Filter Function](#custom-filter-function)
- [Search](#search)
  - [Built-in Search](#built-in-search)
  - [Custom Search](#custom-search)
- [Pagination](#pagination)
  - [Custom Pagination Class](#custom-pagination-class)
  - [FBV with Custom Pagination](#fbv-with-custom-pagination)

---

## Filtering

### Built-in Filtering

Filter a queryset in FBV by accessing query parameters via `request.GET`.

```python
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
def product_list(request):
    queryset = Product.objects.all()

    # Example: /products/?category=Electronics
    category = request.GET.get('category')
    if category:
        queryset = queryset.filter(category__name=category)

    serializer = ProductSerializer(queryset, many=True)
    return Response(serializer.data)
```

**How it works:**

- `request.GET.get('category')` — retrieves the `category` parameter from the URL
- `queryset.filter(category__name=category)` — filters products by category name
- No extra packages required

---

### Custom Filter Function

Create a separate `filters.py` file with a reusable price filter:

```python
# filters.py

def price_filter(queryset, params):
    """
    Custom filter for minimum and maximum price.
    """
    min_price = params.get('min_price')
    max_price = params.get('max_price')

    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)

    return queryset
```

Use it in your view:

```python
# views.py
from .filters import price_filter

@api_view(['GET'])
def product_list(request):
    queryset = Product.objects.all()

    queryset = price_filter(queryset, request.GET)

    serializer = ProductSerializer(queryset, many=True)
    return Response(serializer.data)
```

**How it works:**

- `price_filter` receives the full queryset and request parameters
- Filters by `min_price` and `max_price` if they are provided
- Returns the filtered queryset, which is then serialized and returned as JSON

---

## Search

### Built-in Search

For FBV, manually filter using the `search` query parameter:

```python
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
def product_search(request):
    queryset = Product.objects.all()

    # Example: /products/?search=iphone
    query = request.GET.get('search')
    if query:
        queryset = queryset.filter(name__icontains=query)

    serializer = ProductSerializer(queryset, many=True)
    return Response(serializer.data)
```

> 💡 For CBV, DRF supports `SearchFilter` out of the box. For FBV, filtering is done manually.

---

### Custom Search

Search across **multiple fields** (e.g., `name` and `description`) using Django's `Q` objects:

```python
# filters.py
from django.db.models import Q

def search_filter(queryset, params):
    """
    Custom search in name and description fields.
    """
    query = params.get('search')
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return queryset
```

Use it in your view:

```python
# views.py
from .filters import search_filter

@api_view(['GET'])
def product_search(request):
    queryset = Product.objects.all()

    queryset = search_filter(queryset, request.GET)

    serializer = ProductSerializer(queryset, many=True)
    return Response(serializer.data)
```

**Example request:**

```
GET /products/?search=iphone
```

**How it works:**

- `Q(name__icontains=query) | Q(description__icontains=query)` — searches both fields simultaneously
- Returns the filtered queryset serialized as JSON

---

## Pagination

Pagination splits large datasets into smaller **pages**, improving performance and user experience.

**Example request:**

```
GET /products/?page=2&size=10
```

Returns the **second page** with **10 items per page**.

**Benefits:**
- ✅ Faster responses
- ✅ Less data per request
- ✅ Easier navigation for clients

---

### Custom Pagination Class

```python
# pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 5                   # Default: 5 items per page
    page_size_query_param = 'size'  # Client can override via ?size=10
    max_page_size = 50              # Hard cap: never return more than 50

    def get_paginated_response(self, data):
        return Response({
            'total_items': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })
```

| Parameter | Description |
|-----------|-------------|
| `page_size` | Default number of items per page |
| `page_size_query_param` | Allows client to set page size dynamically |
| `max_page_size` | Maximum items per page (prevents overloading) |
| `get_paginated_response` | Customizes the JSON response structure |

---

### FBV with Custom Pagination

```python
# views.py
from .pagination import CustomPagination

@api_view(['GET'])
def product_list(request):
    queryset = Product.objects.all()

    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    serializer = ProductSerializer(paginated_queryset, many=True)
    return paginator.get_paginated_response(serializer.data)
```

**Example request:**

```
GET /products/?page=2&size=10
```

- `page=2` — second page
- `size=10` — 10 items per page (overrides the default of 5)

**Example response:**

```json
{
  "total_items": 23,
  "total_pages": 3,
  "current_page": 2,
  "results": [
    { "id": 11, "name": "Product 11" },
    { "id": 12, "name": "Product 12" },
    { "id": 13, "name": "Product 13" }
  ]
}
```

---

*DRF Function-Based Views Guide — Filtering · Search · Pagination*