from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from django.db.models import Sum, Q
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import json

from .models import User, Supplier, Transaction


# ─── Auth helpers ─────────────────────────────────────────────────────────────

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        if not request.user.is_admin():
            return render(request, 'kiosk/403.html', status=403)
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


# ─── Auth Views ───────────────────────────────────────────────────────────────

def index(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Invalid username or password.'})
    return render(request, 'kiosk/index.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        if not username or not password:
            return JsonResponse({'success': False, 'error': 'All fields are required.'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already taken.'})
        user = User.objects.create_user(username=username, password=password, role='manager')
        login(request, user)
        return JsonResponse({'success': True})
    return render(request, 'kiosk/signup.html')


def forgot_password_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        new_password = data.get('new_password', '').strip()
        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No account found with that username.'})
    return render(request, 'kiosk/forgot_password.html')


def logout_view(request):
    logout(request)
    return redirect('/')


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required(login_url='/')
def dashboard(request):
    return render(request, 'kiosk/dashboard.html')


@login_required(login_url='/')
def dashboard_data(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_balance = Supplier.objects.aggregate(total=Sum('balance_owed'))['total'] or Decimal('0')
    active_suppliers_count = Supplier.objects.filter(status='active').count()

    month_payments = Transaction.objects.filter(
        transaction_type='payment',
        date__gte=month_start,
        date__lte=today
    )
    payments_count = month_payments.count()
    payments_list = list(month_payments.values('supplier__name', 'amount', 'item', 'date'))

    recent_txns = Transaction.objects.select_related('supplier').order_by('-created_at')[:20]
    recent_list = [
        {
            'supplier': t.supplier.name,
            'type': t.transaction_type,
            'amount': str(t.amount),
            'item': t.item,
            'date': str(t.date),
        }
        for t in recent_txns
    ]

    return JsonResponse({
        'total_balance': str(total_balance),
        'active_suppliers_count': active_suppliers_count,
        'payments_count': payments_count,
        'payments_list': [
            {
                'supplier': p['supplier__name'],
                'amount': str(p['amount']),
                'item': p['item'],
                'date': str(p['date']),
            } for p in payments_list
        ],
        'recent_transactions': recent_list,
    })


# ─── Suppliers ────────────────────────────────────────────────────────────────

@login_required(login_url='/')
def suppliers_page(request):
    return render(request, 'kiosk/suppliers.html')


@login_required(login_url='/')
def suppliers_api(request):
    if request.method == 'GET':
        qs = Supplier.objects.all()
        data = []
        for s in qs:
            data.append({
                'id': s.id,
                'name': s.name,
                'phone': s.phone,
                'item_supplied': s.item_supplied,
                'status': s.status,
                'balance_owed': str(s.balance_owed),
                'total_purchase': str(s.total_purchase),
                'total_paid': str(s.total_paid),
                'date_added': str(s.date_added),
                'last_transaction_date': str(s.last_transaction_date) if s.last_transaction_date else None,
            })
        return JsonResponse({'suppliers': data})

    if request.method == 'POST':
        data = json.loads(request.body)
        supplier = Supplier.objects.create(
            name=data['name'],
            phone=data['phone'],
            item_supplied=data['item_supplied'],
            status=data.get('status', 'active'),
        )
        return JsonResponse({'success': True, 'id': supplier.id})


@login_required(login_url='/')
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'PUT':
        data = json.loads(request.body)
        supplier.name = data.get('name', supplier.name)
        supplier.phone = data.get('phone', supplier.phone)
        supplier.item_supplied = data.get('item_supplied', supplier.item_supplied)
        supplier.status = data.get('status', supplier.status)
        supplier.save()
        return JsonResponse({'success': True})

    if request.method == 'DELETE':
        supplier.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=405)


# ─── Transactions ─────────────────────────────────────────────────────────────

@login_required(login_url='/')
def transactions_page(request):
    return render(request, 'kiosk/transactions.html')


@login_required(login_url='/')
def transactions_api(request):
    if request.method == 'GET':
        qs = Transaction.objects.select_related('supplier').all()
        txn_type = request.GET.get('type')
        month = request.GET.get('month')
        search = request.GET.get('search')

        if txn_type in ('payment', 'purchase'):
            qs = qs.filter(transaction_type=txn_type)
        if month:
            qs = qs.filter(date__month=int(month))
        if search:
            qs = qs.filter(supplier__name__icontains=search)

        data = [
            {
                'id': t.id,
                'date': str(t.date),
                'supplier': t.supplier.name,
                'supplier_id': t.supplier.id,
                'type': t.transaction_type,
                'amount': str(t.amount),
                'item': t.item,
            }
            for t in qs
        ]
        return JsonResponse({'transactions': data})

    if request.method == 'POST':
        data = json.loads(request.body)
        supplier_id = data['supplier_id']
        txn_type = data['type']
        amount = Decimal(str(data['amount']))
        item = data.get('item', '')

        supplier = get_object_or_404(Supplier, pk=supplier_id)

        # Validation
        if txn_type == 'payment':
            if amount > supplier.balance_owed:
                return JsonResponse({'success': False, 'error': 'Payment exceeds balance owed.'})
            supplier.balance_owed -= amount
            supplier.total_paid += amount
        elif txn_type == 'purchase':
            supplier.balance_owed += amount
            supplier.total_purchase += amount

        supplier.last_transaction_date = timezone.now().date()
        supplier.save()

        transaction = Transaction.objects.create(
            supplier=supplier,
            transaction_type=txn_type,
            amount=amount,
            item=item or supplier.item_supplied,
        )
        return JsonResponse({'success': True, 'id': transaction.id})


@login_required(login_url='/')
def transaction_delete(request, pk):
    if request.method == 'DELETE':
        txn = get_object_or_404(Transaction, pk=pk)
        supplier = txn.supplier

        # Reverse the effect
        if txn.transaction_type == 'payment':
            supplier.balance_owed += txn.amount
            supplier.total_paid -= txn.amount
        elif txn.transaction_type == 'purchase':
            supplier.balance_owed -= txn.amount
            supplier.total_purchase -= txn.amount

        # Update last_transaction_date
        remaining = Transaction.objects.filter(supplier=supplier).exclude(pk=pk).order_by('-date').first()
        supplier.last_transaction_date = remaining.date if remaining else None
        supplier.save()

        txn.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)


# ─── Balances ─────────────────────────────────────────────────────────────────

@login_required(login_url='/')
def balances_page(request):
    return render(request, 'kiosk/balances.html')


@login_required(login_url='/')
def balances_api(request):
    sort = request.GET.get('sort', 'date_added')
    qs = Supplier.objects.filter(balance_owed__gt=0)

    order_map = {
        'date_added': 'date_added',
        'oldest': 'date_added',
        'newest': '-date_added',
        'az': 'name',
        'highest': '-balance_owed',
        'lowest': 'balance_owed',
    }
    qs = qs.order_by(order_map.get(sort, 'date_added'))

    data = [
        {
            'id': s.id,
            'name': s.name,
            'item_supplied': s.item_supplied,
            'total_purchase': str(s.total_purchase),
            'total_paid': str(s.total_paid),
            'balance_owed': str(s.balance_owed),
            'date_added': str(s.date_added),
        }
        for s in qs
    ]
    total = sum(Decimal(d['balance_owed']) for d in data)
    return JsonResponse({'balances': data, 'total': str(total)})


# ─── Admin Panel ──────────────────────────────────────────────────────────────

@login_required(login_url='/')
@admin_required
def admin_panel(request):
    return render(request, 'kiosk/admin_panel.html')


@login_required(login_url='/')
@admin_required
def admin_users_api(request):
    if request.method == 'GET':
        users = User.objects.all().order_by('date_joined')
        data = [
            {
                'id': u.id,
                'username': u.username,
                'date_joined': u.date_joined.strftime('%Y-%m-%d'),
                'role': u.role,
            }
            for u in users
        ]
        return JsonResponse({'users': data})

    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'manager')
        if not username or not password:
            return JsonResponse({'success': False, 'error': 'All fields required.'})
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists.'})
        user = User.objects.create_user(username=username, password=password, role=role)
        return JsonResponse({'success': True, 'id': user.id})


@login_required(login_url='/')
@admin_required
def admin_user_delete(request, pk):
    if request.method == 'DELETE':
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            return JsonResponse({'success': False, 'error': 'Cannot delete yourself.'})
        user.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)


# ─── Suppliers dropdown helpers ───────────────────────────────────────────────

@login_required(login_url='/')
def suppliers_with_debt(request):
    suppliers = Supplier.objects.filter(balance_owed__gt=0)
    data = [{'id': s.id, 'name': s.name, 'balance_owed': str(s.balance_owed), 'item_supplied': s.item_supplied} for s in suppliers]
    return JsonResponse({'suppliers': data})


@login_required(login_url='/')
def suppliers_active(request):
    suppliers = Supplier.objects.filter(status='active')
    data = [{'id': s.id, 'name': s.name, 'balance_owed': str(s.balance_owed), 'item_supplied': s.item_supplied} for s in suppliers]
    return JsonResponse({'suppliers': data})
