from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

views = {
    'employee': EmployeeView,
    # 'item': ItemView,
}

urlpatterns = []

router = DefaultRouter()
for prefix, view in views.items():
    router.register(prefix, view)
urlpatterns.append(path('', include(router.urls)))
