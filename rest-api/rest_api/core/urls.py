from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

core_views = {
    'user': UserView,
    'page-private': PagePrivateView,
    'page-public': PagePublicView,
    'content-public': ContentPublicView,
    'content-private': ContentPrivateView,
    'image-public': ImagePublicView,
    'image-private': ImagePrivateView,
}

business_views = {
    'employee': EmployeeView,
    'item': ItemView,
}

urlpatterns = [
    path('token/', CreateTokenView.as_view()),
    path('current-user/', CurrentUserView.as_view()),
    path('content-public-by-page/<int:id>/', ContentPublicByPageView.as_view({'get': 'list'})),
    path('image-public-by-page/<int:id>/', ImagePublicByPageView.as_view({'get': 'list'})),
]

for prefix, view in core_views.items():
    router = DefaultRouter()
    router.register(prefix, view)
    urlpatterns.append(path('', include(router.urls)))

for prefix, view in business_views.items():
    router = DefaultRouter()
    router.register(prefix, view)
    urlpatterns.append(path('', include(router.urls)))
