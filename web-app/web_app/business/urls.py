from django.urls import path

from core.helpers.constants import PageNames
from .views import *

urlpatterns = [
    path('new-employee/', NewEmployeeView.as_view(), name=PageNames.NEW_EMPLOYEE),
    path('new-item/', NewItemView.as_view(), name=PageNames.NEW_ITEM),
]
