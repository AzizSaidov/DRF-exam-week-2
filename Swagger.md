
---

# 📘 Swagger (OpenAPI) для Django REST Framework — Полная Настройка

Это руководство показывает, как подключить **Swagger UI** и **Redoc** в Django REST Framework с помощью **drf-yasg**.

---

## ✅ **Шаг 1. Установка**

```bash
pip install drf-yasg
```

---

## ✅ **Шаг 2. Добавить в `INSTALLED_APPS` и настройки**

Открой `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'drf_yasg',
]

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'TokenAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }
}
```

---

## ✅ **Шаг 3. Создать Swagger Schema в `urls.py`**

Открой основной `urls.py`:

```python
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
```

---

## ✅ **Шаг 4. Добавить маршруты Swagger + Redoc**

В том же `urls.py`:

```python
urlpatterns = [
     

    # Swagger UI
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),

    # ReDoc
    re_path(
        r'^redoc/$',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
```

---

## ✅ **Шаг 5. Добавить документацию к API методам**

### GET

```python
@swagger_auto_schema(
    method='get',
    responses={200: ItemSerializer(many=True)}
)
```

### POST

```python
@swagger_auto_schema(
    method='post',
    request_body=ItemSerializer,
    responses={201: "Created", 400: "Validation error"}
)
```

### PUT

```python
@swagger_auto_schema(
    method='put',
    request_body=ItemSerializer,
    responses={
        200: ItemSerializer(),
        204: "Not found",
        400: "Validation error"
    }
)
```

---

## ✅ **Шаг 6. Запустить сервер**

```bash
python manage.py runserver
```

---

## 🚀 **Готово!**

Теперь Swagger доступен по адресу:

➡️ **[http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)**
➡️ **[http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)**

---

