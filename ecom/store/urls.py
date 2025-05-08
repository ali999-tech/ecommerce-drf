from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, OrderViewSet, HomePageView, RegisterView, LoginFaceView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('orders', OrderViewSet)

urlpatterns = [
    path('', LoginFaceView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('home/', HomePageView.as_view(), name='home'),
    path('api/', include(router.urls)),
]
