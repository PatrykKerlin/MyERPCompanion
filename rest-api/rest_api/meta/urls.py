from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

views = {
}

urlpatterns = []

for prefix, view in views.items():
    router = DefaultRouter()
    router.register(prefix, view)
    urlpatterns.append(path('', include(router.urls)))
