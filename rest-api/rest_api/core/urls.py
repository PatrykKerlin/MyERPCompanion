from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import token_views, user_views, employee_views

user_routes = DefaultRouter()
user_routes.register('user', user_views.UserViews)

employee_routes = DefaultRouter()
employee_routes.register('employee', employee_views.EmployeeViews)

urlpatterns = [
    path('token/', token_views.CreateTokenView.as_view()),
    path('', include(user_routes.urls)),
    path('', include(employee_routes.urls)),
]
