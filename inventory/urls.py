from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Items
    path('items/', views.item_list, name='item_list'),
    path('items/add/', views.item_add, name='item_add'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('items/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('items/<int:pk>/delete/', views.item_delete, name='item_delete'),

    # QR Scanner
    path('scanner/', views.qr_scanner, name='qr_scanner'),
    path('scanner/lookup/', views.qr_lookup, name='qr_lookup'),

    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),

    # Locations
    path('locations/', views.location_list, name='location_list'),
    path('locations/add/', views.location_add, name='location_add'),
    path('locations/<int:pk>/edit/', views.location_edit, name='location_edit'),

    # History
    path('history/', views.transaction_history, name='transaction_history'),
]
