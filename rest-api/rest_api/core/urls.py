from .views import user_views
from django.urls import path

urlpatterns = [
    path('user/create/', user_views.CreateUserView.as_view(), name='create-user'),
]
