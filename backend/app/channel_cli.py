import click
from app.core.db import db
from app.core.errors import ApiError
from app.models import User
from app.services.accounts import next_account_number
from app.services.wallet_service import wallet_for


def register_cli(app):
    @app.cli.command('channels-status')
    def status():
        """Show configuration readiness without exposing provider credentials."""
        cfg = app.config
        click.echo(f"Payments: {cfg['PAYMENT_MODE']}; SMS: {cfg['SMS_MODE']}; USSD: {cfg['USSD_ENVIRONMENT']}")
        for label, keys in {
            'M-PESA collections': ['MPESA_CONSUMER_KEY', 'MPESA_CONSUMER_SECRET', 'MPESA_SHORTCODE',
                                   'MPESA_PASSKEY', 'MPESA_CALLBACK_URL', 'MPESA_CALLBACK_TOKEN'],
            'SMS provider': ['AT_USERNAME', 'AT_API_KEY'],
            'USSD gateway': ['USSD_CALLBACK_TOKEN', 'USSD_SERVICE_CODE'],
            'B2C payouts': ['MPESA_B2C_INITIATOR', 'MPESA_B2C_SECURITY_CREDENTIAL',
                           'MPESA_B2C_RESULT_URL', 'MPESA_B2C_TIMEOUT_URL'],
        }.items():
            missing = [key for key in keys if not cfg.get(key)]
            click.echo(label + ': ' + ('missing ' + ', '.join(missing) if missing else 'fields configured'))
        if cfg['PAYMENT_MODE'] == 'daraja_live':
            from app.services.live_ledger import verify_clean
            try:
                verify_clean()
                click.echo('Live ledger: no unbacked deposits detected')
            except ApiError as error:
                click.echo('Live ledger blocked: ' + error.message)
        click.echo('No provider calls were made. Provisioning and live delivery still require testing.')

    @app.cli.command('create-admin')
    @click.option('--email', prompt=True)
    @click.option('--name', prompt=True)
    @click.password_option(confirmation_prompt=True)
    def admin(email, name, password):
        """Create a new operator account on a server you administer."""
        from marshmallow import fields, ValidationError
        try:
            email = fields.Email().deserialize(email).lower()
        except ValidationError:
            raise click.ClickException('Enter a valid email address') from None
        if len(password) < 12 or len(name.strip()) < 3:
            raise click.ClickException('Use a name of 3+ characters and password of 12+ characters')
        if User.query.filter_by(email=email).first():
            raise click.ClickException('An account already exists with this email; it was not changed')
        account = next_account_number()
        user = User(account_number=account, phone='WEB-' + account, email=email,
                    full_name=name.strip(), role='admin', email_verified=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        wallet_for(user.id)
        db.session.commit()
        click.echo('Administrator created. Sign in and verify your phone through Phone & USSD.')
