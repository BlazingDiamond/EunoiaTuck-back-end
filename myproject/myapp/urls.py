# myapp/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileListCreate,
    UserProfileDetail,
    PostViewSet,
    RegisterView,
    LoginView,
    ProductViewSet,
)
from myapp import views

# python manage.py runserver 192.168.0.44:8081
router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    # path('products/', ProductViewSet.as_view({'get': 'list'}), name='product-list'),
    path(
        "userprofiles/", UserProfileListCreate.as_view(), name="userprofile-list-create"
    ),
    path(
        "userprofiles/<int:pk>/", UserProfileDetail.as_view(), name="userprofile-detail"
    ),
    path("products/", views.ProductsListView.as_view(), name="product-list"),
    path(
        "account/",
        views.AccountViewSet.as_view(),
        name="accounts",
    ),
]
