from django.urls import path

from .helpers.constants import PageNames
from .views import *

urlpatterns = [
    path('', EntryPointView.as_view(), name=PageNames.ENTRY_POINT),
    path('login/', LoginView.as_view(), name=PageNames.USER_LOGIN),
    path('index/', IndexView.as_view(), name=PageNames.INDEX),
]
