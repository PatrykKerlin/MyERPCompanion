from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

views = {
    'user': UserView,
    'label': LabelView,
    'language': LanguageView,
    'translation': TranslationView,
    'module': ModuleView,
    'page': PageView,
    'image': ImageView,
    'page-labels': PageLabelsView,
    'field-translations': LabelTranslationsView,
    'page-images': PageImagesView,
}

urlpatterns = [
    path('health-check/', HealthCheckView.as_view()),
    path('token/', CreateTokenView.as_view()),
    path('current-user/', CurrentUserView.as_view()),
    path('page-content/<str:language>/<str:page_name>/', PageContentView.as_view({'get': 'retrieve'})),
    path('menu-content/<str:language>/', MenuContentView.as_view({'get': 'list'})),
]

# router = DefaultRouter()
# for prefix, view in views.items():
#     router.register(prefix, view)
# urlpatterns.append(path('', include(router.urls)))
