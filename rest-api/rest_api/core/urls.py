from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import token_views, user_views, employee_views, item_views

user_routes = DefaultRouter()
user_routes.register('user', user_views.UserViews)

employee_routes = DefaultRouter()
employee_routes.register('employee', employee_views.EmployeeViews)

item_routes = DefaultRouter()
item_routes.register('item', item_views.ItemViews)

urlpatterns = [
    path('token/', token_views.CreateTokenView.as_view()),
    path('', include(user_routes.urls)),
    path('', include(employee_routes.urls)),
    path('', include(item_routes.urls)),
]
