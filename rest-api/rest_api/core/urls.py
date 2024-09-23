from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

views = {
    'user': UserView,
    'page-private': PagePrivateView,
    'page-public': PagePublicView,
    'employee': EmployeeView,
    'item': ItemView,
}

urlpatterns = [
    path('token/', CreateTokenView.as_view()),
    path('current-user', CurrentUserView.as_view()),
]

for prefix, view in views.items():
    router = DefaultRouter()
    router.register(prefix, view)
    urlpatterns.append(path('', include(router.urls)))
