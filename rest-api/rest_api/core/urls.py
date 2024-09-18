from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import token_views, user_view, employee_view, item_view

user_routes = DefaultRouter()
user_routes.register('user', user_view.UserView)

employee_routes = DefaultRouter()
employee_routes.register('employee', employee_view.EmployeeView)

item_routes = DefaultRouter()
item_routes.register('item', item_view.ItemView)

urlpatterns = [
    path('token/', token_views.CreateTokenView.as_view()),
    path('', include(user_routes.urls)),
    path('', include(employee_routes.urls)),
    path('', include(item_routes.urls)),
]
