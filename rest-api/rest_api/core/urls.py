from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

views = {
    'user': UserView,
    'field': FieldView,
    'text': TextView,
    'page': PageView,
    'image': ImageView,
    'page-fields': PageFieldsView,
}

urlpatterns = [
    path('token/', CreateTokenView.as_view()),
    path('current-user/', CurrentUserView.as_view()),
    # path('content-public-by-page/<int:id>/', ContentPublicByPageView.as_view({'get': 'list'})),
]

for prefix, view in views.items():
    router = DefaultRouter()
    router.register(prefix, view)
    urlpatterns.append(path('', include(router.urls)))
