
````md
# 🔐 Permissions in Django REST Framework (DRF)

Permissions define **who can access an API endpoint and what actions they can perform**.

They are checked **after authentication** and **before the view logic runs**.

---

## ✅ Step 1 — What are Permissions in DRF?

Permissions control access to API endpoints.

Example:
- Two users are logged in
- Only one of them is allowed to edit data

DRF provides **built-in permission classes** and also allows creating **custom permissions**.

---

## ✅ Step 2 — Built-in Permission Classes

### 🔹 1. `AllowAny`

Everyone can access the endpoint — even unauthenticated users.

```python
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

class PublicView(APIView):
    permission_classes = [AllowAny]
````

✔ Use for:

* Login
* Register
* Public pages

---

### 🔹 2. `IsAuthenticated`

Only authenticated users can access the view.

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class PrivateView(APIView):
    permission_classes = [IsAuthenticated]
```

✔ Use when login is required.

---

### 🔹 3. `IsAdminUser`

Only admin/staff users (`is_staff=True`) can access.

```python
from rest_framework.permissions import IsAdminUser

class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]
```

✔ Good for:

* Admin dashboards
* Management APIs

---

### 🔹 4. `IsAuthenticatedOrReadOnly`

Unauthenticated users can **read**, but only authenticated users can **modify**.

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class PostView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
```

✔ Rules:

* `GET` ✅ everyone
* `POST / PUT / DELETE` ❌ only logged-in users

✔ Typical for:

* Blogs
* Comments
* Product lists

---

## ✅ Step 3 — Set Default Permission (Optional)

You can define a global default permission in `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}
```

If not set, DRF uses:

```python
AllowAny
```

by default.

---

## ✅ Step 4 — Apply Permissions to ViewSets / Generic Views

### Example with `ModelViewSet`

```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
```

---

## ✅ Step 5 — Mix Multiple Permissions

```python
class MyView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
```

⚠️ **All permissions must return `True`** to allow access.

---

## ✅ Step 6 — Permissions Based on HTTP Method

If different rules are needed for different methods:

```python
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

class MixedView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
```

---

# 🛠 Custom Permissions in DRF

---

## ✅ Step 1 — Import `BasePermission`

All custom permissions must extend `BasePermission`.

```python
from rest_framework.permissions import BasePermission
```

---

## ✅ Step 2 — Permission Methods

### 🔹 1. `has_permission(self, request, view)`

Runs **before accessing any object**.

Used for:

* Authentication checks
* HTTP method restrictions
* Role/group-based access

---

### 🔹 2. `has_object_permission(self, request, view, obj)`

Runs **after the object is retrieved**.

Used for:

* Ownership checks
* Field-based restrictions
* Status checks

You can override **one or both**.

---

## ✅ Example 1 — Only the Owner Can Access

```python
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
```

Usage:

```python
class ProductDetailView(APIView):
    permission_classes = [IsOwner]

    def get_object(self):
        return Product.objects.get(pk=self.kwargs['pk'])
```

---

## ✅ Example 2 — Owner Can Edit, Others Can Only View

```python
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.owner == request.user
```

✔ Everyone can `GET`
✔ Only the owner can `PUT / PATCH / DELETE`

---

## ✅ Example 3 — Only Users from a Specific Group

```python
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.groups.filter(name='manager').exists()
        )
```

Usage:

```python
class EmployeeListView(APIView):
    permission_classes = [IsManager]
```

---

## ✅ Example 4 — Read-Only Permission

```python
class ReadOnlyPermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')
```

---

## ✅ Example 5 — Combined Permission Logic

```python
class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        # Only authenticated users can access GET
        if request.method == 'GET':
            return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        # Only the owner can modify the object
        return obj.owner == request.user
```

---

## ✅ Step 3 — Applying Custom Permissions

### In `APIView`

```python
class MyView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
```

---

### In `ViewSet`

```python
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]
```

---

## ✅ Step 4 — Mix Built-in + Custom Permissions

```python
class ProductView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
```

---

## 🧠 Summary

* Permissions run **after authentication**
* `has_permission` → access to the view
* `has_object_permission` → access to the object
* Keep access logic **inside permissions**, not views

---

🚀 **Clean permissions = clean architecture**

 
