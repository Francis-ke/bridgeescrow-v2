from types import SimpleNamespace
import click
import time
from flask import current_app
from app.core.db import db
from .webhook_claims import claim, finish
from .webhook_secrets import canonical, signed_headers
from .webhook_transport import send


def deliver(limit=20, sender=None):
    sender = sender or send
    result = {'attempted': 0, 'delivered': 0, 'failed': 0, 'skipped': 0}
    for _ in range(max(0, min(limit, 100))):
        delivery = claim()
        if delivery is None:
            break
        if delivery.get('skipped'):
            result['skipped'] += 1
            continue
        status, error = None, None
        try:
            body = canonical(delivery['payload'])
            endpoint = SimpleNamespace(secret_ciphertext=delivery['secret_ciphertext'])
            headers = signed_headers(endpoint, body)
            headers['BridgeEscrow-Event-Id'] = delivery['payload']['id']
            status = sender(delivery['url'], body, headers)
            if not isinstance(status, int) or not 200 <= status < 300:
                error = f'HTTP {status}' if isinstance(status, int) else 'Invalid HTTP response'
        except Exception as exc:
            error = f'Delivery failed ({type(exc).__name__})'
        finish(delivery, status, error)
        result['attempted'] += 1
        result['delivered' if error is None else 'failed'] += 1
    return result


def register_cli(app):
    @app.cli.command('deliver-webhooks')
    @click.option('--limit', type=click.IntRange(1, 100), default=20, show_default=True)
    @click.option('--watch', is_flag=True, help='Continuously process due events.')
    @click.option('--interval', type=click.IntRange(1, 300), default=5, show_default=True)
    def run(limit, watch, interval):
        """Deliver due webhook events, once or as a durable polling worker."""
        try:
            while True:
                try:
                    result = deliver(limit)
                    click.echo(', '.join(f'{key}: {value}' for key, value in result.items()))
                except Exception as error:
                    db.session.rollback()
                    current_app.logger.error('Webhook worker iteration failed (%s)', type(error).__name__)
                    if not watch:
                        raise click.ClickException('Webhook worker could not complete this iteration') from None
                if not watch:
                    break
                time.sleep(interval)
        except KeyboardInterrupt:
            db.session.rollback()
            click.echo('Webhook worker stopped.')
