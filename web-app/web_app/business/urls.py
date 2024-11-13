from django.urls import path

from core.helpers.constants import PageNames
from .views import *

urlpatterns = [
    path('new-employee/', NewEmployeeView.as_view(), name=PageNames.NEW_EMPLOYEE),
    path('all-employees/', AllEmployeesView.as_view(), name=PageNames.ALL_EMPLOYEES),
    path('new-item/', NewItemView.as_view(), name=PageNames.NEW_ITEM),
    path('new-category/', NewCategoryView.as_view(), name=PageNames.NEW_CATEGORY),
]
