"""
Views for the Lab Inventory Management System.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Item, Category, Location, TransactionLog
from .forms import ItemForm, CheckInForm, CheckOutForm, CategoryForm, LocationForm


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    total_items = Item.objects.count()
    total_categories = Category.objects.count()
    out_of_stock = Item.objects.filter(quantity=0).count()

    # Items where quantity <= minimum_quantity
    all_items = Item.objects.select_related('category', 'location').all()
    low_stock_items = [item for item in all_items if item.is_low_stock][:8]
    low_stock_count = len(low_stock_items)

    recent_transactions = TransactionLog.objects.select_related('item', 'performed_by').order_by('-timestamp')[:10]

    # Stats for the past 7 days
    week_ago = timezone.now() - timedelta(days=7)
    recent_checkins = TransactionLog.objects.filter(
        transaction_type='in', timestamp__gte=week_ago
    ).aggregate(total=Sum('quantity_change'))['total'] or 0
    recent_checkouts = TransactionLog.objects.filter(
        transaction_type='out', timestamp__gte=week_ago
    ).aggregate(total=Sum('quantity_change'))['total'] or 0

    context = {
        'total_items': total_items,
        'total_categories': total_categories,
        'out_of_stock': out_of_stock,
        'low_stock_count': len(low_stock_items),
        'low_stock_items': low_stock_items,
        'recent_transactions': recent_transactions,
        'recent_checkins': recent_checkins,
        'recent_checkouts': abs(recent_checkouts),
        'page': 'dashboard',
    }
    return render(request, 'inventory/dashboard.html', context)


# ─── ITEMS ───────────────────────────────────────────────────────────────────

@login_required
def item_list(request):
    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    location_id = request.GET.get('location', '')
    stock_filter = request.GET.get('stock', '')

    items = Item.objects.select_related('category', 'location').all()

    if q:
        items = items.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q))
    if category_id:
        items = items.filter(category_id=category_id)
    if location_id:
        items = items.filter(location_id=location_id)
    if stock_filter == 'low':
        items = [i for i in items if i.is_low_stock]
    elif stock_filter == 'out':
        items = items.filter(quantity=0)

    categories = Category.objects.all()
    locations = Location.objects.all()

    context = {
        'items': items,
        'categories': categories,
        'locations': locations,
        'q': q,
        'selected_category': category_id,
        'selected_location': location_id,
        'stock_filter': stock_filter,
        'page': 'items',
    }
    return render(request, 'inventory/item_list.html', context)


@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    transactions = item.transactions.select_related('performed_by').order_by('-timestamp')[:20]

    checkin_form = CheckInForm()
    checkout_form = CheckOutForm()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'checkin':
            checkin_form = CheckInForm(request.POST)
            if checkin_form.is_valid():
                qty = checkin_form.cleaned_data['quantity']
                notes = checkin_form.cleaned_data.get('notes', '')
                before = item.quantity
                item.quantity += qty
                item.save()
                TransactionLog.objects.create(
                    item=item, transaction_type='in',
                    quantity_change=qty,
                    quantity_before=before,
                    quantity_after=item.quantity,
                    performed_by=request.user,
                    notes=notes,
                )
                messages.success(request, f'✅ Checked IN {qty} × {item.name}. New stock: {item.quantity}')
                return redirect('item_detail', pk=pk)

        elif action == 'checkout':
            checkout_form = CheckOutForm(request.POST)
            if checkout_form.is_valid():
                qty = checkout_form.cleaned_data['quantity']
                notes = checkout_form.cleaned_data.get('notes', '')
                if qty > item.quantity:
                    messages.error(request, f'❌ Cannot check out {qty} — only {item.quantity} in stock.')
                else:
                    before = item.quantity
                    item.quantity -= qty
                    item.save()
                    TransactionLog.objects.create(
                        item=item, transaction_type='out',
                        quantity_change=-qty,
                        quantity_before=before,
                        quantity_after=item.quantity,
                        performed_by=request.user,
                        notes=notes,
                    )
                    messages.success(request, f'✅ Checked OUT {qty} × {item.name}. Remaining: {item.quantity}')
                    return redirect('item_detail', pk=pk)

    context = {
        'item': item,
        'transactions': transactions,
        'checkin_form': checkin_form,
        'checkout_form': checkout_form,
        'page': 'items',
    }
    return render(request, 'inventory/item_detail.html', context)


@login_required
def item_add(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'✅ Item "{item.name}" added successfully!')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm()
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Add', 'page': 'items'})


@login_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Item "{item.name}" updated.')
            return redirect('item_detail', pk=pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {'form': form, 'action': 'Edit', 'item': item, 'page': 'items'})


@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        name = item.name
        item.delete()
        messages.success(request, f'🗑️ Item "{name}" deleted.')
        return redirect('item_list')
    return render(request, 'inventory/item_confirm_delete.html', {'item': item, 'page': 'items'})


# ─── QR SCANNER ──────────────────────────────────────────────────────────────

@login_required
def qr_scanner(request):
    return render(request, 'inventory/qr_scanner.html', {'page': 'scanner'})


@login_required
def qr_lookup(request):
    """AJAX / redirect endpoint after QR scan."""
    sku = request.GET.get('sku', '').strip()
    if sku:
        try:
            item = Item.objects.get(sku=sku)
            return redirect('item_detail', pk=item.pk)
        except Item.DoesNotExist:
            messages.error(request, f'❌ No item found with SKU: {sku}')
    return redirect('qr_scanner')


# ─── CATEGORIES ──────────────────────────────────────────────────────────────

@login_required
def category_list(request):
    categories = Category.objects.annotate(item_count=Count('items')).order_by('name')
    locations = Location.objects.annotate(item_count=Count('items')).order_by('name')
    return render(request, 'inventory/category_list.html', {'categories': categories, 'locations': locations, 'page': 'settings'})


@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Category added!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {'form': form, 'action': 'Add', 'page': 'settings'})


@login_required
def category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Category updated!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'inventory/category_form.html', {'form': form, 'action': 'Edit', 'page': 'settings'})


# ─── LOCATIONS ───────────────────────────────────────────────────────────────

@login_required
def location_list(request):
    # Redirect to the combined category+location settings page
    return redirect('category_list')


@login_required
def location_add(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Location added!')
            return redirect('location_list')
    else:
        form = LocationForm()
    return render(request, 'inventory/location_form.html', {'form': form, 'action': 'Add', 'page': 'settings'})


@login_required
def location_edit(request, pk):
    loc = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=loc)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Location updated!')
            return redirect('location_list')
    else:
        form = LocationForm(instance=loc)
    return render(request, 'inventory/location_form.html', {'form': form, 'action': 'Edit', 'page': 'settings'})


# ─── TRANSACTION HISTORY ─────────────────────────────────────────────────────

@login_required
def transaction_history(request):
    transactions = TransactionLog.objects.select_related('item', 'performed_by').order_by('-timestamp')[:100]
    return render(request, 'inventory/transaction_history.html', {'transactions': transactions, 'page': 'history'})
