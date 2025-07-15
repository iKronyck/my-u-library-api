from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, RegisterUserView, MagicLoginView, ResendMagicLinkView, UserViewSet, BookLoanViewSet, LoanBookView, DashboardStatsView, ReturnBookView, MarkBookAsLostView, MyLoansView, ActivityFeedView

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'users', UserViewSet)
router.register(r'loans', BookLoanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('magic-login/', MagicLoginView.as_view(), name='magic-login'),
    path('resend-magic-link/', ResendMagicLinkView.as_view(), name='resend-magic-link'),
    path('loan-book/', LoanBookView.as_view(), name='loan-book'),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('loans/<uuid:loan_id>/return/', ReturnBookView.as_view(), name='return-book'),
    path('loans/<uuid:loan_id>/mark-lost/', MarkBookAsLostView.as_view(), name='mark-lost'),
    path('my-loans/', MyLoansView.as_view(), name='my-loans'),
    path('activity-feed/', ActivityFeedView.as_view(), name='activity-feed')
]
