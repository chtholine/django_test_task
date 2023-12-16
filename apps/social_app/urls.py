from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, UserActivityViewSet, LogoutAPIView, SignUpAPIView, LoginAPIView, UserViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('signup/', SignUpAPIView.as_view(), name='signup'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='login'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
