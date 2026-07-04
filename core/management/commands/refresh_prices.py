from django.core.management.base import BaseCommand
from core.models import Holding
from core.utils import get_live_price


class Command(BaseCommand):
    help = "Refresh current_price for all holdings (stocks, ETFs, mutual funds)."

    def handle(self, *args, **kwargs):
        holdings = Holding.objects.all()
        updated = 0
        for h in holdings:
            price = get_live_price(h.asset_type, h.identifier, h.exchange)
            if price is not None:
                h.current_price = price
                h.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f"Updated {updated} of {holdings.count()} holdings."
        ))