from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

views = {
    'user': UserView,
    'label': LabelView,
    'language': LanguageView,
    'translation': TranslationView,
    'module': ModuleView,
    'view': ViewView,
    'image': ImageView,
    'view-labels': ViewLabelsView,
    'field-translations': LabelTranslationsView,
    'view-images': ViewImagesView,
}

urlpatterns = [
    path('health-check/', HealthCheckView.as_view()),
    path('token/', TokenView.as_view()),
    path('current-user/', CurrentUserView.as_view()),
    path('view-content/<str:language>/<str:view_name>/', ViewContentView.as_view({'get': 'retrieve'})),
    path('menu-content/<str:language>/', MenuContentView.as_view({'get': 'list'})),
]

# router = DefaultRouter()
# for prefix, view in views.items():
#     router.register(prefix, view)
# urlpatterns.append(path('', include(router.urls)))
