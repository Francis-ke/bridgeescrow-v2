"""Read-only dashboard totals for the merchant's isolated API sandboxes."""
from app.models.developer_application import DeveloperApplication
from app.models.mixins import MoneyMixin
from .sandbox import overview


def for_owner(user_id):
    applications = DeveloperApplication.query.filter_by(user_id=user_id, environment='sandbox').all()
    totals = {'available': 0, 'escrow': 0}
    for application in applications:
        balances = overview(application.id)
        totals['available'] += MoneyMixin.to_cents(balances['available'])
        totals['escrow'] += MoneyMixin.to_cents(balances['held'])
    return {**{key: MoneyMixin.from_cents(value) for key, value in totals.items()},
            'application_count': len(applications), 'environment': 'sandbox',
            'currency': 'KES', 'production_enabled': False}
