from django import forms
from .models import Item, Category, Location, TransactionLog


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'sku', 'description', 'category', 'location',
                  'quantity', 'minimum_quantity', 'unit', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Sodium Chloride'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CHM-001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'minimum_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. bottle, vial, ml'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CheckInForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1, label='Quantity to Add',
        widget=forms.NumberInput(attrs={'class': 'form-control big-input', 'min': 1, 'value': 1})
    )
    notes = forms.CharField(
        required=False, label='Notes (optional)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Restocked from supplier'})
    )


class CheckOutForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1, label='Quantity to Remove',
        widget=forms.NumberInput(attrs={'class': 'form-control big-input', 'min': 1, 'value': 1})
    )
    notes = forms.CharField(
        required=False, label='Notes (optional)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Used in experiment A3'})
    )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
