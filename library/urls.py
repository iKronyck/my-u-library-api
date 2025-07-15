from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, RegisterUserView, MagicLoginView, ResendMagicLinkView

router = DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('magic-login/', MagicLoginView.as_view(), name='magic-login'),
    path('resend-magic-link/', ResendMagicLinkView.as_view(), name='resend-magic-link')
]
