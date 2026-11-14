import re
from sqlalchemy.dialects import mysql
from sqlalchemy.schema import CreateTable, CreateIndex
from sqlalchemy import select
from app.models.protected_payment import ProtectedPayment, WorkMilestone, ProtectedEvent
from app.models import Escrow
from app.models.merchant_api import IntegrationProfile, MerchantApiKey, CheckoutOrder
from app.models.checkout_security import CheckoutAuth
from app.models.developer_application import DeveloperApplication, ApiCredential
from app.models.developer_usage import ApiUsageLog, ApiRateWindow
from app.models.webhook import WebhookEndpoint, WebhookDelivery


def test_protected_tables_and_locks_compile_for_mysql():
    dialect = mysql.dialect()
    for model in [ProtectedPayment, WorkMilestone, ProtectedEvent,
                  IntegrationProfile, MerchantApiKey, CheckoutOrder, CheckoutAuth,
                  DeveloperApplication, ApiCredential, ApiUsageLog, ApiRateWindow, WebhookEndpoint, WebhookDelivery]:
        statement = str(CreateTable(model.__table__).compile(dialect=dialect))
        assert 'CREATE TABLE' in statement
        assert 'FOREIGN KEY' in statement
        assert all(len(name.strip('`')) <= 64 for name in re.findall(r'CONSTRAINT (\S+)', statement))
        for index in model.__table__.indexes:
            assert 'CREATE INDEX' in str(CreateIndex(index).compile(dialect=dialect))
    ddl = str(CreateTable(ProtectedPayment.__table__).compile(dialect=dialect))
    assert 'JSON' in ddl and 'DATETIME' in ddl
    lock = str(select(Escrow).where(Escrow.id == 1).with_for_update().compile(dialect=dialect))
    assert 'FOR UPDATE' in lock
