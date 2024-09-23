from django.urls import path
from .views.month import MonthView
from .views.login_view import LoginView
from .views.load_pages_view import LoadPagesView

urlpatterns = [
    path('', LoadPagesView.as_view(), name='load_pages'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('<str:month>', MonthView.as_view(), name='month'),
]
