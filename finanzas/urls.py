from django.urls import path,include
from django.contrib import auth
from . import views


urlpatterns = [
    #login/register
    path('',views.login_view, name='login'),
    path('register/',views.register_view, name='register'),

    #dashboard
    path('dashboard/',views.dashboard_view, name='dashboard'),

    #ingresos
    path('dashboard/ingresos/', views.register_incomes_view, name='register_incomes'),
    path('ingresos/<int:id>/borrar/', views.delete_income_register, name='delete_income'),
    path('ingresos/<int:id>/editar/', views.edit_income_register, name='edit_income'),

    #gastos
    path('dashboard/gastos/', views.register_expenses_view, name='register_expenses'),
    path('gastos/<int:id>/borrar/', views.delete_expense_register, name='delete_expense'),
    path('gastos/<int:id>/editar/', views.edit_expense_register, name='edit_expense'),


]