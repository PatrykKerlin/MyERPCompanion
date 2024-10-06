from django.urls import path

from .helpers.constants import PageNames
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name=PageNames.LOGIN),
    path('index/', IndexView.as_view(), name=PageNames.INDEX),
]
