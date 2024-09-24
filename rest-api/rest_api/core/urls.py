from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

core_views = {
    'user': UserView,
    'page-private': PagePrivateView,
    'page-public': PagePublicView,
    'content-private': ContentPrivateView,
    'content-public': ContentPublicView,
}

business_views = {
    'employee': EmployeeView,
    'item': ItemView,
}

urlpatterns = [
    path('core/token/', CreateTokenView.as_view()),
    path('core/current-user/', CurrentUserView.as_view()),
]

for prefix, view in core_views.items():
    router = DefaultRouter()
    router.register(prefix, view)
    urlpatterns.append(path('core/', include(router.urls)))

for prefix, view in business_views.items():
    router = DefaultRouter()
    router.register(prefix, view)
    urlpatterns.append(path('business/', include(router.urls)))
