from django.db import models

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('shopping', 'Shopping'),
        ('bills', 'Bills'),
        ('entertainment', 'Entertainment'),
        ('other', 'Other'),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    note = models.CharField(max_length=200, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - ₹{self.amount}"

class Budget(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

class Holding(models.Model):
    ASSET_CHOICES = [
        ('stock', 'Stock'),
        ('etf', 'ETF'),
        ('mf', 'Mutual Fund'),
    ]
    EXCHANGE_CHOICES = [
        ('NSE', 'NSE'),
        ('BSE', 'BSE'),
    ]

    asset_type = models.CharField(max_length=10, choices=ASSET_CHOICES, default='stock')
    exchange = models.CharField(max_length=5, choices=EXCHANGE_CHOICES, default='NSE', blank=True)
    identifier = models.CharField(max_length=30)
    name = models.CharField(max_length=200, blank=True)
    quantity = models.DecimalField(max_digits=14, decimal_places=4)
    buy_price = models.DecimalField(max_digits=12, decimal_places=4)
    current_price = models.DecimalField(max_digits=12, decimal_places=4)
    date_added = models.DateField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.identifier} ({self.get_asset_type_display()})"

    @property
    def invested(self):
        return self.quantity * self.buy_price

    @property
    def current_value(self):
        return self.quantity * self.current_price

    @property
    def pnl(self):
        return self.current_value - self.invested

    @property
    def pnl_pct(self):
        if self.invested:
            return round((self.pnl / self.invested) * 100, 2)
        return 0