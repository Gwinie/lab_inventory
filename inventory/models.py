"""
Inventory models: Category, Location, Item, TransactionLog
"""
import io
import qrcode
from django.db import models
from django.contrib.auth.models import User
from django.core.files import File
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6366f1', help_text='Hex color for UI badge')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True, verbose_name='SKU / Barcode')
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    quantity = models.IntegerField(default=0)
    minimum_quantity = models.IntegerField(default=5, help_text='Alert threshold for low stock')
    unit = models.CharField(max_length=50, default='unit', help_text='e.g. unit, box, vial, ml')
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.sku})'

    @property
    def is_low_stock(self):
        return 0 < self.quantity <= self.minimum_quantity

    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'out'
        elif self.is_low_stock:
            return 'low'
        return 'ok'

    def generate_qr_code(self):
        """Generate and save a QR code image for this item."""
        qr_data = f'LABITEM:{self.sku}:{self.name}'
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        filename = f'qr_{self.sku}.png'
        self.qr_code.save(filename, File(buf), save=False)

    def save(self, *args, **kwargs):
        # Auto-generate QR code on first save
        is_new = self.pk is None
        if is_new:
            super().save(*args, **kwargs)
            self.generate_qr_code()
            super().save(update_fields=['qr_code'])
        else:
            super().save(*args, **kwargs)


class TransactionLog(models.Model):
    TRANSACTION_TYPES = [
        ('in', 'Check In'),
        ('out', 'Check Out'),
        ('adjust', 'Adjustment'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity_change = models.IntegerField(help_text='Positive = in, Negative = out')
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Transaction Log'

    def __str__(self):
        action = 'IN' if self.quantity_change > 0 else 'OUT'
        return f'{action} {abs(self.quantity_change)}x {self.item.name} @ {self.timestamp:%Y-%m-%d %H:%M}'
