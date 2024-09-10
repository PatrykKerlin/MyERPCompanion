from .views import user_views
from .views import token_views
from django.urls import path

urlpatterns = [
    path('token/', token_views.CreateTokenView.as_view(), name='token'),
    path('user/create/', user_views.CreateUserView.as_view(), name='user-create'),
    path('user/current/', user_views.ManageUserView.as_view(), name='user-current'),
]
