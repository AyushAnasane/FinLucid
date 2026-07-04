from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import Expense, Budget, Holding
from .utils import get_tickers_for_exchange, get_mf_schemes, get_live_price


def index(request):
    return render(request, 'core/index.html')


def dashboard(request):
    return render(request, 'core/dashboard.html')


def financial(request):
    if request.method == 'POST':
        if 'set_budget' in request.POST:
            Budget.objects.all().delete()
            Budget.objects.create(amount=request.POST['budget_amount'])
        else:
            Expense.objects.create(
                amount=request.POST['amount'],
                category=request.POST['category'],
                note=request.POST.get('note', '')
            )
        return redirect('financial')

    category_filter = request.GET.get('category')
    expenses = Expense.objects.all().order_by('-date')
    if category_filter:
        expenses = expenses.filter(category=category_filter)

    total_spent = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    category_totals = Expense.objects.values('category').annotate(total=Sum('amount'))

    budget = Budget.objects.first()
    budget_amount = budget.amount if budget else 0
    budget_used_pct = round((total_spent / budget_amount) * 100, 1) if budget_amount else 0

    context = {
        'expenses': expenses,
        'total_spent': total_spent,
        'category_totals': category_totals,
        'budget_amount': budget_amount,
        'budget_used_pct': budget_used_pct,
        'category_filter': category_filter,
    }
    return render(request, 'core/financial.html', context)


def delete_expense(request, expense_id):
    Expense.objects.filter(id=expense_id).delete()
    return redirect('financial')


def edit_expense(request, expense_id):
    expense = Expense.objects.get(id=expense_id)
    if request.method == 'POST':
        expense.amount = request.POST['amount']
        expense.category = request.POST['category']
        expense.note = request.POST.get('note', '')
        expense.save()
        return redirect('financial')
    return render(request, 'core/edit_expense.html', {'expense': expense})


def options(request):
    return render(request, 'core/options.html')


def portfolio(request):
    error = None

    if request.method == 'POST':
        asset_type = request.POST['asset_type']
        identifier = request.POST['identifier'].strip().upper()
        exchange = request.POST.get('exchange', 'NSE')
        name = ''

        if asset_type in ('stock', 'etf'):
            tickers = get_tickers_for_exchange(exchange)
            if identifier not in tickers:
                error = f"'{identifier}' is not a valid {exchange} ticker."
            else:
                name = tickers[identifier]
        elif asset_type == 'mf':
            mf_schemes = get_mf_schemes()
            exchange = ''
            if identifier not in mf_schemes:
                error = f"'{identifier}' is not a valid AMFI scheme code."
            else:
                name = mf_schemes[identifier]
        else:
            error = "Invalid asset type."

        if not error:
            Holding.objects.create(
                asset_type=asset_type,
                exchange=exchange,
                identifier=identifier,
                name=name,
                quantity=request.POST['quantity'],
                buy_price=request.POST['buy_price'],
                current_price=request.POST['current_price'],
            )
            return redirect('portfolio')

    holdings = Holding.objects.all().order_by('-date_added')
    total_invested = sum(h.invested for h in holdings)
    total_current = sum(h.current_value for h in holdings)
    total_pnl = total_current - total_invested
    total_pnl_pct = round((total_pnl / total_invested) * 100, 2) if total_invested else 0

    breakdown = {}
    for h in holdings:
        label = h.get_asset_type_display()
        breakdown.setdefault(label, 0)
        breakdown[label] += h.current_value
    category_breakdown = [
        {
            'label': label,
            'value': value,
            'pct': round((value / total_current) * 100, 1) if total_current else 0,
        }
        for label, value in breakdown.items()
    ]

    context = {
        'holdings': holdings,
        'total_invested': total_invested,
        'total_current': total_current,
        'total_pnl': total_pnl,
        'total_pnl_pct': total_pnl_pct,
        'valid_tickers_nse': sorted(get_tickers_for_exchange('NSE').keys()),
        'valid_tickers_bse': sorted(get_tickers_for_exchange('BSE').keys()),
        'category_breakdown': category_breakdown,
        'error': error,
    }
    return render(request, 'core/portfolio.html', context)


def delete_holding(request, holding_id):
    Holding.objects.filter(id=holding_id).delete()
    return redirect('portfolio')


def edit_holding(request, holding_id):
    holding = Holding.objects.get(id=holding_id)
    if request.method == 'POST':
        holding.quantity = request.POST['quantity']
        holding.buy_price = request.POST['buy_price']
        holding.current_price = request.POST['current_price']
        holding.save()
        return redirect('portfolio')
    return render(request, 'core/edit_holding.html', {'holding': holding})


def refresh_prices(request):
    holdings = Holding.objects.all()
    for h in holdings:
        live_price = get_live_price(h.asset_type, h.identifier, h.exchange)
        if live_price is not None:
            h.current_price = live_price
            h.save()
    return redirect('portfolio')