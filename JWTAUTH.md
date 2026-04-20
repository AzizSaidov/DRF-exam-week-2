 
````md
# Django REST Framework + JWT Authentication

## Installation

```bash
pip install djangorestframework
pip install djangorestframework-simplejwt
````

---

## Configure REST Framework and JWT

### settings.py

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```

---

## Token lifetime configuration (optional)

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

---

## Custom User Model (optional)

### accounts/models.py

```python
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass
```

### settings.py

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
```

---

## Registration Serializer

### accounts/serializers.py

```python
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
```

---

## Authentication Views

### accounts/views.py

```python
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {"detail": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )
```

---

## URLs

### accounts/urls.py

```python
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from .views import RegisterView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
```

---

## Swagger (JWT)

### settings.py

```python
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer <token>"'
        }
    },
    'USE_SESSION_AUTH': False,
}
```

---

## Swagger Authorization Format

```
Bearer <access_token>
```

---

## Enable Token Blacklist (for logout)

```bash
pip install djangorestframework-simplejwt[blacklist]
```

### settings.py

```python
INSTALLED_APPS = [
    ...
    'rest_framework_simplejwt.token_blacklist',
]
```

---

## API Endpoints

| Method | Endpoint                 | Description          |
| ------ | ------------------------ | -------------------- |
| POST   | /api/auth/register/      | Register             |
| POST   | /api/auth/login/         | Get access + refresh |
| POST   | /api/auth/token/refresh/ | Refresh access       |
| POST   | /api/auth/logout/        | Logout               |

 