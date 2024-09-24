from django.urls import path

from .helpers.constants import PageNames
from .views import *

from .views.month import MonthView

urlpatterns = [
    path('', EntryPointView.as_view(), name=PageNames.ENTRY_POINT),
    path('login/', LoginView.as_view(), name=PageNames.USER_LOGIN),
    path('<str:month>', MonthView.as_view(), name='month'),
]
