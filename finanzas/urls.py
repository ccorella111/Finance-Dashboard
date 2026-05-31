from django.urls import path,include
from django.contrib import auth
from . import views


urlpatterns = [
    #login/register
    path('',views.login_view, name='login'),
    path('register/',views.register_view, name='register'),

    #dashboard
    path('dashboard/',views.dashboard_view, name='dashboard'),
]