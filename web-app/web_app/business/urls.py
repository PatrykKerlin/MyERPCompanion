from django.urls import path

from core.helpers.constants import PageNames
from .views import *

urlpatterns = [
    path('add-employee/', NewEmployeeView.as_view(), name=PageNames.NEW_EMPLOYEE),
    path('add-item/', NewItemView.as_view(), name=PageNames.NEW_ITEM),
]
