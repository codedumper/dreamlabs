from django.urls import path
from . import views

app_name = 'financial'

urlpatterns = [
    # Expenses (Dépenses)
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:expense_id>/update/', views.expense_update, name='expense_update'),
    path('expenses/<int:expense_id>/delete/', views.expense_delete, name='expense_delete'),
    
    # Salaries (Salaires)
    path('salaries/', views.salary_list, name='salary_list'),
    path('salaries/create/', views.salary_create, name='salary_create'),
    
    # Revenues (Revenus)
    path('revenues/', views.revenue_list, name='revenue_list'),
    path('revenues/create/', views.revenue_create, name='revenue_create'),
]
