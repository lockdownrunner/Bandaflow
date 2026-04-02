from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.index, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('logout/', views.logout_view, name='logout'),

    # Pages
    path('dashboard/', views.dashboard, name='dashboard'),
    path('suppliers/', views.suppliers_page, name='suppliers'),
    path('transactions/', views.transactions_page, name='transactions'),
    path('balances/', views.balances_page, name='balances'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),

    # API
    path('api/dashboard/', views.dashboard_data, name='dashboard_data'),
    path('api/suppliers/', views.suppliers_api, name='suppliers_api'),
    path('api/suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('api/suppliers/with-debt/', views.suppliers_with_debt, name='suppliers_with_debt'),
    path('api/suppliers/active/', views.suppliers_active, name='suppliers_active'),
    path('api/transactions/', views.transactions_api, name='transactions_api'),
    path('api/transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    path('api/balances/', views.balances_api, name='balances_api'),
    path('api/admin/users/', views.admin_users_api, name='admin_users_api'),
    path('api/admin/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
]
