from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('financial/', views.financial, name='financial'),
    path('financial/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('financial/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('portfolio/delete/<int:holding_id>/', views.delete_holding, name='delete_holding'),
    path('portfolio/refresh/', views.refresh_prices, name='refresh_prices'),
    path('portfolio/edit/<int:holding_id>/', views.edit_holding, name='edit_holding'),
    path('login/', views.login_page, name='login_page'),
]

