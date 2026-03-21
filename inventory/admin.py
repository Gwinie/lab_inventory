from django.contrib import admin
from .models import Category, Location, Item, TransactionLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'location', 'quantity', 'minimum_quantity', 'stock_status']
    list_filter = ['category', 'location']
    search_fields = ['name', 'sku']
    readonly_fields = ['qr_code', 'created_at', 'updated_at']


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ['item', 'transaction_type', 'quantity_change', 'quantity_before', 'quantity_after', 'performed_by', 'timestamp']
    list_filter = ['transaction_type', 'timestamp']
    search_fields = ['item__name', 'item__sku']
    readonly_fields = ['timestamp']
